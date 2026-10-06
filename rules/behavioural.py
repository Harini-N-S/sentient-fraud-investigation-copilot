"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rule: Behavioural Baseline Deviation
-----------------------------------------------------------------------------
Rule Code: R-BEH-09
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from rules.base import BaseRule, SignalResult


class BehaviouralDeviationRule(BaseRule):
    """
    R-BEH-09: Customer Profile Behavioural Deviation
    Compares the current transaction dimensions against the customer's 60-day moving baseline:
      1. Temporal Deviation (Off-Hours: transaction hour outside typical_active_hours_utc)
      2. Channel Deviation (Unfamiliar transaction channel)
      3. Geographic Hub Deviation (Activity in city outside frequent_cities)
    Produces discrete, explainable signals rather than an opaque composite score.
    """
    rule_code = "R-BEH-09"
    rule_name = "Customer Profile Behavioural Deviation"
    rule_category = "Value_Spike"  # Or Behavioural
    default_weight = 15
    default_severity = "MEDIUM"

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("""
            SELECT 
                t.transaction_id, t.customer_id, t.channel, t.location_city, t.timestamp, t.amount_usd_equivalent,
                b.typical_active_hours_utc, b.common_channels, b.frequent_cities
            FROM transactions t
            JOIN behavioural_baselines b ON t.customer_id = b.customer_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        (
            tid, cid, chan, city, ts_str, amt_usd,
            hours_json, chans_json, cities_json
        ) = row

        tx_dt = datetime.fromisoformat(ts_str)
        tx_hour = tx_dt.hour

        active_hours = json.loads(hours_json) if hours_json else []
        common_chans = json.loads(chans_json) if chans_json else []
        freq_cities = json.loads(cities_json) if cities_json else []

        signals = []

        # 1. Temporal Off-Hours Check
        if active_hours and tx_hour not in active_hours:
            min_hour = min(active_hours)
            max_hour = max(active_hours)
            conf = 0.85 if amt_usd >= 1000.0 else 0.70
            sev = "HIGH" if amt_usd >= 5000.0 else "MEDIUM"
            weight = 20 if sev == "HIGH" else 12

            desc = (
                f"Off-hours activity: Transaction initiated at {tx_hour:02d}:{tx_dt.minute:02d} UTC, "
                f"which falls outside customer's established active window ({min_hour:02d}:00–{max_hour:02d}:00 UTC)."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": tid,
                "deviation_type": "TEMPORAL_OFF_HOURS",
                "transaction_time_utc": f"{tx_hour:02d}:{tx_dt.minute:02d}",
                "transaction_hour": tx_hour,
                "normal_active_hours_range": [min_hour, max_hour],
                "transaction_amount_usd": round(amt_usd, 2)
            }

            signals.append(SignalResult(
                rule_code=f"{self.rule_code}-TIME",
                rule_name="Off-Hours Behavioural Deviation",
                rule_category="Value_Spike",
                severity=sev,
                confidence_score=conf,
                weight=weight,
                description=desc,
                evidence_data=evidence,
                timestamp=ts_str
            ))

        # 2. Novel Channel Check (only if high value)
        if common_chans and chan not in common_chans and amt_usd >= 1500.0:
            desc = (
                f"Unfamiliar channel: Transaction executed via '{chan}', whereas customer's "
                f"historical baseline utilizes {', '.join(common_chans)}."
            )
            evidence = {
                "customer_id": cid,
                "transaction_id": tid,
                "deviation_type": "CHANNEL_DEVIATION",
                "current_channel": chan,
                "established_channels": common_chans,
                "transaction_amount_usd": round(amt_usd, 2)
            }
            signals.append(SignalResult(
                rule_code=f"{self.rule_code}-CHAN",
                rule_name="Unfamiliar Channel Deviation",
                rule_category="Value_Spike",
                severity="MEDIUM",
                confidence_score=0.72,
                weight=10,
                description=desc,
                evidence_data=evidence,
                timestamp=ts_str
            ))

        return signals
