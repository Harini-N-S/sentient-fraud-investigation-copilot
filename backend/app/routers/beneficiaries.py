"""
Beneficiaries Router
-----------------------------------------------------------------------------
Endpoints for querying beneficiary entities, mule accounts, and payment destinations.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.dependencies.deps import get_pagination_params
from backend.app.repositories.beneficiary_repo import BeneficiaryRepository
from backend.app.schemas.beneficiary import BeneficiarySummary, BeneficiaryDetail
from backend.app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/beneficiaries", tags=["Beneficiaries"])


@router.get("", response_model=PaginatedResponse[BeneficiarySummary], summary="List & Filter Beneficiaries")
def list_beneficiaries(
    beneficiary_type: Optional[str] = Query(None, description="Individual_Peer, Merchant_Store, Corporate_Vendor, Mobile_Money_Agent"),
    is_known_mule: Optional[int] = Query(None, description="1 if confirmed mule recipient, 0 otherwise"),
    institution_name: Optional[str] = Query(None, description="Filter by banking institution or telco"),
    search: Optional[str] = Query(None, description="Search by ID, name, institution, or phone/account"),
    sort_by: str = Query("created_at", description="Sort field: created_at, beneficiary_name, total_volume_usd, customer_count"),
    sort_order: str = Query("DESC", description="Sort direction: ASC or DESC"),
    pagination: dict = Depends(get_pagination_params),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves paginated beneficiaries with filtering by mule status, institution, and type.
    """
    items, meta = BeneficiaryRepository.get_beneficiaries(
        db=db,
        page=pagination["page"],
        page_size=pagination["page_size"],
        beneficiary_type=beneficiary_type,
        is_known_mule=is_known_mule,
        institution_name=institution_name,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse(
        items=[BeneficiarySummary(**item) for item in items],
        pagination=meta
    )


@router.get("/{beneficiary_id}", response_model=BeneficiaryDetail, summary="Get Beneficiary Forensic Detail")
def get_beneficiary_detail(
    beneficiary_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves beneficiary profile, interacting customers, total inbound volume,
    recent transaction audit trail, and linked alerts/signals.
    Essential for mule ring and nexus investigations.
    """
    detail = BeneficiaryRepository.get_beneficiary_detail(db, beneficiary_id.strip())
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beneficiary with ID '{beneficiary_id}' was not found in the database."
        )

    return BeneficiaryDetail(**detail)
