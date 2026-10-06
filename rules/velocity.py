"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rule: Transaction Velocity Detection
-----------------------------------------------------------------------------
Rule Code: R-VEL-01
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from rules.base import BaseRule, SignalResult


class VelocityRule(BaseRule):
    """
    R-VEL-01: High-Frequency Transaction Velocity Burst
    Detects when a customer executes multiple rapid transactions within a short time window.
    Default Threshold: >= 4 transactions within 300 seconds (5 minutes),
    or >= 5 transactions within 600 seconds.
    """
    rule_code = "R-VEL-01"
    rule_name = "High-Frequency Transaction Velocity Burst"
    rule_category = "Velocity"
    default_weight = 25
    default_severity = "HIGH"

    def __init__(self, window_seconds: int = 300, min_transaction_count: int = 4):
        self.window_seconds = window_seconds
        self.min_transaction_count = min_transaction_count

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        # 1. Fetch target transaction details
        cursor.execute("""
            SELECT customer_id, timestamp, amount_usd_equivalent 
            FROM transactions 
            WHERE transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        customer_id, current_ts_str, current_usd = row
        current_dt = datetime.fromisoformat(current_ts_str)
        window_start_dt = current_dt - timedelta(seconds=self.window_seconds)

        # 2. Query transactions for this customer within the rolling window up to current transaction
        cursor.execute("""
            SELECT transaction_id, timestamp, amount, currency, amount_usd_equivalent, beneficiary_id
            FROM transactions
            WHERE customer_id = ? 
              AND timestamp >= ? 
              AND timestamp <= ?
            ORDER BY timestamp ASC;
        """, (customer_id, window_start_dt.isoformat(), current_ts_str))
        
        window_txns = cursor.fetchall()
        tx_count = len(window_txns)

        if tx_count >= self.min_transaction_count:
            tx_ids = [tx[0] for tx in window_txns]
            total_usd = sum(tx[4] for tx in window_txns)
            first_ts = window_txns[0][1]
            elapsed_seconds = int((current_dt - datetime.fromisoformat(first_ts)).total_seconds())
            if elapsed_seconds == 0:
                elapsed_seconds = 1  # prevent div by zero if identical timestamps

            # Dynamic severity: 4 txns = HIGH (weight 25), >= 6 txns = CRITICAL (weight 35)
            sev = "CRITICAL" if tx_count >= 6 else "HIGH"
            weight = 35 if sev == "CRITICAL" else self.default_weight
            conf = min(0.99, 0.75 + (tx_count * 0.04))

            desc = (
                f"Velocity burst detected: {tx_count} transactions occurred within {elapsed_seconds} seconds "
                f"(window threshold: {self.window_seconds}s), moving a cumulative total of ${total_usd:,.2f} USD."
            )

            evidence = {
                "customer_id": customer_id,
                "current_transaction_id": transaction_id,
                "window_threshold_seconds": self.window_seconds,
                "observed_elapsed_seconds": elapsed_seconds,
                "transaction_count": tx_count,
                "total_volume_usd": round(total_usd, 2),
                "transaction_ids": tx_ids,
                "first_transaction_timestamp": first_ts,
                "current_transaction_timestamp": current_ts_str
            }

            return [SignalResult(
                rule_code=self.rule_code,
                rule_name=self.rule_name,
                rule_category=self.rule_category,
                severity=sev,
                confidence_score=conf,
                weight=weight,
                description=desc,
                evidence_data=evidence,
                timestamp=current_ts_str
            )]

        return []
