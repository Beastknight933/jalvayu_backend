from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BaseAppException


def add_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for the FastAPI application.
    """
    
    @app.exception_handler(BaseAppException)
    async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        logger.warning(f"Application exception: {exc.message} on path {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "details": exc.payload},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Validation error on path {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"message": "Validation Error", "details": exc.errors()},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(f"Database error on path {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error. Database operation failed."},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception on path {request.url.path}: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error."},
        )
