"""
Beneficiary Repository
-----------------------------------------------------------------------------
Data access layer for beneficiary entities, mule account tracking, and aggregation metrics.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class BeneficiaryRepository:
    """Manages database operations for beneficiaries and mule network forensics."""

    SORT_COLUMNS = {
        "created_at": "b.created_at",
        "beneficiary_name": "b.beneficiary_name",
        "beneficiary_id": "b.beneficiary_id",
        "total_volume_usd": "COALESCE(SUM(t.amount_usd_equivalent), 0.0)",
        "customer_count": "COUNT(DISTINCT t.customer_id)"
    }

    @classmethod
    def get_beneficiaries(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        beneficiary_type: Optional[str] = None,
        is_known_mule: Optional[int] = None,
        institution_name: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if beneficiary_type:
            conditions.append("b.beneficiary_type = ?")
            params.append(beneficiary_type.strip())

        if is_known_mule is not None:
            conditions.append("b.is_known_mule = ?")
            params.append(int(is_known_mule))

        if institution_name:
            conditions.append("b.institution_name = ?")
            params.append(institution_name.strip())

        if search:
            s = f"%{search.strip()}%"
            conditions.append("(b.beneficiary_id LIKE ? OR b.beneficiary_name LIKE ? OR b.institution_name LIKE ? OR b.account_or_phone LIKE ?)")
            params.extend([s, s, s, s])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_sql = f"SELECT COUNT(*) FROM beneficiaries b {where_clause};"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="b.created_at", default_order=sort_order)

        query_sql = f"""
            SELECT 
                b.*,
                COUNT(DISTINCT t.customer_id) as interacting_customer_count,
                COALESCE(SUM(t.amount_usd_equivalent), 0.0) as total_volume_usd
            FROM beneficiaries b
            LEFT JOIN transactions t ON b.beneficiary_id = t.beneficiary_id
            {where_clause}
            GROUP BY b.beneficiary_id
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = []
        for r in cursor.fetchall():
            d = row_to_dict(r)
            d["total_volume_usd"] = round(float(d.get("total_volume_usd", 0.0)), 2)
            items.append(d)

        return items, pagination

    @classmethod
    def get_beneficiary_detail(cls, db: sqlite3.Connection, beneficiary_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # 1. Beneficiary base
        cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?;", (beneficiary_id,))
        ben_row = cursor.fetchone()
        if not ben_row:
            return None
        beneficiary = row_to_dict(ben_row)

        # 2. Interacting customers
        cursor.execute("""
            SELECT 
                c.customer_id, c.full_name, c.customer_segment, c.registered_city,
                COUNT(t.transaction_id) as send_count,
                COALESCE(SUM(t.amount_usd_equivalent), 0.0) as total_sent_usd,
                MIN(t.timestamp) as first_interaction,
                MAX(t.timestamp) as last_interaction
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.beneficiary_id = ?
            GROUP BY c.customer_id
            ORDER BY total_sent_usd DESC;
        """, (beneficiary_id,))
        interacting_customers = []
        for r in cursor.fetchall():
            d = row_to_dict(r)
            d["total_sent_usd"] = round(float(d.get("total_sent_usd", 0.0)), 2)
            interacting_customers.append(d)

        beneficiary["interacting_customer_count"] = len(interacting_customers)

        # 3. Aggregate metrics
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount_usd_equivalent), 0.0)
            FROM transactions 
            WHERE beneficiary_id = ?;
        """, (beneficiary_id,))
        tx_stats = cursor.fetchone()
        transaction_count = tx_stats[0]
        total_volume_usd = round(float(tx_stats[1]), 2)
        beneficiary["total_volume_usd"] = total_volume_usd

        # 4. Recent transactions
        cursor.execute("""
            SELECT t.*, c.full_name as customer_name
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.beneficiary_id = ?
            ORDER BY t.timestamp DESC 
            LIMIT 10;
        """, (beneficiary_id,))
        recent_transactions = rows_to_dicts(cursor.fetchall())

        # 5. Related alerts
        cursor.execute("""
            SELECT DISTINCT a.*, c.full_name as customer_name
            FROM alerts a
            INNER JOIN transactions t ON a.transaction_id = t.transaction_id
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            WHERE t.beneficiary_id = ?
            ORDER BY a.composite_risk_score DESC, a.created_at DESC;
        """, (beneficiary_id,))
        related_alerts = rows_to_dicts(cursor.fetchall())

        # 6. Related signals
        cursor.execute("""
            SELECT DISTINCT fs.*
            FROM fraud_signals fs
            INNER JOIN transactions t ON fs.transaction_id = t.transaction_id
            WHERE t.beneficiary_id = ?
            ORDER BY fs.confidence_score DESC;
        """, (beneficiary_id,))
        related_signals = rows_to_dicts(cursor.fetchall())

        return {
            "beneficiary": beneficiary,
            "interacting_customers": interacting_customers,
            "transaction_count": transaction_count,
            "total_volume_usd": total_volume_usd,
            "recent_transactions": recent_transactions,
            "related_alerts": related_alerts,
            "related_signals": related_signals
        }
