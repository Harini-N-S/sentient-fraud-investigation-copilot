"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Intelligence Engine
-----------------------------------------------------------------------------
Coordinates all deterministic rules, correlation, risk scoring, and evidence packet assembly.
Zero Machine Learning black-box. Zero LLM. 100% deterministic.
"""

import sqlite3
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from rules.base import BaseRule, SignalResult
from rules.velocity import VelocityRule
from rules.value_spike import ValueSpikeRule
from rules.device import NewDeviceRule, SharedDeviceRule
from rules.beneficiary import NewBeneficiaryRule, SharedBeneficiaryRule
from rules.geographic import GeographicVelocityRule
from rules.structuring import StructuringRule
from rules.authentication import AuthenticationAnomalyRule, ATOPatternRule
from rules.behavioural import BehaviouralDeviationRule
from rules.correlation import CorrelationEngine, RiskAssessment
from rules.evidence import EvidencePacketBuilder, EvidencePacket


@dataclass
class TransactionEvaluationResult:
    transaction_id: str
    customer_id: str
    is_flagged: bool
    risk_score: int
    severity: str
    scenario_type: str
    reason_summary: str
    signals: List[SignalResult]
    scoring_breakdown: List[Dict[str, Any]]
    evidence_packet: Optional[EvidencePacket] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "is_flagged": self.is_flagged,
            "risk_score": self.risk_score,
            "severity": self.severity,
            "scenario_type": self.scenario_type,
            "reason_summary": self.reason_summary,
            "signals": [s.to_dict() for s in self.signals],
            "scoring_breakdown": self.scoring_breakdown,
            "evidence_packet": self.evidence_packet.to_dict() if self.evidence_packet else None
        }


class FraudIntelligenceEngine:
    """
    Main programmatic interface for the Phase 3 Deterministic Intelligence Layer.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        # Instantiate registered rule catalogue
        self.rules: List[BaseRule] = [
            VelocityRule(),
            ValueSpikeRule(),
            NewDeviceRule(),
            SharedDeviceRule(),
            NewBeneficiaryRule(),
            SharedBeneficiaryRule(),
            GeographicVelocityRule(),
            StructuringRule(),
            AuthenticationAnomalyRule(),
            ATOPatternRule(),
            BehaviouralDeviationRule()
        ]

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def evaluate_transaction(self, transaction_id: str, build_evidence: bool = True) -> Optional[TransactionEvaluationResult]:
        """
        Evaluate all deterministic rules against a single transaction.
        Returns a structured TransactionEvaluationResult.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT customer_id FROM transactions WHERE transaction_id = ?;", (transaction_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cid = row[0]

            # 1. Run all individual deterministic rules
            all_signals: List[SignalResult] = []
            for rule in self.rules:
                signals = rule.evaluate(conn, transaction_id)
                all_signals.extend(signals)

            # 2. Correlate signals & compute composite risk score
            if all_signals:
                assessment = CorrelationEngine.evaluate(all_signals, conn, transaction_id)
                score = assessment.composite_risk_score
                sev = assessment.severity
                scenario = assessment.scenario_type
                reason = assessment.reason_summary
                breakdown = assessment.scoring_breakdown
                is_flagged = score >= 35 or sev in ["MEDIUM", "HIGH", "CRITICAL"]
            else:
                assessment = None
                score = 0
                sev = "LOW"
                scenario = "ROUTINE"
                reason = "No deterministic risk signals breached."
                breakdown = []
                is_flagged = False

            # 3. Build evidence packet
            evidence_packet = None
            if build_evidence:
                evidence_packet = EvidencePacketBuilder.build(conn, transaction_id, assessment)

            return TransactionEvaluationResult(
                transaction_id=transaction_id,
                customer_id=cid,
                is_flagged=is_flagged,
                risk_score=score,
                severity=sev,
                scenario_type=scenario,
                reason_summary=reason,
                signals=all_signals,
                scoring_breakdown=breakdown,
                evidence_packet=evidence_packet
            )
        finally:
            conn.close()

    def evaluate_customer(self, customer_id: str, limit: int = 10) -> List[TransactionEvaluationResult]:
        """
        Evaluate the most recent transactions for a customer.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT transaction_id FROM transactions 
                WHERE customer_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?;
            """, (customer_id, limit))
            tids = [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()

        results = []
        for tid in tids:
            res = self.evaluate_transaction(tid)
            if res:
                results.append(res)
        return results

    def get_evidence_packet(self, transaction_id: str) -> Optional[EvidencePacket]:
        """
        Construct a standalone 3-tier evidence packet for any transaction.
        """
        conn = self._get_connection()
        try:
            eval_res = self.evaluate_transaction(transaction_id, build_evidence=True)
            return eval_res.evidence_packet if eval_res else None
        finally:
            conn.close()
