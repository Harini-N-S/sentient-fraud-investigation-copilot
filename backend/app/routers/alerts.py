"""
Alerts Router
-----------------------------------------------------------------------------
Endpoints for querying, filtering, and deep-diving into fraud alerts.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.dependencies.deps import get_pagination_params
from backend.app.repositories.alert_repo import AlertRepository
from backend.app.schemas.alert import AlertSummary, AlertDetail
from backend.app.schemas.common import PaginatedResponse
from backend.app.retrieval.models import StandardEvidencePacket

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse[AlertSummary], summary="List & Filter Fraud Alerts")
def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: NEW_UNASSIGNED, UNDER_INVESTIGATION, etc."),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID (e.g. CUS-00014)"),
    transaction_id: Optional[str] = Query(None, description="Filter by transaction ID (e.g. TXN-00801)"),
    rule_category: Optional[str] = Query(None, description="Filter by fraud rule category"),
    rule_code: Optional[str] = Query(None, description="Filter by rule code (e.g. R-ATO-05)"),
    date_from: Optional[str] = Query(None, description="Start date ISO 8601 (inclusive)"),
    date_to: Optional[str] = Query(None, description="End date ISO 8601 (inclusive)"),
    sort_by: str = Query("created_at", description="Sort field: created_at, risk_score, severity, customer_id"),
    sort_order: str = Query("DESC", description="Sort direction: ASC or DESC"),
    pagination: dict = Depends(get_pagination_params),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves paginated fraud alerts with multi-dimensional filtering.
    Supports Command Centre triaging by severity, risk score, rule type, and customer.
    """
    valid_severities = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    if severity and severity.upper() not in valid_severities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid severity '{severity}'. Must be one of: {sorted(list(valid_severities))}"
        )

    items, meta = AlertRepository.get_alerts(
        db=db,
        page=pagination["page"],
        page_size=pagination["page_size"],
        severity=severity,
        status=status_filter,
        customer_id=customer_id,
        transaction_id=transaction_id,
        rule_category=rule_category,
        rule_code=rule_code,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse(
        items=[AlertSummary(**item) for item in items],
        pagination=meta
    )


@router.get("/{alert_id}", response_model=AlertDetail, summary="Get Fraud Alert Dossier")
def get_alert_detail(
    alert_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves full forensic details for a specific alert, including triggering transaction,
    customer profile, debited account, fired fraud signals, and related entity references.
    """
    alert_dossier = AlertRepository.get_alert_by_id(db, alert_id.strip())
    if not alert_dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found in the database."
        )

    return AlertDetail(**alert_dossier)


@router.get("/{alert_id}/evidence", response_model=StandardEvidencePacket, summary="Get Grounded Alert Evidence Packet")
def get_alert_evidence(
    alert_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Constructs the standardized forensic evidence packet for a specific fraud alert.
    Surfaces triggering transaction, customer context, fired fraud signals,
    and counter-evidence (for false-positive / legitimate anomaly alerts).
    """
    alert_dossier = AlertRepository.get_alert_by_id(db, alert_id.strip())
    if not alert_dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' was not found in the database; cannot assemble evidence packet."
        )

    from backend.app.retrieval import evidence_builder
    packet = evidence_builder.build_for_entity("alert", alert_id.strip())
    return packet

