"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rule: Structuring / Smurfing Detection
-----------------------------------------------------------------------------
Rule Code: R-SMURF-06
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from rules.base import BaseRule, SignalResult


class StructuringRule(BaseRule):
    """
    R-SMURF-06: Near-Threshold Structuring Pattern
    Detects when a customer executes multiple transactions clustered just below
    regulatory reporting ceilings (e.g. $10,000 USD BCC AML reporting threshold),
    where individual transactions sit between $8,500 and $9,999 USD.
    Notice: Structuring detection is a technical RISK SIGNAL, not legal proof of money laundering.
    """
    rule_code = "R-SMURF-06"
    rule_name = "Near-Threshold Structuring Pattern"
    rule_category = "Structuring"
    default_weight = 25
    default_severity = "HIGH"

    def __init__(self, reporting_threshold_usd: float = 10000.0, lower_bound_ratio: float = 0.85, window_hours: int = 4, min_cluster_count: int = 2):
        self.reporting_threshold_usd = reporting_threshold_usd
        self.lower_bound_usd = reporting_threshold_usd * lower_bound_ratio  # $8,500
        self.window_hours = window_hours
        self.min_cluster_count = min_cluster_count

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("""
            SELECT transaction_id, customer_id, amount_usd_equivalent, timestamp
            FROM transactions
            WHERE transaction_id = ?;
        """, (transaction_id,))
        curr = cursor.fetchone()
        if not curr:
            return []

        tid, cid, curr_usd, curr_ts_str = curr

        # Only evaluate if current transaction itself sits in the near-threshold band [8,500, 9,999.99]
        if not (self.lower_bound_usd <= curr_usd < self.reporting_threshold_usd):
            return []

        curr_dt = datetime.fromisoformat(curr_ts_str)
        window_start_dt = curr_dt - timedelta(hours=self.window_hours)

        # Query all transactions by this customer in the rolling window that sit in the near-threshold band
        cursor.execute("""
            SELECT transaction_id, amount, currency, amount_usd_equivalent, timestamp, beneficiary_id
            FROM transactions
            WHERE customer_id = ?
              AND timestamp >= ?
              AND timestamp <= ?
              AND amount_usd_equivalent >= ?
              AND amount_usd_equivalent < ?
            ORDER BY timestamp ASC;
        """, (cid, window_start_dt.isoformat(), curr_ts_str, self.lower_bound_usd, self.reporting_threshold_usd))

        cluster_txns = cursor.fetchall()
        cluster_count = len(cluster_txns)

        if cluster_count >= self.min_cluster_count:
            tx_ids = [tx[0] for tx in cluster_txns]
            amounts = [round(tx[3], 2) for tx in cluster_txns]
            total_combined = sum(amounts)
            first_ts = cluster_txns[0][4]

            sev = "CRITICAL" if cluster_count >= 4 else "HIGH"
            weight = 35 if sev == "CRITICAL" else self.default_weight
            conf = min(0.96, 0.78 + (cluster_count * 0.05))

            desc = (
                f"Structuring-like pattern detected: {cluster_count} transactions occurred within {self.window_hours} hours, "
                f"each sized between ${self.lower_bound_usd:,.0f} and ${self.reporting_threshold_usd:,.0f} USD. "
                f"Combined volume: ${total_combined:,.2f} USD (exceeds single $10,000 threshold)."
            )

            evidence = {
                "customer_id": cid,
                "current_transaction_id": tid,
                "reporting_threshold_usd": self.reporting_threshold_usd,
                "near_threshold_band_usd": [self.lower_bound_usd, self.reporting_threshold_usd],
                "cluster_transaction_count": cluster_count,
                "cluster_transaction_ids": tx_ids,
                "individual_amounts_usd": amounts,
                "total_combined_volume_usd": round(total_combined, 2),
                "window_hours": self.window_hours,
                "window_start_timestamp": first_ts,
                "window_end_timestamp": curr_ts_str
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
                timestamp=curr_ts_str
            )]

        return []
