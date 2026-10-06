"""
Alert Repository
-----------------------------------------------------------------------------
Data access layer for fraud alerts, supporting safe filtering, pagination, and detailed dossier assembly.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.repositories.base import row_to_dict, rows_to_dicts, calculate_pagination, sanitize_sort
from backend.app.schemas.common import PaginationMetadata


class AlertRepository:
    """Manages database operations for fraud alerts."""

    SORT_COLUMNS = {
        "created_at": "a.created_at",
        "composite_risk_score": "a.composite_risk_score",
        "risk_score": "a.composite_risk_score",
        "severity": "CASE a.severity WHEN 'CRITICAL' THEN 4 WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 ELSE 1 END",
        "customer_id": "a.customer_id",
        "alert_id": "a.alert_id"
    }

    @classmethod
    def get_alerts(
        cls,
        db: sqlite3.Connection,
        page: int = 1,
        page_size: int = 25,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        customer_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        rule_category: Optional[str] = None,
        rule_code: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "DESC"
    ) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        cursor = db.cursor()
        conditions: List[str] = []
        params: List[Any] = []

        if severity:
            conditions.append("a.severity = ?")
            params.append(severity.upper().strip())

        if status:
            conditions.append("a.status = ?")
            params.append(status.strip())

        if customer_id:
            conditions.append("a.customer_id = ?")
            params.append(customer_id.strip())

        if transaction_id:
            conditions.append("a.transaction_id = ?")
            params.append(transaction_id.strip())

        if date_from:
            conditions.append("a.created_at >= ?")
            params.append(date_from.strip())

        if date_to:
            conditions.append("a.created_at <= ?")
            params.append(date_to.strip())

        if rule_code or rule_category:
            subquery = "EXISTS (SELECT 1 FROM fraud_signals fs WHERE fs.alert_id = a.alert_id"
            if rule_code:
                subquery += " AND fs.rule_code = ?"
                params.append(rule_code.strip())
            if rule_category:
                subquery += " AND fs.rule_category = ?"
                params.append(rule_category.strip())
            subquery += ")"
            conditions.append(subquery)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Count total
        count_sql = f"SELECT COUNT(*) FROM alerts a {where_clause};"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        pagination = calculate_pagination(page, page_size, total)
        offset = (pagination.page - 1) * pagination.page_size

        sort_col, direction = sanitize_sort(sort_by, cls.SORT_COLUMNS, default_col="a.created_at", default_order=sort_order)

        query_sql = f"""
            SELECT 
                a.alert_id, a.transaction_id, a.customer_id, a.account_id,
                a.severity, a.composite_risk_score, a.status, a.reason_summary,
                a.scenario_type, a.assigned_analyst, a.created_at,
                c.full_name as customer_name,
                t.amount_usd_equivalent as transaction_amount_usd,
                (SELECT COUNT(*) FROM fraud_signals fs WHERE fs.alert_id = a.alert_id) as signal_count
            FROM alerts a
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
            {where_clause}
            ORDER BY {sort_col} {direction}
            LIMIT ? OFFSET ?;
        """
        cursor.execute(query_sql, params + [pagination.page_size, offset])
        items = rows_to_dicts(cursor.fetchall())
        return items, pagination

    @classmethod
    def get_alert_by_id(cls, db: sqlite3.Connection, alert_id: str) -> Optional[Dict[str, Any]]:
        cursor = db.cursor()

        # 1. Alert with customer & transaction join
        cursor.execute("""
            SELECT 
                a.alert_id, a.transaction_id, a.customer_id, a.account_id,
                a.severity, a.composite_risk_score, a.status, a.reason_summary,
                a.scenario_type, a.assigned_analyst, a.created_at,
                c.full_name as customer_name,
                t.amount_usd_equivalent as transaction_amount_usd,
                (SELECT COUNT(*) FROM fraud_signals fs WHERE fs.alert_id = a.alert_id) as signal_count
            FROM alerts a
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
            WHERE a.alert_id = ?;
        """, (alert_id,))
        alert_row = cursor.fetchone()
        if not alert_row:
            return None
        alert_summary = row_to_dict(alert_row)

        # 2. Customer Profile
        cursor.execute("""
            SELECT customer_id, full_name, customer_segment, kyc_status, primary_phone, email, registered_city, risk_category, created_at
            FROM customers WHERE customer_id = ?;
        """, (alert_summary["customer_id"],))
        cust_row = cursor.fetchone()
        customer = row_to_dict(cust_row) if cust_row else {}

        # 3. Source Account
        cursor.execute("""
            SELECT account_id, customer_id, account_type, currency, current_balance, available_balance, account_status, created_at
            FROM accounts WHERE account_id = ?;
        """, (alert_summary["account_id"],))
        acc_row = cursor.fetchone()
        account = row_to_dict(acc_row) if acc_row else {}

        # 4. Triggering Transaction
        cursor.execute("""
            SELECT t.*, b.beneficiary_name, b.institution_name as beneficiary_institution,
                   d.device_model, d.ip_address, d.ip_city, d.trust_status as device_trust_status
            FROM transactions t
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            LEFT JOIN devices d ON t.device_id = d.device_id
            WHERE t.transaction_id = ?;
        """, (alert_summary["transaction_id"],))
        tx_row = cursor.fetchone()
        transaction = row_to_dict(tx_row) if tx_row else {}

        # 5. Linked Fraud Signals
        cursor.execute("""
            SELECT signal_id, alert_id, transaction_id, rule_code, rule_name, rule_category, severity, confidence_score, signal_description, created_at
            FROM fraud_signals
            WHERE alert_id = ?
            ORDER BY confidence_score DESC, created_at ASC;
        """, (alert_id,))
        signals = rows_to_dicts(cursor.fetchall())

        # 6. Related Entities (Device & Beneficiary)
        related_entities = []
        if transaction.get("device_id"):
            related_entities.append({
                "entity_type": "device",
                "entity_id": transaction["device_id"],
                "model": transaction.get("device_model"),
                "ip_city": transaction.get("ip_city"),
                "trust_status": transaction.get("device_trust_status")
            })
        if transaction.get("beneficiary_id"):
            related_entities.append({
                "entity_type": "beneficiary",
                "entity_id": transaction["beneficiary_id"],
                "name": transaction.get("beneficiary_name"),
                "institution": transaction.get("beneficiary_institution")
            })

        return {
            "alert": alert_summary,
            "customer": customer,
            "account": account,
            "transaction": transaction,
            "signals": signals,
            "related_entities": related_entities
        }
