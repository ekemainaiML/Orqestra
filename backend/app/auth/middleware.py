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
        username = verify_token(token)
        if username is None:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        request.state.username = username
        return await call_next(request)
