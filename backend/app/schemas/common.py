"""
Common API Schemas
-----------------------------------------------------------------------------
Pagination, standard responses, and error models.
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMetadata(BaseModel):
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total items matching filter")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_prev: bool = Field(..., description="Whether a previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="List of items for current page")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error explanation")
    error_code: Optional[str] = Field(None, description="System error code")
    timestamp: str = Field(..., description="ISO 8601 timestamp of error occurrence")
