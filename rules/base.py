"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules Base Framework
-----------------------------------------------------------------------------
All rule definitions, identifiers, thresholds, and weights are:
[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


@dataclass
class EvidenceItem:
    key: str
    value: Any
    description: str


@dataclass
class SignalResult:
    rule_code: str
    rule_name: str
    rule_category: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence_score: float  # 0.0 - 1.0
    weight: int  # Risk weight contribution (e.g. 10 to 35)
    description: str
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_code": self.rule_code,
            "rule_name": self.rule_name,
            "rule_category": self.rule_category,
            "severity": self.severity,
            "confidence_score": round(self.confidence_score, 2),
            "weight": self.weight,
            "description": self.description,
            "evidence_data": self.evidence_data,
            "timestamp": self.timestamp
        }


class BaseRule:
    """
    Abstract Base Class for Deterministic Fraud Rules.
    Each rule must:
      - Have stable ID and name.
      - Have deterministic inputs and pure mathematical/logical calculation.
      - Produce zero random or LLM-generated output.
      - Generate explicit structured evidence explaining why it triggered.
    """
    rule_code: str = "R-BASE-00"
    rule_name: str = "Base Rule"
    rule_category: str = "General"
    default_weight: int = 10
    default_severity: str = "LOW"

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        """
        Evaluate the rule against the database for a specific transaction.
        Returns a list of SignalResult objects (empty if rule did not trigger).
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
