"""
Health Router
-----------------------------------------------------------------------------
GET /api/health - Verifies API readiness and active SQLite database connectivity.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.database import check_db_connectivity
from backend.app.schemas.health import HealthResponse

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="System Health & Database Connectivity")
def get_health():
    """
    Verifies API liveness and active database connectivity.
    Does not hard-code status; actively executes a verification query against SQLite.
    """
    db_check = check_db_connectivity()
    db_status = db_check["status"]
    is_ok = db_status == "connected"

    return HealthResponse(
        status="ok" if is_ok else "degraded",
        database=db_status,
        environment=settings.app_env,
        version=settings.app_version,
        table_count=db_check.get("table_count"),
        timestamp=datetime.now(timezone.utc).isoformat()
    )
