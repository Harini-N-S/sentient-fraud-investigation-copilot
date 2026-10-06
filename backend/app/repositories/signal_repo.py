"""
Fraud Signal Repository
-----------------------------------------------------------------------------
Data access layer for deterministic fraud signals and rule-level forensic audit trails.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class SignalRepository:
    """Manages database operations for fraud signals."""

    SORT_COLUMNS = {
        "created_at": "fs.created_at",
        "confidence_score": "fs.confidence_score",
        "severity": "CASE fs.severity WHEN 'CRITICAL' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END",
        "signal_id": "fs.signal_id",
        "rule_code": "fs.rule_code"
    }

    @classmethod
    def get_signals(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        rule_code: Optional[str] = None,
        rule_category: Optional[str] = None,
        severity: Optional[str] = None,
        transaction_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        alert_id: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if rule_code:
            conditions.append("fs.rule_code = ?")
            params.append(rule_code.strip())

        if rule_category:
            conditions.append("fs.rule_category = ?")
            params.append(rule_category.strip())

        if severity:
            conditions.append("fs.severity = ?")
            params.append(severity.upper().strip())

        if transaction_id:
            conditions.append("fs.transaction_id = ?")
            params.append(transaction_id.strip())

        if alert_id:
            conditions.append("fs.alert_id = ?")
            params.append(alert_id.strip())

        if customer_id:
            conditions.append("a.customer_id = ?")
            params.append(customer_id.strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        count_sql = f"""
            SELECT COUNT(*) 
            FROM fraud_signals fs
            LEFT JOIN alerts a ON fs.alert_id = a.alert_id
            {where_clause};
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="fs.created_at", default_order=sort_order)

        query_sql = f"""
            SELECT 
                fs.signal_id, fs.alert_id, fs.transaction_id, fs.rule_code,
                fs.rule_name, fs.rule_category, fs.severity, fs.confidence_score,
                fs.signal_description, fs.created_at
            FROM fraud_signals fs
            LEFT JOIN alerts a ON fs.alert_id = a.alert_id
            {where_clause}
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = rows_to_dicts(cursor.fetchall())
        return items, pagination

    @classmethod
    def get_signal_by_id(cls, db: sqlite3.Connection, signal_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # Base signal with joined details
        cursor.execute("""
            SELECT 
                fs.signal_id, fs.alert_id, fs.transaction_id, fs.rule_code,
                fs.rule_name, fs.rule_category, fs.severity, fs.confidence_score,
                fs.signal_description, fs.created_at,
                t.customer_id, c.full_name as customer_name,
                t.amount_usd_equivalent as transaction_amount_usd,
                t.location_city as transaction_city,
                a.severity as alert_severity,
                a.status as alert_status
            FROM fraud_signals fs
            LEFT JOIN transactions t ON fs.transaction_id = t.transaction_id
            LEFT JOIN customers c ON t.customer_id = c.customer_id
            LEFT JOIN alerts a ON fs.alert_id = a.alert_id
            WHERE fs.signal_id = ?;
        """, (signal_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = row_to_dict(row)

        signal_summary = {
            "signal_id": data["signal_id"],
            "alert_id": data["alert_id"],
            "transaction_id": data["transaction_id"],
            "rule_code": data["rule_code"],
            "rule_name": data["rule_name"],
            "rule_category": data["rule_category"],
            "severity": data["severity"],
            "confidence_score": data["confidence_score"],
            "signal_description": data["signal_description"],
            "created_at": data["created_at"]
        }

        return {
            "signal": signal_summary,
            "customer_id": data.get("customer_id"),
            "customer_name": data.get("customer_name"),
            "transaction_amount_usd": data.get("transaction_amount_usd"),
            "transaction_city": data.get("transaction_city"),
            "alert_severity": data.get("alert_severity"),
            "alert_status": data.get("alert_status"),
            "calculated_values": {
                "rule_code": data["rule_code"],
                "confidence_score": data["confidence_score"],
                "severity": data["severity"]
            },
            "evidence": {
                "description": data["signal_description"],
                "rule_category": data["rule_category"]
            }
        }
