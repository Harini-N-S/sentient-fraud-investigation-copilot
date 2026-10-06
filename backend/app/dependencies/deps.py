"""
FastAPI Dependencies
-----------------------------------------------------------------------------
Dependency injection providers for database sessions, pagination validation, and repositories.
"""

from typing import Generator
import sqlite3
from fastapi import Query
from backend.app.database import get_db
from backend.app.config import settings


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description=f"Items per page (max {settings.max_page_size})"
    )
):
    """Reusable pagination query parameters."""
    return {"page": page, "page_size": page_size}
