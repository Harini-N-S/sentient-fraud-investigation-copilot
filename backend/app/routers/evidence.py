"""
Evidence Router
-----------------------------------------------------------------------------
Dedicated endpoint for retrieving 3-tier grounded forensic evidence packets.
Tier 1: EXACT DATA
Tier 2: CALCULATED
Tier 3: RETRIEVED EVIDENCE
Tier 4: AI REASONING is explicitly None / deferred until future phases.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.services.evidence_service import evidence_service
from backend.app.schemas.evidence import EvidenceResponse

router = APIRouter(prefix="/api/evidence", tags=["Forensic Evidence"])


@router.get(
    "/{transaction_id}",
    response_model=EvidenceResponse,
    summary="Get 3-Tier Grounded Forensic Evidence Packet"
)
def get_evidence(transaction_id: str):
    """
    Constructs the 3-Tier Evidence Packet anchored strictly in verified database ground truth:
    - Tier 1: EXACT DATA (Raw, immutable database records)
    - Tier 2: CALCULATED (Deterministic mathematical indicators & scores)
    - Tier 3: RETRIEVED EVIDENCE (Related graph nodes, history, baselines, logs)
    - Tier 4: AI REASONING (Explicitly None in Phase 4)
    """
    packet = evidence_service.get_evidence_packet(transaction_id.strip())
    if not packet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found; cannot assemble evidence packet."
        )

    return EvidenceResponse(**packet)
