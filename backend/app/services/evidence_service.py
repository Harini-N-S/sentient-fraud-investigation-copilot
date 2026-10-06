"""
Evidence Service
-----------------------------------------------------------------------------
Constructs the 3-tier forensic evidence packet preserving strict ground truth.
Tier 1: EXACT DATA
Tier 2: CALCULATED
Tier 3: RETRIEVED EVIDENCE
Tier 4: AI REASONING is explicitly None.
"""

from typing import Dict, Any, Optional
from backend.app.config import settings
from rules.engine import FraudIntelligenceEngine
from rules.evidence import EvidencePacket


class EvidenceService:
    """Provides access to structured 3-tier forensic evidence packets."""

    def __init__(self):
        self.engine = FraudIntelligenceEngine(db_path=str(settings.database_path))

    def get_evidence_packet(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves or generates a forensic evidence packet for the given transaction.
        """
        packet: Optional[EvidencePacket] = self.engine.get_evidence_packet(transaction_id)
        if not packet:
            return None

        # Return dict conforming to 3-tier taxonomy
        data = packet.to_dict()
        # Guarantee tier_4_ai_reasoning is None
        data["tier_4_ai_reasoning"] = None
        return data


evidence_service = EvidenceService()
