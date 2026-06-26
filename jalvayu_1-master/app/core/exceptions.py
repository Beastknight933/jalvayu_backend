from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base Exception for the Application"""
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class BadRequestException(BaseAppException):
    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)


class UnauthorizedException(BaseAppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(BaseAppException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class ConflictException(BaseAppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409)


class UnprocessableEntityException(BaseAppException):
    def __init__(self, message: str = "Unprocessable Entity", payload: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, payload=payload)
