"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules: Beneficiary Anomalies & Mule Detection
-----------------------------------------------------------------------------
Rule Codes: R-BEN-03, R-MULE-04
Status: [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
"""

from typing import List, Dict, Any, Optional
from rules.base import BaseRule, SignalResult


class NewBeneficiaryRule(BaseRule):
    """
    R-BEN-03: First-Time Recipient Beneficiary Transfer
    Detects transactions directed to a beneficiary that has zero prior transaction history
    with the originating customer.
    Notice: New beneficiary is an exploratory RISK SIGNAL, not standalone proof of fraud.
    """
    rule_code = "R-BEN-03"
    rule_name = "First-Time Recipient Beneficiary Transfer"
    rule_category = "Mule_Network"
    default_weight = 15
    default_severity = "LOW"

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("""
            SELECT 
                t.transaction_id, t.customer_id, t.beneficiary_id, t.timestamp, t.amount_usd_equivalent,
                b.beneficiary_name, b.institution_name, b.beneficiary_type, b.is_known_mule
            FROM transactions t
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        tid, cid, bid, ts, amt_usd, bname, binst, btype, is_mule = row

        # Check count of prior transactions between this customer and this beneficiary
        cursor.execute("""
            SELECT COUNT(*), MIN(timestamp)
            FROM transactions
            WHERE customer_id = ? AND beneficiary_id = ? AND timestamp < ?;
        """, (cid, bid, ts))
        prior_stats = cursor.fetchone()
        prior_count = prior_stats[0] if prior_stats else 0

        if prior_count == 0:
            # If known mule, escalate to CRITICAL
            if is_mule:
                sev = "CRITICAL"
                weight = 30
                conf = 0.95
            elif amt_usd >= 3000.0:
                sev = "MEDIUM"
                weight = 20
                conf = 0.82
            else:
                sev = self.default_severity
                weight = self.default_weight
                conf = 0.70

            desc = (
                f"New beneficiary detected: Customer {cid} has never previously transacted with "
                f"beneficiary {bid} ({bname} via {binst}). Current transfer: ${amt_usd:,.2f} USD."
            )

            evidence = {
                "customer_id": cid,
                "transaction_id": tid,
                "beneficiary_id": bid,
                "beneficiary_name": bname,
                "institution_name": binst,
                "beneficiary_type": btype,
                "prior_transactions_with_beneficiary": 0,
                "is_known_mule_flag": bool(is_mule),
                "transfer_amount_usd": round(amt_usd, 2)
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


class SharedBeneficiaryRule(BaseRule):
    """
    R-MULE-04: Multiple-Customer Beneficiary Concentration (Mule Inflow)
    Detects when a single beneficiary receives transfers from multiple distinct customers,
    exhibiting a classic aggregator / money mule fan-in topology.
    """
    rule_code = "R-MULE-04"
    rule_name = "Multiple-Customer Beneficiary Concentration"
    rule_category = "Mule_Network"
    default_weight = 25
    default_severity = "HIGH"

    def __init__(self, min_distinct_senders: int = 3):
        self.min_distinct_senders = min_distinct_senders

    def evaluate(self, db_conn, transaction_id: str, context: Optional[Dict[str, Any]] = None) -> List[SignalResult]:
        cursor = db_conn.cursor()

        cursor.execute("""
            SELECT 
                t.transaction_id, t.customer_id, t.beneficiary_id, t.timestamp,
                b.beneficiary_name, b.institution_name, b.is_known_mule
            FROM transactions t
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return []

        tid, current_cid, bid, ts, bname, binst, is_mule = row

        cursor.execute("""
            SELECT 
                COUNT(DISTINCT customer_id) as sender_count,
                GROUP_CONCAT(DISTINCT customer_id) as senders,
                COUNT(transaction_id) as total_txs,
                SUM(amount_usd_equivalent) as total_vol
            FROM transactions
            WHERE beneficiary_id = ?;
        """, (bid,))
        stats = cursor.fetchone()

        if stats and stats[0] >= self.min_distinct_senders:
            sender_count, senders_str, total_txs, total_vol = stats
            sender_list = senders_str.split(",") if senders_str else []

            if is_mule or sender_count >= 6:
                sev = "CRITICAL"
                weight = 35
                conf = 0.96
            else:
                sev = self.default_severity
                weight = self.default_weight
                conf = min(0.92, 0.70 + (sender_count * 0.04))

            desc = (
                f"Multiple-customer beneficiary concentration detected: Beneficiary {bid} ({bname}) "
                f"has received funds from {sender_count} distinct senders across {total_txs} transactions "
                f"(totaling ${total_vol:,.2f} USD). Senders: {', '.join(sender_list[:5])}."
            )

            evidence = {
                "transaction_id": tid,
                "beneficiary_id": bid,
                "beneficiary_name": bname,
                "institution_name": binst,
                "distinct_senders_count": sender_count,
                "sender_customer_ids": sender_list,
                "total_inbound_transactions": total_txs,
                "total_aggregated_volume_usd": round(total_vol or 0.0, 2),
                "is_known_mule_flag": bool(is_mule)
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
