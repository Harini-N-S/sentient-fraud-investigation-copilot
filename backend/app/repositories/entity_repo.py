"""
Entity Relationship Repository
-----------------------------------------------------------------------------
Graph-style link exploration computed deterministically from relational foreign keys.
Zero fabricated links. All graph nodes and edges derive from actual database records.
"""

import sqlite3
from typing import Dict, Any, List, Optional
from backend.app.repositories.base import row_to_dict, rows_to_dicts


class EntityRepository:
    """Explores 1-hop and 2-hop relational connections across the banking topology."""

    SUPPORTED_TYPES = {"customer", "account", "transaction", "device", "beneficiary", "alert"}

    @classmethod
    def get_entity_relationships(cls, db: sqlite3.Connection, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        entity_type = entity_type.lower().strip()
        if entity_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported entity type: '{entity_type}'. Supported: {sorted(list(cls.SUPPORTED_TYPES))}")

        cursor = db.cursor()
        root_entity = None
        edges: List[Dict[str, Any]] = []
        second_hop_edges: List[Dict[str, Any]] = []

        # ---------------------------------------------------------------------
        # 1. CUSTOMER GRAPH
        # ---------------------------------------------------------------------
        if entity_type == "customer":
            cursor.execute("SELECT customer_id, full_name, customer_segment, registered_city FROM customers WHERE customer_id = ?;", (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Accounts (OWNS)
            cursor.execute("SELECT account_id, account_type, currency, current_balance FROM accounts WHERE customer_id = ?;", (entity_id,))
            for r in cursor.fetchall():
                acc = row_to_dict(r)
                edges.append({
                    "source_type": "customer",
                    "source_id": entity_id,
                    "relationship": "OWNS_ACCOUNT",
                    "target_type": "account",
                    "target_id": acc["account_id"],
                    "target_label": f"{acc['account_type']} ({acc['currency']})",
                    "direction": "outgoing",
                    "details": {"balance": acc["current_balance"]}
                })

            # Devices (USES)
            cursor.execute("""
                SELECT DISTINCT d.device_id, d.device_model, d.trust_status, d.ip_city
                FROM devices d
                WHERE d.primary_customer_id = ?
                   OR d.device_id IN (SELECT DISTINCT device_id FROM transactions WHERE customer_id = ?);
            """, (entity_id, entity_id))
            used_devices = rows_to_dicts(cursor.fetchall())
            for d in used_devices:
                edges.append({
                    "source_type": "customer",
                    "source_id": entity_id,
                    "relationship": "USES_DEVICE",
                    "target_type": "device",
                    "target_id": d["device_id"],
                    "target_label": f"{d['device_model']} ({d['trust_status']})",
                    "direction": "outgoing",
                    "details": {"ip_city": d["ip_city"]}
                })

                # 2nd hop: other customers sharing this device
                cursor.execute("""
                    SELECT DISTINCT c.customer_id, c.full_name, c.customer_segment
                    FROM transactions t
                    JOIN customers c ON t.customer_id = c.customer_id
                    WHERE t.device_id = ? AND t.customer_id != ?;
                """, (d["device_id"], entity_id))
                for other_c in rows_to_dicts(cursor.fetchall()):
                    second_hop_edges.append({
                        "source_type": "device",
                        "source_id": d["device_id"],
                        "relationship": "ALSO_USED_BY",
                        "target_type": "customer",
                        "target_id": other_c["customer_id"],
                        "target_label": f"{other_c['full_name']} ({other_c['customer_segment']})",
                        "direction": "outgoing",
                        "details": {"pivot_device": d["device_model"]}
                    })

            # Beneficiaries (TRANSFERS_TO)
            cursor.execute("""
                SELECT b.beneficiary_id, b.beneficiary_name, b.institution_name, b.is_known_mule,
                       COUNT(t.transaction_id) as tx_count, SUM(t.amount_usd_equivalent) as total_usd
                FROM beneficiaries b
                JOIN transactions t ON b.beneficiary_id = t.beneficiary_id
                WHERE t.customer_id = ?
                GROUP BY b.beneficiary_id
                ORDER BY total_usd DESC
                LIMIT 15;
            """, (entity_id,))
            sent_bens = rows_to_dicts(cursor.fetchall())
            for b in sent_bens:
                edges.append({
                    "source_type": "customer",
                    "source_id": entity_id,
                    "relationship": "TRANSFERS_TO",
                    "target_type": "beneficiary",
                    "target_id": b["beneficiary_id"],
                    "target_label": f"{b['beneficiary_name']} ({b['institution_name']})",
                    "direction": "outgoing",
                    "details": {"tx_count": b["tx_count"], "total_usd": round(b["total_usd"], 2), "is_known_mule": b["is_known_mule"]}
                })

                # 2nd hop: other customers who also sent to this beneficiary
                cursor.execute("""
                    SELECT DISTINCT c.customer_id, c.full_name
                    FROM transactions t
                    JOIN customers c ON t.customer_id = c.customer_id
                    WHERE t.beneficiary_id = ? AND t.customer_id != ?
                    LIMIT 5;
                """, (b["beneficiary_id"], entity_id))
                for other_sender in rows_to_dicts(cursor.fetchall()):
                    second_hop_edges.append({
                        "source_type": "beneficiary",
                        "source_id": b["beneficiary_id"],
                        "relationship": "ALSO_RECEIVES_FROM",
                        "target_type": "customer",
                        "target_id": other_sender["customer_id"],
                        "target_label": other_sender["full_name"],
                        "direction": "incoming",
                        "details": {"pivot_beneficiary": b["beneficiary_name"]}
                    })

            # Alerts (SUBJECT_OF)
            cursor.execute("""
                SELECT alert_id, severity, composite_risk_score, status, scenario_type
                FROM alerts WHERE customer_id = ?;
            """, (entity_id,))
            for a in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "customer",
                    "source_id": entity_id,
                    "relationship": "SUBJECT_OF_ALERT",
                    "target_type": "alert",
                    "target_id": a["alert_id"],
                    "target_label": f"{a['severity']} ({a['composite_risk_score']}/100) - {a['scenario_type']}",
                    "direction": "outgoing",
                    "details": {"status": a["status"]}
                })

        # ---------------------------------------------------------------------
        # 2. ACCOUNT GRAPH
        # ---------------------------------------------------------------------
        elif entity_type == "account":
            cursor.execute("SELECT account_id, customer_id, account_type, currency, current_balance, account_status FROM accounts WHERE account_id = ?;", (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Customer (HELD_BY)
            cursor.execute("SELECT customer_id, full_name, customer_segment FROM customers WHERE customer_id = ?;", (root_entity["customer_id"],))
            owner = row_to_dict(cursor.fetchone())
            edges.append({
                "source_type": "account",
                "source_id": entity_id,
                "relationship": "HELD_BY_CUSTOMER",
                "target_type": "customer",
                "target_id": owner["customer_id"],
                "target_label": owner["full_name"],
                "direction": "incoming",
                "details": {"segment": owner["customer_segment"]}
            })

            # Transactions (DEBITED_BY)
            cursor.execute("""
                SELECT transaction_id, amount_usd_equivalent, timestamp, status, beneficiary_id
                FROM transactions WHERE account_id = ?
                ORDER BY timestamp DESC LIMIT 10;
            """, (entity_id,))
            for tx in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "account",
                    "source_id": entity_id,
                    "relationship": "DEBITED_BY_TXN",
                    "target_type": "transaction",
                    "target_id": tx["transaction_id"],
                    "target_label": f"${tx['amount_usd_equivalent']} USD ({tx['status']})",
                    "direction": "outgoing",
                    "details": {"timestamp": tx["timestamp"]}
                })

            # Alerts
            cursor.execute("SELECT alert_id, severity, composite_risk_score FROM alerts WHERE account_id = ?;", (entity_id,))
            for a in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "account",
                    "source_id": entity_id,
                    "relationship": "FLAGGED_ON_ALERT",
                    "target_type": "alert",
                    "target_id": a["alert_id"],
                    "target_label": f"{a['severity']} ({a['composite_risk_score']})",
                    "direction": "outgoing",
                    "details": {}
                })

        # ---------------------------------------------------------------------
        # 3. TRANSACTION GRAPH
        # ---------------------------------------------------------------------
        elif entity_type == "transaction":
            cursor.execute("""
                SELECT t.*, c.full_name as cust_name, b.beneficiary_name as ben_name, d.device_model as dev_name
                FROM transactions t
                LEFT JOIN customers c ON t.customer_id = c.customer_id
                LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
                LEFT JOIN devices d ON t.device_id = d.device_id
                WHERE t.transaction_id = ?;
            """, (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Customer
            edges.append({
                "source_type": "transaction",
                "source_id": entity_id,
                "relationship": "INITIATED_BY",
                "target_type": "customer",
                "target_id": root_entity["customer_id"],
                "target_label": root_entity.get("cust_name", root_entity["customer_id"]),
                "direction": "incoming",
                "details": {}
            })

            # Account
            edges.append({
                "source_type": "transaction",
                "source_id": entity_id,
                "relationship": "DRAWN_FROM",
                "target_type": "account",
                "target_id": root_entity["account_id"],
                "target_label": root_entity["account_id"],
                "direction": "incoming",
                "details": {}
            })

            # Beneficiary
            edges.append({
                "source_type": "transaction",
                "source_id": entity_id,
                "relationship": "PAID_TO",
                "target_type": "beneficiary",
                "target_id": root_entity["beneficiary_id"],
                "target_label": root_entity.get("ben_name", root_entity["beneficiary_id"]),
                "direction": "outgoing",
                "details": {"amount_usd": root_entity["amount_usd_equivalent"]}
            })

            # Device
            edges.append({
                "source_type": "transaction",
                "source_id": entity_id,
                "relationship": "ORIGINATED_AT",
                "target_type": "device",
                "target_id": root_entity["device_id"],
                "target_label": root_entity.get("dev_name", root_entity["device_id"]),
                "direction": "incoming",
                "details": {"city": root_entity["location_city"]}
            })

            # Alerts
            cursor.execute("SELECT alert_id, severity, composite_risk_score FROM alerts WHERE transaction_id = ?;", (entity_id,))
            for a in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "transaction",
                    "source_id": entity_id,
                    "relationship": "TRIGGERED_ALERT",
                    "target_type": "alert",
                    "target_id": a["alert_id"],
                    "target_label": f"{a['severity']} ({a['composite_risk_score']})",
                    "direction": "outgoing",
                    "details": {}
                })

        # ---------------------------------------------------------------------
        # 4. DEVICE GRAPH
        # ---------------------------------------------------------------------
        elif entity_type == "device":
            cursor.execute("SELECT device_id, primary_customer_id, device_model, trust_status, ip_address, ip_city FROM devices WHERE device_id = ?;", (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Primary owner
            cursor.execute("SELECT customer_id, full_name FROM customers WHERE customer_id = ?;", (root_entity["primary_customer_id"],))
            owner = row_to_dict(cursor.fetchone())
            edges.append({
                "source_type": "device",
                "source_id": entity_id,
                "relationship": "REGISTERED_TO",
                "target_type": "customer",
                "target_id": owner["customer_id"],
                "target_label": f"{owner['full_name']} (Primary Owner)",
                "direction": "incoming",
                "details": {}
            })

            # All distinct customers who transacted on this device
            cursor.execute("""
                SELECT DISTINCT c.customer_id, c.full_name, COUNT(t.transaction_id) as tx_count,
                       SUM(t.amount_usd_equivalent) as total_usd
                FROM transactions t
                JOIN customers c ON t.customer_id = c.customer_id
                WHERE t.device_id = ?
                GROUP BY c.customer_id;
            """, (entity_id,))
            for u in rows_to_dicts(cursor.fetchall()):
                if u["customer_id"] != root_entity["primary_customer_id"]:
                    edges.append({
                        "source_type": "device",
                        "source_id": entity_id,
                        "relationship": "SHARED_WITH_USER",
                        "target_type": "customer",
                        "target_id": u["customer_id"],
                        "target_label": f"{u['full_name']} ({u['tx_count']} txns)",
                        "direction": "outgoing",
                        "details": {"total_usd": round(u["total_usd"], 2)}
                    })

            # Alerts on device transactions
            cursor.execute("""
                SELECT DISTINCT a.alert_id, a.severity, a.composite_risk_score, a.scenario_type
                FROM alerts a
                JOIN transactions t ON a.transaction_id = t.transaction_id
                WHERE t.device_id = ?;
            """, (entity_id,))
            for a in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "device",
                    "source_id": entity_id,
                    "relationship": "ASSOCIATED_ALERT",
                    "target_type": "alert",
                    "target_id": a["alert_id"],
                    "target_label": f"{a['severity']} ({a['composite_risk_score']}) - {a['scenario_type']}",
                    "direction": "outgoing",
                    "details": {}
                })

        # ---------------------------------------------------------------------
        # 5. BENEFICIARY GRAPH
        # ---------------------------------------------------------------------
        elif entity_type == "beneficiary":
            cursor.execute("SELECT beneficiary_id, beneficiary_name, institution_name, is_known_mule, registered_city FROM beneficiaries WHERE beneficiary_id = ?;", (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Senders (customers sending money to this beneficiary)
            cursor.execute("""
                SELECT c.customer_id, c.full_name, COUNT(t.transaction_id) as tx_count,
                       SUM(t.amount_usd_equivalent) as total_usd
                FROM transactions t
                JOIN customers c ON t.customer_id = c.customer_id
                WHERE t.beneficiary_id = ?
                GROUP BY c.customer_id
                ORDER BY total_usd DESC;
            """, (entity_id,))
            for s in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "beneficiary",
                    "source_id": entity_id,
                    "relationship": "RECEIVED_FUNDS_FROM",
                    "target_type": "customer",
                    "target_id": s["customer_id"],
                    "target_label": f"{s['full_name']} ({s['tx_count']} txns)",
                    "direction": "incoming",
                    "details": {"total_usd": round(s["total_usd"], 2)}
                })

            # Alerts on this beneficiary
            cursor.execute("""
                SELECT DISTINCT a.alert_id, a.severity, a.composite_risk_score, a.scenario_type
                FROM alerts a
                JOIN transactions t ON a.transaction_id = t.transaction_id
                WHERE t.beneficiary_id = ?;
            """, (entity_id,))
            for a in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "beneficiary",
                    "source_id": entity_id,
                    "relationship": "ASSOCIATED_ALERT",
                    "target_type": "alert",
                    "target_id": a["alert_id"],
                    "target_label": f"{a['severity']} ({a['composite_risk_score']}) - {a['scenario_type']}",
                    "direction": "outgoing",
                    "details": {}
                })

        # ---------------------------------------------------------------------
        # 6. ALERT GRAPH
        # ---------------------------------------------------------------------
        elif entity_type == "alert":
            cursor.execute("SELECT alert_id, transaction_id, customer_id, account_id, severity, composite_risk_score, scenario_type FROM alerts WHERE alert_id = ?;", (entity_id,))
            root_row = cursor.fetchone()
            if not root_row:
                return None
            root_entity = row_to_dict(root_row)

            # Transaction
            edges.append({
                "source_type": "alert",
                "source_id": entity_id,
                "relationship": "CONCERNS_TRANSACTION",
                "target_type": "transaction",
                "target_id": root_entity["transaction_id"],
                "target_label": root_entity["transaction_id"],
                "direction": "outgoing",
                "details": {}
            })

            # Customer
            cursor.execute("SELECT full_name FROM customers WHERE customer_id = ?;", (root_entity["customer_id"],))
            c_row = cursor.fetchone()
            edges.append({
                "source_type": "alert",
                "source_id": entity_id,
                "relationship": "INVOLVES_CUSTOMER",
                "target_type": "customer",
                "target_id": root_entity["customer_id"],
                "target_label": c_row[0] if c_row else root_entity["customer_id"],
                "direction": "outgoing",
                "details": {}
            })

            # Account
            edges.append({
                "source_type": "alert",
                "source_id": entity_id,
                "relationship": "TARGETS_ACCOUNT",
                "target_type": "account",
                "target_id": root_entity["account_id"],
                "target_label": root_entity["account_id"],
                "direction": "outgoing",
                "details": {}
            })

            # Signals
            cursor.execute("SELECT signal_id, rule_code, severity, confidence_score FROM fraud_signals WHERE alert_id = ?;", (entity_id,))
            for s in rows_to_dicts(cursor.fetchall()):
                edges.append({
                    "source_type": "alert",
                    "source_id": entity_id,
                    "relationship": "FIRED_SIGNAL",
                    "target_type": "signal",
                    "target_id": s["signal_id"],
                    "target_label": f"[{s['rule_code']}] {s['severity']} ({s['confidence_score']})",
                    "direction": "outgoing",
                    "details": {}
                })

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "root_entity": root_entity,
            "total_relationships": len(edges) + len(second_hop_edges),
            "relationships": edges,
            "second_hop_links": second_hop_edges
        }
