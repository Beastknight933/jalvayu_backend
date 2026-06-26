from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """
    Standard successful API response wrapper.
    """
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    metadata: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None

class PaginatedData(BaseModel, Generic[T]):
    """
    Data wrapper for paginated endpoints.
    """
    items: List[T]
    total: int
    skip: int
    limit: int

class APIPaginatedResponse(APIResponse[PaginatedData[T]], Generic[T]):
    """
    Standard paginated API response wrapper.
    """
    pass

class APIErrorResponse(BaseModel):
    """
    Standard error response wrapper.
    """
    success: bool = False
    message: str
    errors: Optional[List[dict]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
