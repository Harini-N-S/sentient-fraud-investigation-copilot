"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules: Device Anomaly & Shared Device Detection
-----------------------------------------------------------------------------
Rule Codes: R-DEV-02, R-DEV-SHR-01
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from rules.base import BaseRule, SignalResult


class NewDeviceRule(BaseRule):
    """
    R-DEV-02: Unverified or Novel Device Access
    Detects when a transaction is initiated from a hardware device that:
      1. Has a trust status of 'New_Unverified' or 'Suspicious_Blacklisted', OR
      2. Was first observed within 24 hours of the transaction, OR
      3. Is distinct from the customer's historical primary enrolled device.
    Notice: A new device is an investigative RISK SIGNAL, not standalone proof of fraud.
    """
    rule_code = "R-DEV-02"
    rule_name = "Unverified or Novel Device Access"
    rule_category = "Device_Risk"
    default_weight = 15
    default_severity = "MEDIUM"

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("""
            SELECT 
                t.transaction_id, t.customer_id, t.device_id, t.timestamp,
                d.device_model, d.trust_status, d.first_seen_timestamp, d.ip_address, 
                d.is_vpn_or_tor, d.is_rooted_jailbroken, d.primary_customer_id
            FROM transactions t
            JOIN devices d ON t.device_id = d.device_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        (
            tid, cid, dev_id, tx_ts_str,
            dmodel, trust, first_seen_str, ip,
            is_vpn, is_rooted, primary_cid
        ) = row

        tx_dt = datetime.fromisoformat(tx_ts_str)
        first_seen_dt = datetime.fromisoformat(first_seen_str)
        age_hours = (tx_dt - first_seen_dt).total_seconds() / 3600.0

        # Query other known devices for this customer
        cursor.execute("""
            SELECT DISTINCT device_id 
            FROM transactions 
            WHERE customer_id = ? AND transaction_id != ?;
        """, (cid, tid))
        prior_devices = [r[0] for r in cursor.fetchall()]

        is_new_device = (trust in ["New_Unverified", "Suspicious_Blacklisted"]) or (age_hours <= 24.0) or (dev_id not in prior_devices and len(prior_devices) > 0)

        if is_new_device:
            if trust == "Suspicious_Blacklisted" or is_rooted == 1 or is_vpn == 1:
                sev = "CRITICAL"
                weight = 30
                conf = 0.95
            elif age_hours <= 2.0:
                sev = "HIGH"
                weight = 20
                conf = 0.88
            else:
                sev = self.default_severity
                weight = self.default_weight
                conf = 0.75

            desc = (
                f"Device risk signal: Transaction executed from device {dev_id} ({dmodel}) "
                f"with trust status '{trust}', first seen {age_hours:.1f} hours prior. "
                f"Flags: VPN/Tor={bool(is_vpn)}, Rooted={bool(is_rooted)}."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": tid,
                "device_id": dev_id,
                "device_model": dmodel,
                "trust_status": trust,
                "device_age_hours_at_tx": round(age_hours, 1),
                "is_vpn_or_tor": bool(is_vpn),
                "is_rooted_jailbroken": bool(is_rooted),
                "ip_address": ip,
                "prior_known_devices_count": len(prior_devices),
                "prior_known_devices": prior_devices[:5]
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


class SharedDeviceRule(BaseRule):
    """
    R-DEV-SHR-01: Shared Hardware Device Across Disparate Accounts
    Detects when a single physical hardware device is utilized by multiple distinct customer accounts.
    May indicate: Fraud syndicate / mule ring, agent terminal sharing, or shared family phone.
    """
    rule_code = "R-DEV-SHR-01"
    rule_name = "Shared Hardware Device Across Disparate Accounts"
    rule_category = "Device_Risk"
    default_weight = 25
    default_severity = "HIGH"

    def __init__(self, min_distinct_customers: int = 2):
        self.min_distinct_customers = min_distinct_customers

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("SELECT device_id, customer_id, timestamp FROM transactions WHERE transaction_id = ?;", (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        dev_id, cid, ts = row

        cursor.execute("""
            SELECT 
                COUNT(DISTINCT customer_id) as cust_count,
                GROUP_CONCAT(DISTINCT customer_id) as cust_list,
                COUNT(transaction_id) as tx_count,
                SUM(amount_usd_equivalent) as total_vol
            FROM transactions
            WHERE device_id = ?;
        """, (dev_id,))
        stats = cursor.fetchone()

        if stats and stats[0] >= self.min_distinct_customers:
            cust_count, cust_list_str, tx_count, total_vol = stats
            cust_ids = cust_list_str.split(",") if cust_list_str else []

            sev = "CRITICAL" if cust_count >= 4 else "HIGH"
            weight = 35 if sev == "CRITICAL" else self.default_weight
            conf = min(0.98, 0.70 + (cust_count * 0.07))

            desc = (
                f"Shared device detected: Device {dev_id} is associated with {cust_count} distinct customer accounts "
                f"across {tx_count} transactions (totaling ${total_vol:,.2f} USD). "
                f"Linked accounts: {', '.join(cust_ids[:5])}."
            )

            evidence = {
                "transaction_id": transaction_id,
                "current_customer_id": cid,
                "device_id": dev_id,
                "distinct_customers_count": cust_count,
                "linked_customer_ids": cust_ids,
                "total_transactions_on_device": tx_count,
                "total_volume_usd_on_device": round(total_vol or 0.0, 2)
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
