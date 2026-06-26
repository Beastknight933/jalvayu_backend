import time
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class APILoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all API requests with their execution time, status codes, and correlation ID.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = getattr(request.state, "request_id", "unknown")
        
        start_time = time.time()
        logger.info(f"Req [{request_id}] | {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Res [{request_id}] | {response.status_code} | {process_time:.3f}s")
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Err [{request_id}] | {request.method} {request.url.path} | {process_time:.3f}s | {e}")
            raise
