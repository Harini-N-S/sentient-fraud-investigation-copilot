"""
Deterministic Evaluation Service
-----------------------------------------------------------------------------
Bridges FastAPI request handlers to the Phase 3 FraudIntelligenceEngine.
Zero duplicated fraud logic in API controllers.
100% deterministic rules, correlation, and scoring.
"""

from typing import Dict, Any, List, Optional
from backend.app.config import settings
from rules.engine import FraudIntelligenceEngine, TransactionEvaluationResult


class EvaluationService:
    """Invokes Phase 3 Deterministic Fraud Intelligence Engine on transactions and customers."""

    def __init__(self):
        self.engine = FraudIntelligenceEngine(db_path=str(settings.database_path))

    def evaluate_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Executes full deterministic rule suite, correlation, and scoring for a transaction.
        """
        result: Optional[TransactionEvaluationResult] = self.engine.evaluate_transaction(
            transaction_id=transaction_id,
            build_evidence=True
        )
        if not result:
            return None

        data = result.to_dict()
        return data

    def evaluate_customer(self, customer_id: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Evaluates recent transactions for a customer, aggregates contributing signals,
        computes peak risk metrics, and constructs a holistic forensic summary.
        """
        # First verify customer exists
        conn = self.engine._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT customer_id, full_name, risk_category FROM customers WHERE customer_id = ?;", (customer_id,))
            cust_row = cursor.fetchone()
            if not cust_row:
                return None
            full_name = cust_row[1]
            base_risk = cust_row[2]
        finally:
            conn.close()

        # Run deterministic evaluation on customer's transactions
        tx_results: List[TransactionEvaluationResult] = self.engine.evaluate_customer(customer_id, limit=limit)
        
        evaluated_count = len(tx_results)
        flagged_count = sum(1 for r in tx_results if r.is_flagged)
        highest_score = max([r.risk_score for r in tx_results], default=0)

        # Severity rank mapping
        sev_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        overall_sev = "LOW"
        max_rank = 1
        for r in tx_results:
            rank = sev_rank.get(r.severity.upper(), 1)
            if rank > max_rank:
                max_rank = rank
                overall_sev = r.severity.upper()

        # Collect unique contributing signals
        unique_signals = {}
        for r in tx_results:
            for s in r.signals:
                key = (s.rule_code, r.transaction_id)
                if key not in unique_signals:
                    unique_signals[key] = {
                        "rule_code": s.rule_code,
                        "rule_name": s.rule_name,
                        "rule_category": s.rule_category,
                        "severity": s.severity,
                        "confidence_score": s.confidence_score,
                        "signal_description": getattr(s, "description", getattr(s, "signal_description", "")),
                        "transaction_id": r.transaction_id
                    }

        # Build narrative summary
        if flagged_count > 0:
            scenarios = list(set(r.scenario_type for r in tx_results if r.is_flagged and r.scenario_type != "ROUTINE"))
            scenario_str = ", ".join(scenarios) if scenarios else "Anomaly"
            summary = (
                f"Customer {customer_id} ({full_name}) has {flagged_count} of {evaluated_count} recent transactions flagged. "
                f"Peak composite risk score {highest_score}/100 ({overall_sev} severity) driven by {len(unique_signals)} deterministic signals. "
                f"Primary scenario typology: {scenario_str}."
            )
        else:
            summary = (
                f"Customer {customer_id} ({full_name}) exhibits routine behaviour across all {evaluated_count} evaluated transactions. "
                f"Zero deterministic fraud rules breached. Baseline category: {base_risk}."
            )

        return {
            "customer_id": customer_id,
            "evaluated_transactions_count": evaluated_count,
            "flagged_transactions_count": flagged_count,
            "highest_risk_score": highest_score,
            "overall_severity": overall_sev,
            "total_signals_detected": len(unique_signals),
            "transaction_evaluations": [r.to_dict() for r in tx_results],
            "contributing_signals": list(unique_signals.values()),
            "summary": summary
        }


evaluation_service = EvaluationService()
