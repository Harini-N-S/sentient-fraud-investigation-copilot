"""
Device Repository
-----------------------------------------------------------------------------
Data access layer for device fingerprinting, fraud cluster tracking, and hardware forensics.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class DeviceRepository:
    """Manages database operations for devices and shared hardware analysis."""

    SORT_COLUMNS = {
        "last_seen_timestamp": "d.last_seen_timestamp",
        "first_seen_timestamp": "d.first_seen_timestamp",
        "device_id": "d.device_id",
        "trust_status": "d.trust_status"
    }

    @classmethod
    def get_devices(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        device_type: Optional[str] = None,
        trust_status: Optional[str] = None,
        is_vpn_or_tor: Optional[int] = None,
        is_rooted_jailbroken: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "last_seen_timestamp",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if device_type:
            conditions.append("d.device_type = ?")
            params.append(device_type.strip())

        if trust_status:
            conditions.append("d.trust_status = ?")
            params.append(trust_status.strip())

        if is_vpn_or_tor is not None:
            conditions.append("d.is_vpn_or_tor = ?")
            params.append(int(is_vpn_or_tor))

        if is_rooted_jailbroken is not None:
            conditions.append("d.is_rooted_jailbroken = ?")
            params.append(int(is_rooted_jailbroken))

        if search:
            s = f"%{search.strip()}%"
            conditions.append("(d.device_id LIKE ? OR d.device_model LIKE ? OR d.ip_address LIKE ? OR d.ip_city LIKE ?)")
            params.extend([s, s, s, s])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_sql = f"SELECT COUNT(*) FROM devices d {where_clause};"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="d.last_seen_timestamp", default_order=sort_order)

        query_sql = f"""
            SELECT 
                d.*,
                (SELECT COUNT(DISTINCT customer_id) FROM transactions WHERE device_id = d.device_id) as associated_customer_count
            FROM devices d
            {where_clause}
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = rows_to_dicts(cursor.fetchall())
        return items, pagination

    @classmethod
    def get_device_detail(cls, db: sqlite3.Connection, device_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # 1. Device base
        cursor.execute("SELECT * FROM devices WHERE device_id = ?;", (device_id,))
        dev_row = cursor.fetchone()
        if not dev_row:
            return None
        device = row_to_dict(dev_row)

        # 2. Associated customers (distinct customers who transacted on this device, plus primary owner)
        cursor.execute("""
            SELECT DISTINCT c.customer_id, c.full_name, c.customer_segment, c.kyc_status, c.registered_city,
                   (CASE WHEN c.customer_id = ? THEN 1 ELSE 0 END) as is_primary_owner,
                   COUNT(t.transaction_id) as transaction_count,
                   COALESCE(SUM(t.amount_usd_equivalent), 0.0) as total_spent_usd
            FROM customers c
            LEFT JOIN transactions t ON c.customer_id = t.customer_id AND t.device_id = ?
            WHERE c.customer_id = ?
               OR c.customer_id IN (SELECT DISTINCT customer_id FROM transactions WHERE device_id = ?)
            GROUP BY c.customer_id
            ORDER BY is_primary_owner DESC, transaction_count DESC;
        """, (device["primary_customer_id"], device_id, device["primary_customer_id"], device_id))
        associated_customers = rows_to_dicts(cursor.fetchall())

        # 3. Transaction metrics
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount_usd_equivalent), 0.0)
            FROM transactions 
            WHERE device_id = ?;
        """, (device_id,))
        tx_stats = cursor.fetchone()
        transaction_count = tx_stats[0]
        total_volume_usd = round(float(tx_stats[1]), 2)

        # 4. Recent transactions
        cursor.execute("""
            SELECT t.*, c.full_name as customer_name, b.beneficiary_name
            FROM transactions t
            LEFT JOIN customers c ON t.customer_id = c.customer_id
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.device_id = ?
            ORDER BY t.timestamp DESC 
            LIMIT 10;
        """, (device_id,))
        recent_transactions = rows_to_dicts(cursor.fetchall())

        # 5. Recent auth activity
        cursor.execute("""
            SELECT a.*, c.full_name as customer_name
            FROM auth_activities a
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            WHERE a.device_id = ?
            ORDER BY a.timestamp DESC 
            LIMIT 10;
        """, (device_id,))
        recent_auth_activity = rows_to_dicts(cursor.fetchall())

        # 6. Related alerts
        cursor.execute("""
            SELECT DISTINCT a.*, c.full_name as customer_name
            FROM alerts a
            INNER JOIN transactions t ON a.transaction_id = t.transaction_id
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            WHERE t.device_id = ?
            ORDER BY a.composite_risk_score DESC, a.created_at DESC;
        """, (device_id,))
        related_alerts = rows_to_dicts(cursor.fetchall())

        # 7. Related signals
        cursor.execute("""
            SELECT DISTINCT fs.*
            FROM fraud_signals fs
            INNER JOIN transactions t ON fs.transaction_id = t.transaction_id
            WHERE t.device_id = ?
            ORDER BY fs.confidence_score DESC;
        """, (device_id,))
        related_signals = rows_to_dicts(cursor.fetchall())

        return {
            "device": device,
            "associated_customers": associated_customers,
            "transaction_count": transaction_count,
            "total_volume_usd": total_volume_usd,
            "recent_transactions": recent_transactions,
            "recent_auth_activity": recent_auth_activity,
            "related_alerts": related_alerts,
            "related_signals": related_signals
        }
