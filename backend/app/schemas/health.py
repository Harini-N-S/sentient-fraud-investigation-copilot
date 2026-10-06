"""
Health Endpoint Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall service status (ok/degraded/error)")
    database: str = Field(..., description="Database connectivity status (connected/disconnected)")
    environment: str = Field(..., description="Current environment (development/staging/production)")
    version: str = Field(..., description="API semantic version")
    table_count: Optional[int] = Field(None, description="Number of database tables found")
    timestamp: str = Field(..., description="Current server time (UTC ISO 8601)")
