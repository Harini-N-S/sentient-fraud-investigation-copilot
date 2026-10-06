"""
Forensic Evidence Packet Schemas
-----------------------------------------------------------------------------
Preserves the Phase 3 strict 3-tier taxonomy:
  Tier 1: EXACT DATA (Raw, immutable database records)
  Tier 2: CALCULATED (Deterministic mathematical indicators & scores)
  Tier 3: RETRIEVED EVIDENCE (Related graph nodes, history, baselines, logs)
  Tier 4: AI REASONING is explicitly None / deferred until future phases.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceResponse(BaseModel):
    transaction_id: str = Field(..., description="Target transaction ID")
    customer_id: str = Field(..., description="Target customer ID")
    generated_at: str = Field(..., description="Timestamp of evidence packet assembly")
    tier_1_exact_data: Dict[str, Any] = Field(..., description="Tier 1: Raw immutable database records")
    tier_2_calculated: Dict[str, Any] = Field(..., description="Tier 2: Deterministic mathematical indicators & scores")
    tier_3_retrieved_evidence: Dict[str, Any] = Field(..., description="Tier 3: Graph nodes, historical baseline, device history, auth logs")
    tier_4_ai_reasoning: Optional[Dict[str, Any]] = Field(
        None,
        description="Tier 4: Strictly None in Phase 4. Reserved for Phase 7 Groq AI layer."
    )
