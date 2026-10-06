"""
Transaction Repository
-----------------------------------------------------------------------------
Data access layer for transactions with multi-field filtering, pagination, and relational assembly.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class TransactionRepository:
    """Manages database operations for financial transactions."""

    SORT_COLUMNS = {
        "timestamp": "t.timestamp",
        "amount_usd": "t.amount_usd_equivalent",
        "amount_usd_equivalent": "t.amount_usd_equivalent",
        "amount": "t.amount",
        "transaction_id": "t.transaction_id"
    }

    CHANNEL_MAPPING = {
        "MOBILE_APP": "IllicoCash_App",
        "MOBILE BANKING APP": "IllicoCash_App",
        "ONLINE_BANKING": "RawbankOnline_Web",
        "ONLINE BANKING": "RawbankOnline_Web",
        "WEB PORTAL": "RawbankOnline_Web",
        "WEB_PORTAL": "RawbankOnline_Web",
        "AGENCY_BANKING": "Agency_Express_POS",
        "AGENCY BANKING": "Agency_Express_POS",
        "ATM": "ATM_Cardless",
        "ATM TERMINAL": "ATM_Cardless",
        "ATM_TERMINAL": "ATM_Cardless",
        "ATM / CARDLESS": "ATM_Cardless",
        "ATM_CARDLESS": "ATM_Cardless",
        "ILLICOCASH_APP": "IllicoCash_App",
        "ILLICOCASH": "IllicoCash_App",
        "RAWBANKONLINE_WEB": "RawbankOnline_Web",
        "RAWBANKONLINE": "RawbankOnline_Web",
        "AGENCY_EXPRESS_POS": "Agency_Express_POS",
    }

    @classmethod
    def get_transactions(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        customer_id: Optional[str] = None,
        account_id: Optional[str] = None,
        beneficiary_id: Optional[str] = None,
        device_id: Optional[str] = None,
        channel: Optional[str] = None,
        transaction_type: Optional[str] = None,
        currency: Optional[str] = None,
        location_city: Optional[str] = None,
        status: Optional[str] = None,
        min_amount_usd: Optional[float] = None,
        max_amount_usd: Optional[float] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "timestamp",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if customer_id:
            conditions.append("t.customer_id = ?")
            params.append(customer_id.strip())

        if account_id:
            conditions.append("t.account_id = ?")
            params.append(account_id.strip())

        if beneficiary_id:
            conditions.append("t.beneficiary_id = ?")
            params.append(beneficiary_id.strip())

        if device_id:
            conditions.append("t.device_id = ?")
            params.append(device_id.strip())

        if channel:
            c_clean = channel.strip()
            resolved_channel = cls.CHANNEL_MAPPING.get(c_clean.upper().replace("-", "_"), c_clean)
            if resolved_channel.upper() not in {"ALL", "ALL CHANNELS", "ALL_CHANNELS", ""}:
                conditions.append("t.channel = ?")
                params.append(resolved_channel)

        if transaction_type:
            conditions.append("t.transaction_type = ?")
            params.append(transaction_type.strip())

        if currency:
            c_upper = currency.upper().strip()
            if c_upper not in {"CDF & USD", "CDF/USD", "CDF,USD", "ALL", "BOTH", ""}:
                conditions.append("t.currency = ?")
                params.append(c_upper)

        if location_city:
            conditions.append("t.location_city LIKE ?")
            params.append(f"%{location_city.strip()}%")

        if status:
            conditions.append("t.status = ?")
            params.append(status.strip())

        if min_amount_usd is not None:
            conditions.append("t.amount_usd_equivalent >= ?")
            params.append(float(min_amount_usd))

        if max_amount_usd is not None:
            conditions.append("t.amount_usd_equivalent <= ?")
            params.append(float(max_amount_usd))

        if date_from:
            conditions.append("t.timestamp >= ?")
            params.append(date_from.strip())

        if date_to:
            conditions.append("t.timestamp <= ?")
            params.append(date_to.strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Count total
        count_sql = f"SELECT COUNT(*) FROM transactions t {where_clause};"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="t.timestamp", default_order=sort_order)

        query_sql = f"""
            SELECT 
                t.transaction_id, t.account_id, t.customer_id, t.beneficiary_id, t.device_id,
                t.channel, t.transaction_type, t.amount, t.currency, t.amount_usd_equivalent,
                t.location_city, t.status, t.timestamp,
                c.full_name as customer_name,
                b.beneficiary_name as beneficiary_name
            FROM transactions t
            LEFT JOIN customers c ON t.customer_id = c.customer_id
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            {where_clause}
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = rows_to_dicts(cursor.fetchall())
        return items, pagination

    @classmethod
    def get_transaction_by_id(cls, db: sqlite3.Connection, transaction_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # 1. Base transaction
        cursor.execute("""
            SELECT 
                t.transaction_id, t.account_id, t.customer_id, t.beneficiary_id, t.device_id,
                t.channel, t.transaction_type, t.amount, t.currency, t.amount_usd_equivalent,
                t.location_city, t.status, t.timestamp,
                c.full_name as customer_name,
                b.beneficiary_name as beneficiary_name
            FROM transactions t
            LEFT JOIN customers c ON t.customer_id = c.customer_id
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE t.transaction_id = ?;
        """, (transaction_id,))
        tx_row = cursor.fetchone()
        if not tx_row:
            return None
        tx_summary = row_to_dict(tx_row)

        # 2. Customer
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?;", (tx_summary["customer_id"],))
        customer = row_to_dict(cursor.fetchone())

        # 3. Account
        cursor.execute("SELECT * FROM accounts WHERE account_id = ?;", (tx_summary["account_id"],))
        account = row_to_dict(cursor.fetchone())

        # 4. Beneficiary
        cursor.execute("SELECT * FROM beneficiaries WHERE beneficiary_id = ?;", (tx_summary["beneficiary_id"],))
        beneficiary = row_to_dict(cursor.fetchone())

        # 5. Device
        cursor.execute("SELECT * FROM devices WHERE device_id = ?;", (tx_summary["device_id"],))
        device = row_to_dict(cursor.fetchone())

        # 6. Recent auth activity for this customer around the time of transaction
        cursor.execute("""
            SELECT * FROM auth_activities 
            WHERE customer_id = ?
            ORDER BY timestamp DESC 
            LIMIT 5;
        """, (tx_summary["customer_id"],))
        auth_activities = rows_to_dicts(cursor.fetchall())

        # 7. Recorded fraud signals in database
        cursor.execute("""
            SELECT * FROM fraud_signals 
            WHERE transaction_id = ?
            ORDER BY confidence_score DESC;
        """, (transaction_id,))
        signals = rows_to_dicts(cursor.fetchall())

        # 8. Related alerts
        cursor.execute("""
            SELECT * FROM alerts 
            WHERE transaction_id = ?;
        """, (transaction_id,))
        alerts = rows_to_dicts(cursor.fetchall())

        return {
            "transaction": tx_summary,
            "customer": customer,
            "account": account,
            "beneficiary": beneficiary,
            "device": device,
            "recent_auth_activity": auth_activities,
            "fraud_signals": signals,
            "related_alerts": alerts
        }
