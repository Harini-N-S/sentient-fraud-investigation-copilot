"""
Transactions Router
-----------------------------------------------------------------------------
Endpoints for querying, filtering, and investigating financial transactions and evidence packets.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.dependencies.deps import get_pagination_params
from backend.app.repositories.transaction_repo import TransactionRepository
from backend.app.services.evaluation_service import evaluation_service
from backend.app.services.evidence_service import evidence_service
from backend.app.schemas.transaction import TransactionSummary, TransactionDetail
from backend.app.schemas.evidence import EvidenceResponse
from backend.app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


CHANNEL_MAPPING = {
    "MOBILE_APP": "IllicoCash_App",
    "MOBILE BANKING APP": "IllicoCash_App",
    "ONLINE_BANKING": "RawbankOnline_Web",
    "ONLINE BANKING": "RawbankOnline_Web",
    "WEB PORTAL": "RawbankOnline_Web",
    "WEB_PORTAL": "RawbankOnline_Web",
    "AGENCY_BANKING": "Agency_Express_POS",
    "AGENCY BANKING": "Agency_Express_POS",
    "ATM": "ATM_Cardless",
    "ATM TERMINAL": "ATM_Cardless",
    "ATM_TERMINAL": "ATM_Cardless",
    "ATM / CARDLESS": "ATM_Cardless",
    "ATM_CARDLESS": "ATM_Cardless",
    "ILLICOCASH_APP": "IllicoCash_App",
    "ILLICOCASH": "IllicoCash_App",
    "RAWBANKONLINE_WEB": "RawbankOnline_Web",
    "RAWBANKONLINE": "RawbankOnline_Web",
    "AGENCY_EXPRESS_POS": "Agency_Express_POS",
}


def resolve_channel(ch: Optional[str]) -> Optional[str]:
    if not ch:
        return None
    cleaned = ch.strip()
    upper = cleaned.upper().replace("-", "_")
    if upper in {"ALL", "ALL CHANNELS", "ALL_CHANNELS", ""}:
        return None
    return CHANNEL_MAPPING.get(upper, cleaned)


@router.get("", response_model=PaginatedResponse[TransactionSummary], summary="List & Filter Transactions")
def list_transactions(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    beneficiary_id: Optional[str] = Query(None, description="Filter by destination beneficiary ID"),
    device_id: Optional[str] = Query(None, description="Filter by originating device ID"),
    channel: Optional[str] = Query(None, description="Filter by channel: IllicoCash_App, RawbankOnline_Web, etc."),
    transaction_type: Optional[str] = Query(None, description="Filter by type: P2P_Transfer, Merchant_Payment, etc."),
    currency: Optional[str] = Query(None, description="Filter by currency: CDF or USD"),
    location_city: Optional[str] = Query(None, description="Filter by location city (e.g. Kinshasa, Lubumbashi)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: Completed, Pending_Review, Blocked_Declined"),
    min_amount_usd: Optional[float] = Query(None, ge=0.0, description="Minimum amount in USD equivalent"),
    max_amount_usd: Optional[float] = Query(None, ge=0.0, description="Maximum amount in USD equivalent"),
    date_from: Optional[str] = Query(None, description="Start date ISO 8601 (inclusive)"),
    date_to: Optional[str] = Query(None, description="End date ISO 8601 (inclusive)"),
    sort_by: str = Query("timestamp", description="Sort field: timestamp, amount_usd, amount, transaction_id"),
    sort_order: str = Query("DESC", description="Sort direction: ASC or DESC"),
    pagination: dict = Depends(get_pagination_params),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves paginated transactions with multi-field filtering.
    """
    normalized_currency: Optional[str] = None
    if currency:
        c_upper = currency.upper().strip()
        if c_upper in {"CDF & USD", "CDF/USD", "CDF,USD", "ALL", "BOTH", ""}:
            normalized_currency = None
        elif c_upper in {"CDF", "USD"}:
            normalized_currency = c_upper
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency '{currency}'. Must be 'CDF' or 'USD'."
            )

    db_channel = resolve_channel(channel)

    items, meta = TransactionRepository.get_transactions(
        db=db,
        page=pagination["page"],
        page_size=pagination["page_size"],
        customer_id=customer_id,
        account_id=account_id,
        beneficiary_id=beneficiary_id,
        device_id=device_id,
        channel=db_channel,
        transaction_type=transaction_type,
        currency=normalized_currency,
        location_city=location_city,
        status=status_filter,
        min_amount_usd=min_amount_usd,
        max_amount_usd=max_amount_usd,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse(
        items=[TransactionSummary(**item) for item in items],
        pagination=meta
    )


@router.get("/{transaction_id}", response_model=TransactionDetail, summary="Get Transaction Forensic Dossier")
def get_transaction_detail(
    transaction_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves full transaction dossier including customer, account, beneficiary, device,
    prior authentication logs, historical database signals, fresh deterministic rule evaluation,
    and 3-tier forensic evidence packet.
    """
    tx_dossier = TransactionRepository.get_transaction_by_id(db, transaction_id.strip())
    if not tx_dossier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found in the database."
        )

    # Attach fresh deterministic evaluation and evidence packet
    eval_result = evaluation_service.evaluate_transaction(transaction_id.strip())
    evidence_pkt = evidence_service.get_evidence_packet(transaction_id.strip())

    tx_dossier["deterministic_evaluation"] = eval_result
    tx_dossier["evidence_packet"] = evidence_pkt

    return TransactionDetail(**tx_dossier)


@router.get("/{transaction_id}/evidence", response_model=EvidenceResponse, summary="Get 3-Tier Forensic Evidence Packet")
def get_transaction_evidence(transaction_id: str):
    """
    Returns the grounded 3-tier forensic evidence packet:
      Tier 1: EXACT DATA (Raw, immutable database records)
      Tier 2: CALCULATED (Deterministic mathematical indicators & scores)
      Tier 3: RETRIEVED EVIDENCE (Related graph nodes, history, baselines, logs)
      Tier 4: AI REASONING (Explicitly None in Phase 4)
    """
    packet = evidence_service.get_evidence_packet(transaction_id.strip())
    if not packet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' not found; cannot assemble evidence packet."
        )

    return EvidenceResponse(**packet)
