"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rule: Value-Spike Detection
-----------------------------------------------------------------------------
Rule Code: R-VAL-07
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from rules.base import BaseRule, SignalResult


class ValueSpikeRule(BaseRule):
    """
    R-VAL-07: Unusually Large Transaction Value Spike
    Compares current transaction amount against the customer's historical 60-day baseline.
    Triggers when current transaction exceeds 400% of baseline average, or
    exceeds 150% of the historical single maximum transaction amount.
    """
    rule_code = "R-VAL-07"
    rule_name = "Unusually Large Transaction Value Spike"
    rule_category = "Value_Spike"
    default_weight = 20
    default_severity = "HIGH"

    def __init__(self, multiplier_threshold: float = 4.0, max_multiplier_threshold: float = 1.5, min_usd_floor: float = 250.0):
        self.multiplier_threshold = multiplier_threshold
        self.max_multiplier_threshold = max_multiplier_threshold
        self.min_usd_floor = min_usd_floor

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        # 1. Fetch transaction and baseline
        cursor.execute("""
            SELECT 
                t.transaction_id, t.customer_id, t.amount, t.currency, t.amount_usd_equivalent, t.timestamp,
                b.avg_tx_amount_usd, b.max_single_tx_amount_usd, b.avg_monthly_volume_usd,
                c.customer_segment
            FROM transactions t
            JOIN behavioural_baselines b ON t.customer_id = b.customer_id
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        (
            tid, cid, amt, curr, current_usd, ts,
            avg_usd, max_usd, monthly_vol, segment
        ) = row

        # Floor check to avoid flagging tiny routine transactions
        if current_usd < self.min_usd_floor:
            return []

        # Avoid div by zero
        baseline_avg = max(avg_usd, 1.0)
        deviation_pct = (current_usd / baseline_avg) * 100.0
        deviation_amount = current_usd - baseline_avg
        ratio_to_max = current_usd / max(max_usd, 1.0)

        is_spike = (current_usd >= baseline_avg * self.multiplier_threshold) or (current_usd >= max_usd * self.max_multiplier_threshold)

        if is_spike:
            # Determine severity based on severity of ratio
            if ratio_to_max >= 3.0 or deviation_pct >= 1000.0:
                sev = "CRITICAL"
                weight = 30
                conf = 0.95
            elif ratio_to_max >= 1.5 or deviation_pct >= 400.0:
                sev = "HIGH"
                weight = self.default_weight
                conf = 0.88
            else:
                sev = "MEDIUM"
                weight = 15
                conf = 0.75

            desc = (
                f"Value spike detected: Transaction of ${current_usd:,.2f} USD ({amt:,.2f} {curr}) is "
                f"{deviation_pct:,.1f}% of customer's baseline average (${baseline_avg:,.2f} USD) and "
                f"{ratio_to_max:.2f}x historical maximum (${max_usd:,.2f} USD)."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": tid,
                "current_amount_raw": amt,
                "currency": curr,
                "current_amount_usd": round(current_usd, 2),
                "baseline_avg_amount_usd": round(baseline_avg, 2),
                "baseline_max_amount_usd": round(max_usd, 2),
                "deviation_amount_usd": round(deviation_amount, 2),
                "deviation_percentage": round(deviation_pct, 1),
                "ratio_to_historical_max": round(ratio_to_max, 2),
                "customer_segment": segment
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
                timestamp=ts
            )]

        return []
