import hashlib
import hmac
import os
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


def _make_token(username: str) -> str:
    payload = f"{username}:{int(time.time()) + TOKEN_EXPIRY_S}"
    sig = hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def verify_token(token: str) -> str | None:
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        username, expiry_str, sig = parts
        expiry = int(expiry_str)
        if time.time() > expiry:
            return None
        expected = hmac.new(
            settings.jwt_secret.encode(), f"{username}:{expiry}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return username
    except (ValueError, IndexError):
        return None


class SignupRequest(BaseModel):
    username: str
    password: str


class SignupResponse(BaseModel):
    message: str
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    message: str


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

    user = UserModel(username=username, password_hash=_hash_password(req.password))
    session.add(user)
    await session.commit()
    return SignupResponse(message="User created successfully", username=username)


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(UserModel).where(UserModel.username == req.username))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _make_token(req.username)
    return LoginResponse(token=token, username=req.username, message="Login successful")
