import uuid

from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.auth.router import verify_token
from app.models.tenant import Tenant
from app.services.database import get_async_session
from app.services.settings import settings
from app.services.tenant_context import set_current_tenant_id

PUBLIC_PATHS = {
    "/health",
    "/auth/login",
    "/auth/signup",
    "/auth/tenants",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id: uuid.UUID | None = None

        if settings.auth_enabled:
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                result = verify_token(auth[7:])
                if result:
                    username, tenant_id_str = result[0], result[1]
                    request.state.username = username
                    try:
                        tenant_id = uuid.UUID(tenant_id_str) if tenant_id_str else None
                    except (ValueError, AttributeError):
                        tenant_id = None
        else:
            tenant_id_str = request.headers.get("X-Tenant-ID", "")
            tenant_slug = request.headers.get("X-Tenant-Slug", "")
            if not tenant_id_str and tenant_slug:
                async with get_async_session()() as session:
                    result = await session.scalar(
                        select(Tenant).where(Tenant.slug == tenant_slug)
                    )
                    if result:
                        tenant_id = result.id
            elif tenant_id_str:
                try:
                    tenant_id = uuid.UUID(tenant_id_str)
                except (ValueError, AttributeError):
                    tenant_id = None

        set_current_tenant_id(tenant_id)

        try:
            return await call_next(request)
        finally:
            set_current_tenant_id(None)
