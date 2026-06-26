import logging
import sys

from loguru import logger
from typing import cast
from types import FrameType


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and route them to Loguru.
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(environment: str = "development") -> None:
    """
    Setup centralized Loguru logging.
    """
    # Remove standard Loguru handlers
    logger.remove()

    # Define log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Add console handler
    logger.add(sys.stdout, format=log_format, level="DEBUG" if environment == "development" else "INFO")

    # Add file handlers for persistency
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="10 days",
        format=log_format,
        level="INFO"
    )
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        format=log_format,
        level="ERROR"
    )

    # Intercept standard library logging (e.g., Uvicorn, FastAPI, SQLAlchemy)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Configure specific loggers to use Loguru
    for _log in ["uvicorn", "uvicorn.error", "fastapi", "sqlalchemy.engine", "celery"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False
