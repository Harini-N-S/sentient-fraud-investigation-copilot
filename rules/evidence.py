"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Evidence Packet Builder
-----------------------------------------------------------------------------
Constructs the 3-Tier Grounded Evidence Packet:
  Tier 1: EXACT DATA (Raw, immutable database records)
  Tier 2: CALCULATED (Deterministic mathematical indicators & scores)
  Tier 3: RETRIEVED EVIDENCE (Related graph nodes, history, baselines, logs)
  Tier 4: AI REASONING (Strictly deferred to Phase 7 Groq layer)
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


@dataclass
class EvidencePacket:
    transaction_id: str
    customer_id: str
    generated_at: str
    exact_data: Dict[str, Any]
    calculated: Dict[str, Any]
    retrieved_evidence: Dict[str, Any]
    ai_reasoning: Optional[Dict[str, Any]] = None  # Strictly None in Phase 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "generated_at": self.generated_at,
            "tier_1_exact_data": self.exact_data,
            "tier_2_calculated": self.calculated,
            "tier_3_retrieved_evidence": self.retrieved_evidence,
            "tier_4_ai_reasoning": self.ai_reasoning
        }


class EvidencePacketBuilder:
    """
    Constructs comprehensive forensic evidence dossiers from the SQLite database.
    Guarantees that subsequent AI layers are anchored 100% in factual ground truth.
    """

    @staticmethod
    def build(db_conn, transaction_id: str, risk_assessment: Optional[Any] = None) -> Optional[EvidencePacket]:
        cursor = db_conn.cursor()

        # 1. TIER 1: EXACT DATA (Raw transaction, account, customer, device, beneficiary)
        cursor.execute("""
            SELECT 
                t.transaction_id, t.account_id, t.customer_id, t.beneficiary_id, t.device_id,
                t.channel, t.transaction_type, t.amount, t.currency, t.amount_usd_equivalent,
                t.location_city, t.status, t.timestamp,
                acc.account_type, acc.currency as acc_curr, acc.current_balance, acc.available_balance, acc.account_status,
                c.full_name, c.customer_segment, c.kyc_status, c.primary_phone, c.email, c.registered_city, c.risk_category, c.created_at as cust_created,
                d.device_type, d.device_model, d.os_version, d.device_fingerprint_hash, d.ip_address, d.ip_city, d.is_vpn_or_tor, d.is_rooted_jailbroken, d.trust_status,
                b.beneficiary_name, b.institution_name, b.account_or_phone, b.beneficiary_type, b.registered_city as ben_city, b.is_known_mule
            FROM transactions t
            JOIN accounts acc ON t.account_id = acc.account_id
            JOIN customers c ON t.customer_id = c.customer_id
            JOIN devices d ON t.device_id = d.device_id
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        if not row:
            return None

        exact_data = {
            "transaction": {
                "transaction_id": row[0],
                "channel": row[5],
                "transaction_type": row[6],
                "amount": row[7],
                "currency": row[8],
                "amount_usd_equivalent": row[9],
                "location_city": row[10],
                "status": row[11],
                "timestamp": row[12]
            },
            "source_account": {
                "account_id": row[1],
                "account_type": row[13],
                "currency": row[14],
                "current_balance": row[15],
                "available_balance": row[16],
                "account_status": row[17]
            },
            "customer": {
                "customer_id": row[2],
                "full_name": row[18],
                "segment": row[19],
                "kyc_status": row[20],
                "phone": row[21],
                "email": row[22],
                "registered_city": row[23],
                "risk_category": row[24],
                "onboarding_date": row[25]
            },
            "device": {
                "device_id": row[4],
                "device_type": row[26],
                "device_model": row[27],
                "os_version": row[28],
                "fingerprint_hash": row[29],
                "ip_address": row[30],
                "ip_city": row[31],
                "is_vpn_or_tor": bool(row[32]),
                "is_rooted": bool(row[33]),
                "trust_status": row[34]
            },
            "beneficiary": {
                "beneficiary_id": row[3],
                "beneficiary_name": row[35],
                "institution": row[36],
                "account_or_phone": row[37],
                "beneficiary_type": row[38],
                "registered_city": row[39],
                "is_known_mule": bool(row[40])
            }
        }

        cid = row[2]
        dev_id = row[4]
        bid = row[3]
        tx_ts = row[12]

        # 2. TIER 2: CALCULATED METRICS
        # Compute 24-hour velocity, 7-day volume, device customer count, beneficiary sender count
        cursor.execute("""
            SELECT COUNT(*), SUM(amount_usd_equivalent)
            FROM transactions
            WHERE customer_id = ? AND timestamp <= ? AND timestamp >= datetime(?, '-24 hours');
        """, (cid, tx_ts, tx_ts))
        v24 = cursor.fetchone()
        tx_count_24h = v24[0] if v24 else 0
        tx_vol_24h = round(v24[1] or 0.0, 2)

        # Baseline deviation calculations
        cursor.execute("SELECT avg_tx_amount_usd, max_single_tx_amount_usd, avg_monthly_volume_usd FROM behavioural_baselines WHERE customer_id = ?;", (cid,))
        base_row = cursor.fetchone()
        avg_base = base_row[0] if base_row else 1.0
        max_base = base_row[1] if base_row else 1.0
        dev_pct = round((row[9] / max(avg_base, 1.0)) * 100.0, 1)

        # Device distinct customers
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM transactions WHERE device_id = ?;", (dev_id,))
        dev_cust_count = cursor.fetchone()[0]

        # Beneficiary distinct senders
        cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM transactions WHERE beneficiary_id = ?;", (bid,))
        ben_sender_count = cursor.fetchone()[0]

        calculated = {
            "composite_risk_score": risk_assessment.composite_risk_score if risk_assessment else 0,
            "severity": risk_assessment.severity if risk_assessment else "LOW",
            "scenario_classification": risk_assessment.scenario_type if risk_assessment else "ROUTINE",
            "velocity_24h_count": tx_count_24h,
            "velocity_24h_volume_usd": tx_vol_24h,
            "amount_deviation_vs_baseline_pct": dev_pct,
            "ratio_to_historical_single_max": round(row[9] / max(max_base, 1.0), 2),
            "device_associated_customers_count": dev_cust_count,
            "beneficiary_distinct_senders_count": ben_sender_count,
            "potential_false_positive": risk_assessment.potential_false_positive if risk_assessment else False,
            "mitigating_factors": risk_assessment.mitigating_factors if risk_assessment else []
        }

        # 3. TIER 3: RETRIEVED EVIDENCE
        # Baseline profile
        cursor.execute("SELECT * FROM behavioural_baselines WHERE customer_id = ?;", (cid,))
        col_names = [d[0] for d in cursor.description]
        b_data = cursor.fetchone()
        baseline_dict = dict(zip(col_names, b_data)) if b_data else {}
        if "typical_active_hours_utc" in baseline_dict:
            baseline_dict["typical_active_hours_utc"] = json.loads(baseline_dict["typical_active_hours_utc"])
        if "common_channels" in baseline_dict:
            baseline_dict["common_channels"] = json.loads(baseline_dict["common_channels"])

        # Prior 5 transactions for customer
        cursor.execute("""
            SELECT transaction_id, timestamp, amount_usd_equivalent, channel, beneficiary_id, location_city
            FROM transactions
            WHERE customer_id = ? AND timestamp < ?
            ORDER BY timestamp DESC
            LIMIT 5;
        """, (cid, tx_ts))
        recent_txns = [
            {"transaction_id": r[0], "timestamp": r[1], "amount_usd": r[2], "channel": r[3], "beneficiary_id": r[4], "city": r[5]}
            for r in cursor.fetchall()
        ]

        # Prior 5 auth activities for customer
        cursor.execute("""
            SELECT activity_id, event_type, status, failure_reason, device_id, ip_address, timestamp
            FROM auth_activities
            WHERE customer_id = ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT 5;
        """, (cid, tx_ts))
        recent_auths = [
            {"activity_id": r[0], "event_type": r[1], "status": r[2], "reason": r[3], "device_id": r[4], "ip": r[5], "timestamp": r[6]}
            for r in cursor.fetchall()
        ]

        # Connected accounts on this device (syndicate ring detection)
        cursor.execute("SELECT DISTINCT customer_id FROM transactions WHERE device_id = ? AND customer_id != ?;", (dev_id, cid))
        linked_accounts = [r[0] for r in cursor.fetchall()]

        retrieved_evidence = {
            "customer_baseline": baseline_dict,
            "preceding_transactions": recent_txns,
            "session_security_logs": recent_auths,
            "device_shared_customer_ids": linked_accounts,
            "triggered_signals": [s.to_dict() for s in risk_assessment.contributing_signals] if risk_assessment else []
        }

        return EvidencePacket(
            transaction_id=transaction_id,
            customer_id=cid,
            generated_at=datetime.now(timezone.utc).isoformat(),
            exact_data=exact_data,
            calculated=calculated,
            retrieved_evidence=retrieved_evidence,
            ai_reasoning=None  # STRICTLY NULL IN PHASE 3
        )
