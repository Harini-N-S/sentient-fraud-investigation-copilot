"""
Base Repository Utilities
-----------------------------------------------------------------------------
Helper functions for row dict transformation, safe pagination, and parameter sanitization.
Prevents SQL injection by enforcing strict column whitelisting on sorting and filtering.
"""

import sqlite3
from typing import Dict, Any, List, Tuple
from backend.app.schemas.common import PaginationMetadata


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row into a standard Python dict."""
    if row is None:
        return {}
    return {k: row[k] for k in row.keys()}


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convert list of sqlite3.Row objects to list of dicts."""
    return [row_to_dict(r) for r in rows]


def calculate_pagination(page: int, page_size: int, total: int) -> PaginationMetadata:
    """Calculate pagination metadata with page boundaries."""
    page = max(1, page)
    page_size = max(1, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size) if total > 0 else 1
    
    return PaginationMetadata(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )


def sanitize_sort(sort_by: str, allowed_columns: Dict[str, str], default_col: str = "created_at", default_order: str = "DESC") -> Tuple[str, str]:
    """
    Safely whitelist and map sort column and sort order.
    Returns (sql_column_expression, order_direction).
    """
    col = allowed_columns.get(sort_by.lower().strip() if sort_by else "", default_col)
    order = "ASC" if default_order.upper() == "ASC" else "DESC"
    return col, order
