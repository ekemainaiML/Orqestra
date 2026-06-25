import hashlib
import hmac
import os
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import UserModel
from app.services.database import get_session
from app.services.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

TOKEN_EXPIRY_S = 86400 * 7  # 7 days


def _hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    pwd = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return f"{salt}:{pwd}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, pwd_hash = stored.split(":", 1)
        computed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
        return hmac.compare_digest(computed, pwd_hash)
    except (ValueError, IndexError):
        return False


def _make_token(username: str, tenant_id: str | None = None) -> str:
    payload = f"{username}:{tenant_id or ''}:{int(time.time()) + TOKEN_EXPIRY_S}"
    sig = hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_token(token: str) -> tuple[str, str] | None:
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        username, tenant_id_str, expiry_str, sig = parts
        expiry = int(expiry_str)
        if time.time() > expiry:
            return None
        expected = hmac.new(
            settings.jwt_secret.encode(),
            f"{username}:{tenant_id_str}:{expiry}".encode(),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return username, tenant_id_str
    except (ValueError, IndexError):
        return None


class SignupRequest(BaseModel):
    username: str
    password: str
    tenant_slug: str | None = None


class SignupResponse(BaseModel):
    message: str
    username: str
    tenant_id: str | None = None
    tenant_slug: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    tenant_id: str | None = None
    message: str


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: str | None = None


@router.post("/signup", response_model=SignupResponse)
async def signup(req: SignupRequest, session: AsyncSession = Depends(get_session)):
    username = req.username.strip()
    if len(username) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    existing = await session.scalar(select(UserModel).where(UserModel.username == username))
    if existing:
        raise HTTPException(status_code=409, detail="Username already taken")

    tenant_id: uuid.UUID | None = None
    tenant_slug: str | None = None
    if req.tenant_slug:
        tenant = await session.scalar(
            select(Tenant).where(Tenant.slug == req.tenant_slug)
        )
        if tenant:
            tenant_id = tenant.id
            tenant_slug = tenant.slug

    user = UserModel(
        username=username,
        password_hash=_hash_password(req.password),
        tenant_id=tenant_id,
    )
    session.add(user)
    await session.commit()
    return SignupResponse(
        message="User created successfully",
        username=username,
        tenant_id=str(tenant_id) if tenant_id else None,
        tenant_slug=tenant_slug,
    )


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(UserModel).where(UserModel.username == req.username))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tenant_id_str = str(user.tenant_id) if user.tenant_id else ""
    token = _make_token(req.username, tenant_id_str)
    return LoginResponse(
        token=token,
        username=req.username,
        tenant_id=tenant_id_str or None,
        message="Login successful",
    )


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(req: CreateTenantRequest, session: AsyncSession = Depends(get_session)):
    slug = req.slug.strip().lower().replace(" ", "-")
    existing = await session.scalar(select(Tenant).where(Tenant.slug == slug))
    if existing:
        raise HTTPException(status_code=409, detail="Tenant slug already exists")
    tenant = Tenant(name=req.name.strip(), slug=slug)
    session.add(tenant)
    await session.commit()
    return TenantResponse(
        id=str(tenant.id),
        name=tenant.name,
        slug=tenant.slug,
        created_at=tenant.created_at.isoformat() if tenant.created_at else None,
    )


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()
    return [
    TenantResponse(
        id=str(t.id),
        name=t.name,
        slug=t.slug,
        created_at=t.created_at.isoformat() if t.created_at else None,
    )
    for t in tenants
]


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: str, req: CreateTenantRequest, session: AsyncSession = Depends(get_session)):
    try:
        uid = uuid.UUID(tenant_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid tenant ID")
    tenant = await session.get(Tenant, uid)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    slug = req.slug.strip().lower().replace(" ", "-")
    if slug != tenant.slug:
        existing = await session.scalar(select(Tenant).where(Tenant.slug == slug).where(Tenant.id != uid))
        if existing:
            raise HTTPException(status_code=409, detail="Tenant slug already exists")
    tenant.name = req.name.strip()
    tenant.slug = slug
    await session.commit()
    await session.refresh(tenant)
    return TenantResponse(
        id=str(tenant.id), name=tenant.name, slug=tenant.slug,
        created_at=tenant.created_at.isoformat() if tenant.created_at else None,
    )


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, session: AsyncSession = Depends(get_session)):
    try:
        uid = uuid.UUID(tenant_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid tenant ID")
    tenant = await session.get(Tenant, uid)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if tenant.slug == "default":
        raise HTTPException(status_code=400, detail="Cannot delete the default tenant")
    await session.delete(tenant)
    await session.commit()
    return {"message": "Tenant deleted", "id": tenant_id}


class NotificationSettings(BaseModel):
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@orqestra.ai"
    slack_webhook_url: str = ""


@router.get("/settings/notifications")
async def get_notification_settings():
    return NotificationSettings(
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        smtp_username=settings.smtp_username,
        smtp_password="********" if settings.smtp_password else "",
        smtp_from=settings.smtp_from,
        slack_webhook_url="********" if settings.slack_webhook_url else "",
    )


@router.put("/settings/notifications")
async def update_notification_settings(req: NotificationSettings):
    settings.smtp_host = req.smtp_host
    settings.smtp_port = req.smtp_port
    settings.smtp_username = req.smtp_username
    if req.smtp_password and req.smtp_password != "********":
        settings.smtp_password = req.smtp_password
    settings.smtp_from = req.smtp_from
    if req.slack_webhook_url and req.slack_webhook_url != "********":
        settings.slack_webhook_url = req.slack_webhook_url
    import app.services.notifications as nmod
    nmod._global_notifier = None
    return {"message": "Notification settings updated"}
