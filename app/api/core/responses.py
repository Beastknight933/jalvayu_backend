from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

T = TypeVar("T")

def utcnow():
    return datetime.now(timezone.utc)

class APIResponse(BaseModel, Generic[T]):
    """
    Standard successful API response wrapper.
    """
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    metadata: Optional[dict] = None
    timestamp: datetime = Field(default_factory=utcnow)
    request_id: Optional[str] = None

class PaginatedData(BaseModel, Generic[T]):
    """
    Data wrapper for paginated endpoints.
    """
    items: List[T]
    total: int
    skip: int
    limit: int
    
    @property
    def page(self) -> int:
        return (self.skip // self.limit) + 1 if self.limit > 0 else 1
        
    @property
    def pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 1
        
    @property
    def has_next(self) -> bool:
        return self.skip + self.limit < self.total
        
    @property
    def has_previous(self) -> bool:
        return self.skip > 0

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
    timestamp: datetime = Field(default_factory=utcnow)
    request_id: Optional[str] = None
