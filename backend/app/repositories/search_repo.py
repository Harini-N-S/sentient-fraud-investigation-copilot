"""
Search Repository
-----------------------------------------------------------------------------
Deterministic multi-entity search engine powered by parameterized SQL.
Zero LLM hallucination. Fast, index-aware lookups across all primary entities.
"""

import sqlite3
from typing import Dict, Any, List


class SearchRepository:
    """Performs unified deterministic multi-entity search across the synthetic bank database."""

    @classmethod
    def search_all(cls, db: sqlite3.Connection, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        q = query.strip()
        if not q:
            return []

        pattern = f"%{q}%"
        results: List[Dict[str, Any]] = []
        cursor = db.cursor()

        # 1. Search Customers (ID, full_name, phone, email)
        cursor.execute("""
            SELECT customer_id, full_name, customer_segment, registered_city, primary_phone, email
            FROM customers
            WHERE customer_id LIKE ? OR full_name LIKE ? OR primary_phone LIKE ? OR email LIKE ?
            LIMIT 10;
        """, (pattern, pattern, pattern, pattern))
        for r in cursor.fetchall():
            cid, name, seg, city, phone, email = r
            match_field = "customer_id" if q.lower() in cid.lower() else (
                "full_name" if q.lower() in name.lower() else (
                    "primary_phone" if q.lower() in phone.lower() else "email"
                )
            )
            match_val = cid if match_field == "customer_id" else (
                name if match_field == "full_name" else (
                    phone if match_field == "primary_phone" else email
                )
            )
            results.append({
                "entity_type": "customer",
                "entity_id": cid,
                "title": name,
                "subtitle": f"{seg} • {city}",
                "match_field": match_field,
                "match_value": match_val,
                "details": {"segment": seg, "city": city, "phone": phone, "email": email}
            })

        # 2. Search Accounts (account_id)
        cursor.execute("""
            SELECT acc.account_id, acc.account_type, acc.currency, acc.current_balance, c.full_name
            FROM accounts acc
            JOIN customers c ON acc.customer_id = c.customer_id
            WHERE acc.account_id LIKE ?
            LIMIT 10;
        """, (pattern,))
        for r in cursor.fetchall():
            acc_id, acc_type, curr, bal, cname = r
            results.append({
                "entity_type": "account",
                "entity_id": acc_id,
                "title": f"{acc_type} ({curr})",
                "subtitle": f"Owner: {cname} • Balance: {bal:,.2f} {curr}",
                "match_field": "account_id",
                "match_value": acc_id,
                "details": {"currency": curr, "balance": bal, "owner": cname}
            })

        # 3. Search Transactions (transaction_id, location_city)
        cursor.execute("""
            SELECT t.transaction_id, t.amount, t.currency, t.amount_usd_equivalent, t.timestamp, c.full_name, t.channel
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            WHERE t.transaction_id LIKE ?
            LIMIT 10;
        """, (pattern,))
        for r in cursor.fetchall():
            tid, amt, curr, usd, ts, cname, ch = r
            results.append({
                "entity_type": "transaction",
                "entity_id": tid,
                "title": f"Transfer {amt:,.2f} {curr} (${usd:,.2f} USD)",
                "subtitle": f"{cname} via {ch} • {ts}",
                "match_field": "transaction_id",
                "match_value": tid,
                "details": {"amount_usd": usd, "timestamp": ts, "channel": ch}
            })

        # 4. Search Devices (device_id, device_model, ip_address, ip_city)
        cursor.execute("""
            SELECT device_id, device_model, device_type, ip_address, ip_city, trust_status
            FROM devices
            WHERE device_id LIKE ? OR device_model LIKE ? OR ip_address LIKE ? OR ip_city LIKE ?
            LIMIT 10;
        """, (pattern, pattern, pattern, pattern))
        for r in cursor.fetchall():
            did, model, dtype, ip, city, trust = r
            match_field = "device_id" if q.lower() in did.lower() else (
                "device_model" if q.lower() in model.lower() else (
                    "ip_address" if q.lower() in ip.lower() else "ip_city"
                )
            )
            match_val = did if match_field == "device_id" else (
                model if match_field == "device_model" else (
                    ip if match_field == "ip_address" else city
                )
            )
            results.append({
                "entity_type": "device",
                "entity_id": did,
                "title": model,
                "subtitle": f"{dtype} • {city} ({trust})",
                "match_field": match_field,
                "match_value": match_val,
                "details": {"trust_status": trust, "ip": ip, "city": city}
            })

        # 5. Search Beneficiaries (beneficiary_id, beneficiary_name, institution_name, account_or_phone)
        cursor.execute("""
            SELECT beneficiary_id, beneficiary_name, institution_name, beneficiary_type, registered_city, is_known_mule
            FROM beneficiaries
            WHERE beneficiary_id LIKE ? OR beneficiary_name LIKE ? OR institution_name LIKE ? OR account_or_phone LIKE ?
            LIMIT 10;
        """, (pattern, pattern, pattern, pattern))
        for r in cursor.fetchall():
            bid, name, inst, btype, city, mule = r
            match_field = "beneficiary_id" if q.lower() in bid.lower() else (
                "beneficiary_name" if q.lower() in name.lower() else (
                    "institution_name" if q.lower() in inst.lower() else "account_or_phone"
                )
            )
            match_val = bid if match_field == "beneficiary_id" else (
                name if match_field == "beneficiary_name" else inst
            )
            results.append({
                "entity_type": "beneficiary",
                "entity_id": bid,
                "title": name,
                "subtitle": f"{inst} • {btype}{' [KNOWN MULE]' if mule else ''}",
                "match_field": match_field,
                "match_value": match_val,
                "details": {"institution": inst, "is_known_mule": mule, "city": city}
            })

        # 6. Search Alerts (alert_id, scenario_type, reason_summary)
        cursor.execute("""
            SELECT a.alert_id, a.severity, a.composite_risk_score, a.scenario_type, a.reason_summary, c.full_name
            FROM alerts a
            JOIN customers c ON a.customer_id = c.customer_id
            WHERE a.alert_id LIKE ? OR a.scenario_type LIKE ? OR a.reason_summary LIKE ?
            LIMIT 10;
        """, (pattern, pattern, pattern))
        for r in cursor.fetchall():
            aid, sev, score, scen, reason, cname = r
            match_field = "alert_id" if q.lower() in aid.lower() else (
                "scenario_type" if q.lower() in scen.lower() else "reason_summary"
            )
            match_val = aid if match_field == "alert_id" else (
                scen if match_field == "scenario_type" else reason[:50]
            )
            results.append({
                "entity_type": "alert",
                "entity_id": aid,
                "title": f"Alert {aid} [{sev}] ({score}/100)",
                "subtitle": f"{cname}: {scen}",
                "match_field": match_field,
                "match_value": match_val,
                "details": {"severity": sev, "risk_score": score, "scenario": scen}
            })

        # Prioritize exact ID matches first, then prefix matches, then substring matches
        def sort_priority(item: Dict[str, Any]) -> int:
            if item["entity_id"].lower() == q.lower():
                return 0
            if item["entity_id"].lower().startswith(q.lower()):
                return 1
            if q.lower() in item["title"].lower():
                return 2
            return 3

        results.sort(key=sort_priority)
        return results[:limit]
