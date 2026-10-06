"""
Overview Repository
-----------------------------------------------------------------------------
Computes system-level dashboard metrics directly from the live synthetic database.
Zero hardcoding. 100% computed ground truth.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any


class OverviewRepository:
    """Calculates live platform KPIs and triage statistics."""

    @staticmethod
    def get_overview_metrics(db: sqlite3.Connection) -> Dict[str, Any]:
        cursor = db.cursor()

        # 1. Total entity counts
        cursor.execute("SELECT COUNT(*) FROM customers;")
        total_customers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM accounts;")
        total_accounts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount_usd_equivalent), 0.0) FROM transactions;")
        tx_row = cursor.fetchone()
        total_transactions = tx_row[0]
        total_volume_usd = round(float(tx_row[1]), 2)

        cursor.execute("SELECT COUNT(*) FROM alerts;")
        total_alerts = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM fraud_signals;")
        total_signals = cursor.fetchone()[0]

        # 2. Alert severity counts
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM alerts 
            GROUP BY severity;
        """)
        sev_counts = {row[0].upper(): row[1] for row in cursor.fetchall()}
        critical_alerts = sev_counts.get("CRITICAL", 0)
        high_alerts = sev_counts.get("HIGH", 0)
        medium_alerts = sev_counts.get("MEDIUM", 0)
        low_alerts = sev_counts.get("LOW", 0)

        # 3. Alert status counts
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM alerts 
            GROUP BY status;
        """)
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # 4. Total flagged volume in USD
        cursor.execute("""
            SELECT COALESCE(SUM(t.amount_usd_equivalent), 0.0)
            FROM transactions t
            INNER JOIN alerts a ON t.transaction_id = a.transaction_id;
        """)
        flagged_vol_row = cursor.fetchone()
        total_flagged_volume_usd = round(float(flagged_vol_row[0]), 2)

        # 5. Known mules
        cursor.execute("SELECT COUNT(*) FROM beneficiaries WHERE is_known_mule = 1;")
        known_mules_count = cursor.fetchone()[0]

        # 6. Suspicious devices
        cursor.execute("""
            SELECT COUNT(*) FROM devices 
            WHERE trust_status = 'Suspicious_Blacklisted' 
               OR is_vpn_or_tor = 1 
               OR is_rooted_jailbroken = 1;
        """)
        suspicious_devices_count = cursor.fetchone()[0]

        # 7. Alerts by scenario type
        cursor.execute("SELECT scenario_type, COUNT(*) FROM alerts GROUP BY scenario_type ORDER BY COUNT(*) DESC;")
        alerts_by_scenario = {row[0]: row[1] for row in cursor.fetchall()}

        # 8. Top mule beneficiaries
        cursor.execute("""
            SELECT b.beneficiary_id, b.beneficiary_name, b.institution_name,
                   COUNT(DISTINCT t.customer_id) as unique_senders,
                   COALESCE(SUM(t.amount_usd_equivalent), 0.0) as agg_vol
            FROM beneficiaries b
            JOIN transactions t ON b.beneficiary_id = t.beneficiary_id
            WHERE b.is_known_mule = 1
            GROUP BY b.beneficiary_id
            ORDER BY unique_senders DESC, agg_vol DESC
            LIMIT 5;
        """)
        top_mule_beneficiaries = [
            {
                "beneficiary_id": row[0],
                "beneficiary_name": row[1],
                "routing_channel": row[2],
                "unique_senders": row[3],
                "aggregated_volume_usd": round(float(row[4]), 2)
            }
            for row in cursor.fetchall()
        ]

        return {
            "total_customers": total_customers,
            "total_accounts": total_accounts,
            "total_transactions": total_transactions,
            "total_alerts": total_alerts,
            "total_fraud_signals": total_signals,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "medium_alerts": medium_alerts,
            "low_alerts": low_alerts,
            "alerts_by_status": status_counts,
            "total_volume_usd": total_volume_usd,
            "total_flagged_volume_usd": total_flagged_volume_usd,
            "known_mules_count": known_mules_count,
            "suspicious_devices_count": suspicious_devices_count,
            "alerts_by_scenario": alerts_by_scenario,
            "top_mule_beneficiaries": top_mule_beneficiaries,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
