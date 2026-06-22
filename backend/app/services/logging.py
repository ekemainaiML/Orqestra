import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.monotonic()

        logger = logging.getLogger("orqestra.access")
        logger.info(
            "request_id=%s method=%s path=%s query_params=%s",
            request_id, request.method, request.url.path, dict(request.query_params),
        )

        try:
            response = await call_next(request)
            duration_ms = (time.monotonic() - start) * 1000
            logger.info(
                "request_id=%s method=%s path=%s status=%d duration_ms=%.0f",
                request_id, request.method, request.url.path, response.status_code, duration_ms,
            )
            _record_metrics(response.status_code, duration_ms)
        except Exception:
            duration_ms = (time.monotonic() - start) * 1000
            logger.exception("request_id=%s method=%s path=%s duration_ms=%.0f", request_id, request.method, request.url.path, duration_ms)
            _record_metrics(500, duration_ms, error_type="unhandled")
            raise

        response.headers["X-Request-ID"] = request_id
        return response


def _record_metrics(status_code: int, duration_ms: float, error_type: str | None = None):
    try:
        from app.services.metrics import metrics
        metrics.record_request(status_code, duration_ms, error_type)
    except ImportError:
        pass


def setup_logging(environment: str = "development") -> None:
    level = logging.DEBUG if environment == "development" else logging.INFO

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger("orqestra")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    access_logger = logging.getLogger("orqestra.access")
    access_logger.setLevel(level)
    access_logger.addHandler(handler)

    if environment == "production":
        import json as _json

        class JSONFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_entry = {
                    "timestamp": self.formatTime(record),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if hasattr(record, "exc_info") and record.exc_info:
                    log_entry["traceback"] = self.formatException(record.exc_info)
                return _json.dumps(log_entry)

        json_handler = logging.StreamHandler(sys.stdout)
        json_handler.setFormatter(JSONFormatter())
        root_logger.handlers.clear()
        root_logger.addHandler(json_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
