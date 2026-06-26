from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.handlers import add_exception_handlers
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application.
    Runs on startup and shutdown.
    """
    # Setup logging on startup
    setup_logging(environment=settings.ENVIRONMENT)
    
    # Start Prometheus internal metrics server on port 9090
    from prometheus_client import start_http_server
    try:
        start_http_server(9090)
        from loguru import logger
        logger.info("Started internal Prometheus metrics server on port 9090")
    except Exception as e:
        from loguru import logger
        logger.error(f"Failed to start Prometheus metrics server: {e}")
        
    yield
    # Cleanup on shutdown can be added here (e.g., closing Redis connections, DB engines)


def create_app() -> FastAPI:
    """
    FastAPI application factory.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Add standard middlewares (Order matters!)
    from starlette.middleware.gzip import GZipMiddleware
    from app.api.middlewares.request_id import RequestIDMiddleware
    from app.api.middlewares.logging import APILoggingMiddleware
    from app.api.middlewares.rate_limit import limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(APILoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup slowapi rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Add global exception handlers
    add_exception_handlers(app)

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
