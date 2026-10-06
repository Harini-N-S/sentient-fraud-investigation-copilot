"""
Customers Router
-----------------------------------------------------------------------------
Endpoints for customer search, profiling, and 360-degree forensic dossiers.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.dependencies.deps import get_pagination_params
from backend.app.repositories.customer_repo import CustomerRepository
from backend.app.schemas.customer import CustomerSummary, CustomerDossier
from backend.app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/customers", tags=["Customers"])


SEGMENT_MAPPING = {
    "RETAIL": "Retail",
    "RETAIL INDIVIDUAL": "Retail",
    "RETAIL_INDIVIDUAL": "Retail",
    "SME": "SME",
    "SME COMMERCIAL": "SME",
    "SME_COMMERCIAL": "SME",
    "CORPORATE": "Corporate",
    "LARGE CORPORATE": "Corporate",
    "LARGE_CORPORATE": "Corporate",
    "VIP": "HNWI",
    "HNWI": "HNWI",
    "PRIVATE BANKING VIP": "HNWI",
    "PRIVATE_BANKING_VIP": "HNWI",
    "AGENCY_BANKING": "AgencyBankingOperator",
    "AGENCY BANKING": "AgencyBankingOperator",
    "AGENCYBANKINGOPERATOR": "AgencyBankingOperator",
    "AGENCY_BANKING_OPERATOR": "AgencyBankingOperator",
    "AGENCY BANKING OPERATOR": "AgencyBankingOperator",
}

KYC_MAPPING = {
    "FULL": "Tier_3_Full",
    "FULL VERIFICATION": "Tier_3_Full",
    "FULL_VERIFICATION": "Tier_3_Full",
    "TIER_3_FULL": "Tier_3_Full",
    "TIER_3": "Tier_3_Full",
    "PARTIAL": "Tier_2_Standard",
    "PARTIAL VERIFICATION": "Tier_2_Standard",
    "PARTIAL_VERIFICATION": "Tier_2_Standard",
    "STANDARD": "Tier_2_Standard",
    "TIER_2_STANDARD": "Tier_2_Standard",
    "TIER_2": "Tier_2_Standard",
    "PENDING": "Tier_1_Basic",
    "PENDING VERIFICATION": "Tier_1_Basic",
    "PENDING_VERIFICATION": "Tier_1_Basic",
    "BASIC": "Tier_1_Basic",
    "TIER_1_BASIC": "Tier_1_Basic",
    "TIER_1": "Tier_1_Basic",
}

RISK_MAPPING = {
    "HIGH": "High",
    "HIGH RISK TIER": "High",
    "HIGH_RISK_TIER": "High",
    "MEDIUM": "Medium",
    "MEDIUM RISK TIER": "Medium",
    "MEDIUM_RISK_TIER": "Medium",
    "LOW": "Low",
    "LOW RISK TIER": "Low",
    "LOW_RISK_TIER": "Low",
}


def resolve_segment(seg: Optional[str]) -> Optional[str]:
    if not seg:
        return None
    cleaned = seg.strip()
    upper = cleaned.upper().replace("-", "_")
    if upper in {"ALL", "ALL SEGMENTS", "ALL_SEGMENTS", ""}:
        return None
    return SEGMENT_MAPPING.get(upper, cleaned)


def resolve_kyc(k: Optional[str]) -> Optional[str]:
    if not k:
        return None
    cleaned = k.strip()
    upper = cleaned.upper().replace("-", "_")
    if upper in {"ALL", "ALL KYC STATUSES", "ALL_KYC_STATUSES", "ALL_KYC", ""}:
        return None
    return KYC_MAPPING.get(upper, cleaned)


def resolve_risk(r: Optional[str]) -> Optional[str]:
    if not r:
        return None
    cleaned = r.strip()
    upper = cleaned.upper().replace("-", "_")
    if upper in {"ALL", "ALL RISK TIERS", "ALL_RISK_TIERS", "ALL_RISK", ""}:
        return None
    return RISK_MAPPING.get(upper, cleaned.capitalize())


def resolve_city(c: Optional[str]) -> Optional[str]:
    if not c:
        return None
    cleaned = c.strip()
    upper = cleaned.upper().replace("-", "_")
    if upper in {"ALL", "ALL CITIES", "ALL_CITIES", ""}:
        return None
    return cleaned


@router.get("", response_model=PaginatedResponse[CustomerSummary], summary="List & Search Customers")
def list_customers(
    search: Optional[str] = Query(None, description="Search by ID, name, email, or phone"),
    segment: Optional[str] = Query(None, description="Retail, SME, Corporate, HNWI, AgencyBankingOperator"),
    kyc_status: Optional[str] = Query(None, description="Tier_1_Basic, Tier_2_Standard, Tier_3_Full"),
    risk_category: Optional[str] = Query(None, description="Low, Medium, High"),
    registered_city: Optional[str] = Query(None, description="Kinshasa, Lubumbashi, Kolwezi, Goma, Matadi, Bukavu"),
    city: Optional[str] = Query(None, description="Alias for registered_city"),
    sort_by: str = Query("created_at", description="Sort field: created_at, full_name, customer_id, risk_category"),
    sort_order: str = Query("DESC", description="Sort direction: ASC or DESC"),
    pagination: dict = Depends(get_pagination_params),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves paginated customers with multi-attribute filtering.
    """
    if registered_city and registered_city.strip():
        effective_city = registered_city.strip()
    elif city and city.strip():
        effective_city = city.strip()
    else:
        effective_city = None

    db_segment = resolve_segment(segment)
    db_kyc = resolve_kyc(kyc_status)
    db_risk = resolve_risk(risk_category)
    db_city = resolve_city(effective_city)

    items, meta = CustomerRepository.get_customers(
        db=db,
        page=pagination["page"],
        page_size=pagination["page_size"],
        search=search,
        segment=db_segment,
        kyc_status=db_kyc,
        risk_category=db_risk,
        registered_city=db_city,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse(
        items=[CustomerSummary(**item) for item in items],
        pagination=meta
    )


@router.get("/{customer_id}", response_model=CustomerDossier, summary="Get Full Customer 360 Dossier")
def get_customer_dossier(
    customer_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves 360-degree forensic customer dossier:
    - Customer identity & KYC profile
    - Linked accounts with balances
    - Lifetime transaction summary & recent activity
    - Behavioural baseline profile
    - Known devices & recent authentication events
    - Beneficiary interactions
    - Risk analysis (alerts, signals, peak score)
    - Relationship graph (shared devices and shared beneficiaries)
    """
    dossier = CustomerRepository.get_customer_dossier(db, customer_id.strip())
    if not dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID '{customer_id}' was not found in the database."
        )

    return CustomerDossier(**dossier)
