"""
Customer Repository
-----------------------------------------------------------------------------
Data access layer for customer profiles and full 360-degree forensic dossiers.
Zero AI hallucination. Pure deterministic relational assembly.
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class CustomerRepository:
    """Manages database operations for customer records and dossiers."""

    SORT_COLUMNS = {
        "created_at": "c.created_at",
        "full_name": "c.full_name",
        "customer_id": "c.customer_id",
        "registered_city": "c.registered_city",
        "risk_category": "CASE c.risk_category WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END"
    }

    @classmethod
    def get_customers(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        search: Optional[str] = None,
        segment: Optional[str] = None,
        kyc_status: Optional[str] = None,
        risk_category: Optional[str] = None,
        registered_city: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if search:
            s = f"%{search.strip()}%"
            conditions.append("(c.customer_id LIKE ? OR c.full_name LIKE ? OR c.email LIKE ? OR c.primary_phone LIKE ?)")
            params.extend([s, s, s, s])

        if segment:
            conditions.append("c.customer_segment = ? COLLATE NOCASE")
            params.append(segment.strip())

        if kyc_status:
            conditions.append("c.kyc_status = ? COLLATE NOCASE")
            params.append(kyc_status.strip())

        if risk_category:
            conditions.append("c.risk_category = ? COLLATE NOCASE")
            params.append(risk_category.strip())

        if registered_city:
            conditions.append("c.registered_city = ? COLLATE NOCASE")
            params.append(registered_city.strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Count
        count_sql = f"SELECT COUNT(*) FROM customers c {where_clause};"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="c.created_at", default_order=sort_order)

        query_sql = f"""
            SELECT 
                c.customer_id, c.full_name, c.customer_segment, c.kyc_status,
                c.primary_phone, c.email, c.registered_city, c.risk_category, c.created_at,
                COUNT(DISTINCT acc.account_id) as account_count,
                COALESCE(SUM(CASE WHEN acc.currency = 'USD' THEN acc.current_balance ELSE acc.current_balance / 2750.0 END), 0.0) as total_balance_usd
            FROM customers c
            LEFT JOIN accounts acc ON c.customer_id = acc.customer_id
            {where_clause}
            GROUP BY c.customer_id
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = []
        for r in cursor.fetchall():
            d = row_to_dict(r)
            d["total_balance_usd"] = round(float(d.get("total_balance_usd", 0.0)), 2)
            d["registration_date"] = d.get("created_at")
            d["is_active"] = True
            items.append(d)

        return items, pagination

    @classmethod
    def get_customer_dossier(cls, db: sqlite3.Connection, customer_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # 1. Customer
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?;", (customer_id,))
        cust_row = cursor.fetchone()
        if not cust_row:
            return None
        customer = row_to_dict(cust_row)
        customer["registration_date"] = customer.get("created_at")
        customer["is_active"] = True

        # 2. Accounts
        cursor.execute("SELECT * FROM accounts WHERE customer_id = ? ORDER BY created_at ASC;", (customer_id,))
        accounts = rows_to_dicts(cursor.fetchall())
        total_balance_usd = sum(
            acc["current_balance"] if acc["currency"] == "USD" else acc["current_balance"] / 2750.0
            for acc in accounts
        )
        customer["account_count"] = len(accounts)
        customer["total_balance_usd"] = round(total_balance_usd, 2)

        # 3. Transaction Summary
        cursor.execute("""
            SELECT 
                COUNT(*) as tx_count,
                COALESCE(SUM(amount_usd_equivalent), 0.0) as total_volume_usd,
                COALESCE(AVG(amount_usd_equivalent), 0.0) as avg_volume_usd,
                COALESCE(MAX(amount_usd_equivalent), 0.0) as max_volume_usd
            FROM transactions 
            WHERE customer_id = ?;
        """, (customer_id,))
        summary_row = cursor.fetchone()
        activity_summary = {
            "lifetime_transaction_count": summary_row[0],
            "lifetime_volume_usd": round(float(summary_row[1]), 2),
            "average_transaction_usd": round(float(summary_row[2]), 2),
            "max_single_transaction_usd": round(float(summary_row[3]), 2)
        }

        # 4. Recent Transactions (last 10)
        cursor.execute("""
            SELECT t.*, b.beneficiary_name 
            FROM transactions t
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.customer_id = ?
            ORDER BY t.timestamp DESC 
            LIMIT 10;
        """, (customer_id,))
        recent_transactions = rows_to_dicts(cursor.fetchall())

        # 5. Behavioural Baseline
        cursor.execute("SELECT * FROM behavioural_baselines WHERE customer_id = ?;", (customer_id,))
        baseline_row = cursor.fetchone()
        behavioural_baseline = row_to_dict(baseline_row) if baseline_row else None
        if behavioural_baseline:
            # Parse json / comma fields for frontend convenience
            for k in ["typical_active_hours_utc", "common_channels", "frequent_beneficiary_ids", "frequent_cities"]:
                val = behavioural_baseline.get(k)
                if isinstance(val, str) and (val.startswith("[") or "," in val):
                    try:
                        behavioural_baseline[f"{k}_list"] = json.loads(val) if val.startswith("[") else [x.strip() for x in val.split(",")]
                    except Exception:
                        pass

        # 6. Devices (owned or used)
        cursor.execute("""
            SELECT DISTINCT d.* 
            FROM devices d
            WHERE d.primary_customer_id = ?
               OR d.device_id IN (SELECT DISTINCT device_id FROM transactions WHERE customer_id = ?)
            ORDER BY d.last_seen_timestamp DESC;
        """, (customer_id, customer_id))
        devices = rows_to_dicts(cursor.fetchall())

        # 7. Beneficiaries
        cursor.execute("""
            SELECT DISTINCT b.*, COUNT(t.transaction_id) as send_count, SUM(t.amount_usd_equivalent) as total_sent_usd
            FROM beneficiaries b
            INNER JOIN transactions t ON b.beneficiary_id = t.beneficiary_id
            WHERE t.customer_id = ?
            GROUP BY b.beneficiary_id
            ORDER BY total_sent_usd DESC;
        """, (customer_id,))
        beneficiaries = rows_to_dicts(cursor.fetchall())

        # 8. Recent Authentication Events
        cursor.execute("""
            SELECT a.*, d.device_model 
            FROM auth_activities a
            LEFT JOIN devices d ON a.device_id = d.device_id
            WHERE a.customer_id = ?
            ORDER BY a.timestamp DESC 
            LIMIT 10;
        """, (customer_id,))
        recent_auth_events = rows_to_dicts(cursor.fetchall())

        # 9. Risk Information (Alerts and Signals)
        cursor.execute("""
            SELECT a.*, COUNT(fs.signal_id) as signal_count 
            FROM alerts a
            LEFT JOIN fraud_signals fs ON a.alert_id = fs.alert_id
            WHERE a.customer_id = ?
            GROUP BY a.alert_id
            ORDER BY a.composite_risk_score DESC, a.created_at DESC;
        """, (customer_id,))
        alerts = rows_to_dicts(cursor.fetchall())

        cursor.execute("""
            SELECT fs.*, a.severity as alert_severity 
            FROM fraud_signals fs
            INNER JOIN alerts a ON fs.alert_id = a.alert_id
            WHERE a.customer_id = ?
            ORDER BY fs.confidence_score DESC, fs.created_at DESC;
        """, (customer_id,))
        signals = rows_to_dicts(cursor.fetchall())

        highest_risk_score = max([a["composite_risk_score"] for a in alerts], default=0)
        risk = {
            "total_alerts": len(alerts),
            "highest_risk_score": highest_risk_score,
            "alerts": alerts,
            "fraud_signals": signals,
            "has_critical_alert": any(a["severity"] == "CRITICAL" for a in alerts),
            "has_high_alert": any(a["severity"] == "HIGH" for a in alerts)
        }

        # 10. Relationships: Shared Devices & Shared Beneficiaries
        # Shared Devices: devices used by this customer that were also used by other customers
        cursor.execute("""
            SELECT DISTINCT d.device_id, d.device_model, t.customer_id as other_customer_id, c.full_name as other_customer_name
            FROM transactions t
            JOIN devices d ON t.device_id = d.device_id
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.device_id IN (
                SELECT DISTINCT device_id FROM transactions WHERE customer_id = ?
            )
            AND t.customer_id != ?;
        """, (customer_id, customer_id))
        shared_devices = rows_to_dicts(cursor.fetchall())

        # Shared Beneficiaries: beneficiaries sent to by this customer that were also sent to by other customers
        cursor.execute("""
            SELECT DISTINCT b.beneficiary_id, b.beneficiary_name, b.is_known_mule,
                   t.customer_id as other_customer_id, c.full_name as other_customer_name
            FROM transactions t
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.beneficiary_id IN (
                SELECT DISTINCT beneficiary_id FROM transactions WHERE customer_id = ?
            )
            AND t.customer_id != ?
            LIMIT 20;
        """, (customer_id, customer_id))
        shared_beneficiaries = rows_to_dicts(cursor.fetchall())

        relationships = {
            "shared_devices_count": len(shared_devices),
            "shared_devices": shared_devices,
            "shared_beneficiaries_count": len(shared_beneficiaries),
            "shared_beneficiaries": shared_beneficiaries
        }

        return {
            "customer": customer,
            "accounts": accounts,
            "activity_summary": activity_summary,
            "recent_transactions": recent_transactions,
            "behavioural_baseline": behavioural_baseline,
            "devices": devices,
            "beneficiaries": beneficiaries,
            "recent_auth_events": recent_auth_events,
            "risk": risk,
            "relationships": relationships
        }
