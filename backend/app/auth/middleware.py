from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth.router import verify_token
from app.services.settings import settings

PUBLIC_PATHS = {
    "/health",
    "/auth/login",
    "/auth/signup",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.auth_enabled:
            return await call_next(request)

        path = request.url.path.rstrip("/") or "/"
        if path in PUBLIC_PATHS or path.startswith(("/docs/", "/openapi.json", "/redoc")):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header[7:]
        result = verify_token(token)
        if result is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        username, tenant_id_str = result
        request.state.username = username
        request.state.tenant_id = tenant_id_str
        return await call_next(request)
