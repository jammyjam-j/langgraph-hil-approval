from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
import json
from typing import Awaitable

logger = logging.getLogger("app")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8") if body_bytes else ""
            client_host = request.client.host if request.client else "unknown"
            method = request.method
            url_path = request.url.path
            logger.info(
                f"Incoming request: {method} {url_path} from {client_host} with body {body_str}"
            )
            response: Response = await call_next(request)
        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
            error_message = str(exc)
            logger.error(
                f"Error processing request: {method} {url_path} after {elapsed_ms}ms: {error_message}"
            )
            raise
        finally:
            elapsed_ms = int((time.time() - start_time) * 1000)
            status_code = response.status_code if isinstance(response, Response) else "unknown"
            logger.info(
                f"Completed request: {method} {url_path} with status {status_code} in {elapsed_ms}ms"
            )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.exception("Unhandled exception")
            content = {"detail": "Internal Server Error"}
            return Response(
                content=json.dumps(content),
                status_code=500,
                media_type="application/json",
            )