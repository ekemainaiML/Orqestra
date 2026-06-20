import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.deliberation.state_machine import StateMachineError

logger = logging.getLogger("orqestra")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except StateMachineError as e:
            logger.warning("State machine error: %s", str(e))
            return JSONResponse(
                status_code=400,
                content={
                    "error": "state_machine_error",
                    "detail": str(e),
                    "code": "INVALID_TRANSITION",
                },
            )
        except ValueError as e:
            logger.warning("Validation error: %s", str(e))
            return JSONResponse(
                status_code=422,
                content={
                    "error": "validation_error",
                    "detail": str(e),
                    "code": "INVALID_INPUT",
                },
            )
        except Exception as e:
            logger.exception("Unhandled error: %s", str(e))
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_error",
                    "detail": "An unexpected error occurred" if "production" else str(e),
                    "code": "INTERNAL_ERROR",
                    "traceback": traceback.format_exc() if __debug__ else None,
                },
            )
