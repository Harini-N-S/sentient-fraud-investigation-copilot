"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules: Authentication & ATO Detection
-----------------------------------------------------------------------------
Rule Codes: R-AUTH-08, R-ATO-05
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from rules.base import BaseRule, SignalResult


class AuthenticationAnomalyRule(BaseRule):
    """
    R-AUTH-08: Consecutive Failed Authentication Attempts
    Detects when a customer account experiences multiple failed authentication attempts
    (e.g. invalid PIN or credentials) within 30 minutes prior to a transaction.
    """
    rule_code = "R-AUTH-08"
    rule_name = "Consecutive Failed Authentication Attempts"
    rule_category = "Auth_Anomaly"
    default_weight = 20
    default_severity = "HIGH"

    def __init__(self, min_failed_attempts: int = 3, window_minutes: int = 30):
        self.min_failed_attempts = min_failed_attempts
        self.window_minutes = window_minutes

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("SELECT customer_id, timestamp FROM transactions WHERE transaction_id = ?;", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        cid, tx_ts_str = row
        tx_dt = datetime.fromisoformat(tx_ts_str)
        window_start_dt = tx_dt - timedelta(minutes=self.window_minutes)

        cursor.execute("""
            SELECT activity_id, event_type, status, failure_reason, ip_address, timestamp
            FROM auth_activities
            WHERE customer_id = ?
              AND status = 'Failed'
              AND timestamp >= ?
              AND timestamp <= ?
            ORDER BY timestamp DESC;
        """, (cid, window_start_dt.isoformat(), tx_ts_str))

        failed_logs = cursor.fetchall()
        fail_count = len(failed_logs)

        if fail_count >= self.min_failed_attempts:
            sev = "CRITICAL" if fail_count >= 5 else "HIGH"
            weight = 30 if sev == "CRITICAL" else self.default_weight
            conf = min(0.95, 0.75 + (fail_count * 0.05))

            desc = (
                f"Authentication anomaly detected: {fail_count} failed authentication attempts "
                f"occurred within {self.window_minutes} minutes preceding this transaction."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": transaction_id,
                "failed_attempts_count": fail_count,
                "window_minutes": self.window_minutes,
                "failed_activity_ids": [log[0] for log in failed_logs],
                "failure_reasons": list(set(log[3] for log in failed_logs if log[3])),
                "attempt_ips": list(set(log[4] for log in failed_logs)),
                "most_recent_failure": failed_logs[0][5]
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
                timestamp=tx_ts_str
            )]

        return []


class ATOPatternRule(BaseRule):
    """
    R-ATO-05: Critical Credential / Device Change Preceding Transfer
    Detects high-risk Account Takeover (ATO) behavior where an administrative security event
    (Password_Reset_Triggered or Device_Enrolled) precedes an outbound transaction within 60 minutes.
    """
    rule_code = "R-ATO-05"
    rule_name = "Critical Security Event Preceding Transfer"
    rule_category = "Credential_ATO"
    default_weight = 35
    default_severity = "CRITICAL"

    def __init__(self, window_minutes: int = 60):
        self.window_minutes = window_minutes

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("SELECT customer_id, timestamp, amount_usd_equivalent FROM transactions WHERE transaction_id = ?;", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        cid, tx_ts_str, tx_usd = row
        tx_dt = datetime.fromisoformat(tx_ts_str)
        window_start_dt = tx_dt - timedelta(minutes=self.window_minutes)

        cursor.execute("""
            SELECT activity_id, event_type, device_id, ip_address, timestamp
            FROM auth_activities
            WHERE customer_id = ?
              AND event_type IN ('Password_Reset_Triggered', 'Device_Enrolled')
              AND timestamp >= ?
              AND timestamp <= ?
            ORDER BY timestamp DESC;
        """, (cid, window_start_dt.isoformat(), tx_ts_str))

        sec_events = cursor.fetchall()
        if sec_events:
            most_recent_ev = sec_events[0]
            act_id, ev_type, dev_id, ip, ev_ts_str = most_recent_ev
            elapsed_mins = round((tx_dt - datetime.fromisoformat(ev_ts_str)).total_seconds() / 60.0, 1)

            conf = 0.96
            desc = (
                f"ATO signature detected: Critical security event '{ev_type}' occurred on device {dev_id} "
                f"just {elapsed_mins} minutes prior to outbound transaction (${tx_usd:,.2f} USD)."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": transaction_id,
                "security_activity_id": act_id,
                "security_event_type": ev_type,
                "security_event_device_id": dev_id,
                "security_event_ip": ip,
                "security_event_timestamp": ev_ts_str,
                "elapsed_minutes_to_transaction": elapsed_mins,
                "transaction_amount_usd": round(tx_usd, 2)
            }

            return [SignalResult(
                rule_code=self.rule_code,
                rule_name=self.rule_name,
                rule_category=self.rule_category,
                severity=self.default_severity,
                confidence_score=conf,
                weight=self.default_weight,
                description=desc,
                evidence_data=evidence,
                timestamp=tx_ts_str
            )]

        return []
