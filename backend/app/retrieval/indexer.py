"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Semantic & Structured Retrieval Indexer
-----------------------------------------------------------------------------
Constructs normalized RetrievalDocuments from the synthetic database.
Maintains in-memory primary, secondary, and inverted BM25 token indices.
Zero LLM dependencies.
"""

import math
import re
import sqlite3
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
from backend.app.config import settings
from backend.app.retrieval.models import RetrievalDocument


class BankingIndexer:
    """
    In-memory indexing engine for the synthetic banking database.
    Normalizes tables into search documents and builds multi-tier indexes.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.database_path)
        self.documents: Dict[str, RetrievalDocument] = {}
        
        # Primary lookup maps
        self.by_entity: Dict[Tuple[str, str], List[RetrievalDocument]] = defaultdict(list)
        self.by_type: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        
        # Secondary Foreign-Key indices
        self.by_customer: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_account: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_device: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_beneficiary: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_transaction: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_alert: Dict[str, List[RetrievalDocument]] = defaultdict(list)

        # Attribute indices
        self.by_severity: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_scenario: Dict[str, List[RetrievalDocument]] = defaultdict(list)
        self.by_rule_code: Dict[str, List[RetrievalDocument]] = defaultdict(list)

        # Inverted index for BM25 lexical search
        # token -> dict of {doc_id: term_frequency}
        self.inverted_index: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length: float = 0.0

        self._is_indexed = False

    def ensure_indexed(self):
        """Builds index if not already constructed."""
        if not self._is_indexed:
            self.build_index()

    def build_index(self):
        """Reads synthetic SQLite database and creates all normalized retrieval documents."""
        self.documents.clear()
        self.by_entity.clear()
        self.by_type.clear()
        self.by_customer.clear()
        self.by_account.clear()
        self.by_device.clear()
        self.by_beneficiary.clear()
        self.by_transaction.clear()
        self.by_alert.clear()
        self.by_severity.clear()
        self.by_scenario.clear()
        self.by_rule_code.clear()
        self.inverted_index.clear()
        self.doc_lengths.clear()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            self._index_customers(cursor)
            self._index_accounts(cursor)
            self._index_devices(cursor)
            self._index_beneficiaries(cursor)
            self._index_baselines(cursor)
            self._index_auth_activities(cursor)
            self._index_transactions(cursor)
            self._index_alerts(cursor)
            self._index_fraud_signals(cursor)
            self._index_clusters(cursor)
            self._index_rule_catalog()

            # Build BM25 statistics
            total_tokens = sum(self.doc_lengths.values())
            total_docs = len(self.doc_lengths)
            self.avg_doc_length = (total_tokens / total_docs) if total_docs > 0 else 1.0

            self._is_indexed = True

        finally:
            conn.close()

    def _register_document(self, doc: RetrievalDocument):
        """Stores doc in primary, secondary, and inverted indices."""
        self.documents[doc.document_id] = doc
        self.by_entity[(doc.entity_type, doc.entity_id)].append(doc)
        self.by_type[doc.entity_type].append(doc)

        meta = doc.metadata
        if "customer_id" in meta and meta["customer_id"]:
            self.by_customer[meta["customer_id"]].append(doc)
        if "account_id" in meta and meta["account_id"]:
            self.by_account[meta["account_id"]].append(doc)
        if "device_id" in meta and meta["device_id"]:
            self.by_device[meta["device_id"]].append(doc)
        if "beneficiary_id" in meta and meta["beneficiary_id"]:
            self.by_beneficiary[meta["beneficiary_id"]].append(doc)
        if "transaction_id" in meta and meta["transaction_id"]:
            self.by_transaction[meta["transaction_id"]].append(doc)
        if "alert_id" in meta and meta["alert_id"]:
            self.by_alert[meta["alert_id"]].append(doc)

        if "severity" in meta and meta["severity"]:
            self.by_severity[meta["severity"].upper()].append(doc)
        if "scenario_type" in meta and meta["scenario_type"]:
            self.by_scenario[meta["scenario_type"]].append(doc)
        if "rule_codes" in meta and isinstance(meta["rule_codes"], list):
            for rc in meta["rule_codes"]:
                self.by_rule_code[rc.upper()].append(doc)
        elif "rule_code" in meta and meta["rule_code"]:
            self.by_rule_code[meta["rule_code"].upper()].append(doc)

        # Inverted index tokens
        tokens = self._tokenize(doc.text + " " + doc.title)
        self.doc_lengths[doc.document_id] = len(tokens)
        counts = defaultdict(int)
        for t in tokens:
            counts[t] += 1
        for t, cnt in counts.items():
            self.inverted_index[t][doc.document_id] = cnt

    def _tokenize(self, text: str) -> List[str]:
        """Simple deterministic tokenizer."""
        return [w.lower() for w in re.findall(r"[A-Za-z0-9\-_]+", text) if len(w) >= 2]

    # -------------------------------------------------------------------------
    # Indexing specific tables
    # -------------------------------------------------------------------------
    def _index_customers(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT * FROM customers;")
        for row in cursor.fetchall():
            cid = row["customer_id"]
            name = row["full_name"]
            seg = row["customer_segment"]
            kyc = row["kyc_status"]
            city = row["registered_city"]
            risk = row["risk_category"]
            phone = row["primary_phone"]
            email = row["email"]
            created = row["created_at"]

            text = (
                f"Customer Dossier: {name} (ID: {cid}). Segment: {seg}. KYC Status: {kyc}. "
                f"Risk Category: {risk}. Registered City: {city}, Democratic Republic of Congo. "
                f"Contact Phone: {phone}, Email: {email}. Onboarding Date: {created}. "
                f"Banking Profile: Operates domestic CDF and USD accounts via IllicoCash App and RawbankOnline Web."
            )
            doc = RetrievalDocument(
                document_id=f"doc_cus_{cid}",
                entity_type="customer",
                entity_id=cid,
                title=f"Customer {cid}: {name} ({seg})",
                source_table="customers",
                source_id=cid,
                timestamp=created,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "customer_id": cid,
                    "customer_name": name,
                    "segment": seg,
                    "kyc_status": kyc,
                    "risk_category": risk,
                    "registered_city": city
                }
            )
            self._register_document(doc)

    def _index_accounts(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT acc.*, c.full_name as customer_name
            FROM accounts acc
            JOIN customers c ON acc.customer_id = c.customer_id;
        """)
        for row in cursor.fetchall():
            aid = row["account_id"]
            cid = row["customer_id"]
            cname = row["customer_name"]
            atype = row["account_type"]
            curr = row["currency"]
            cbal = row["current_balance"]
            abal = row["available_balance"]
            status = row["account_status"]

            text = (
                f"Account Ledger: {aid} owned by Customer {cid} ({cname}). "
                f"Type: {atype}. Currency: {curr}. Current Balance: {cbal:,.2f} {curr}. "
                f"Available Balance: {abal:,.2f} {curr}. Account Status: {status}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_acc_{aid}",
                entity_type="account",
                entity_id=aid,
                title=f"Account {aid}: {atype} ({curr})",
                source_table="accounts",
                source_id=aid,
                timestamp=row["created_at"],
                text=text,
                structured_fields=dict(row),
                metadata={
                    "account_id": aid,
                    "customer_id": cid,
                    "currency": curr,
                    "account_type": atype,
                    "balance": cbal,
                    "status": status
                }
            )
            self._register_document(doc)

    def _index_devices(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT * FROM devices;")
        for row in cursor.fetchall():
            did = row["device_id"]
            cid = row["primary_customer_id"]
            dtype = row["device_type"]
            model = row["device_model"]
            os_ver = row["os_version"]
            ip = row["ip_address"]
            ip_city = row["ip_city"]
            trust = row["trust_status"]
            vpn = bool(row["is_vpn_or_tor"])
            rooted = bool(row["is_rooted_jailbroken"])
            first_seen = row["first_seen_timestamp"]
            last_seen = row["last_seen_timestamp"]

            text = (
                f"Hardware Profile: Device {did} ({model}, {os_ver}). Type: {dtype}. "
                f"Primary Enrolled User: {cid}. Trust Status: {trust}. "
                f"Observed IP: {ip} originating from {ip_city}. VPN/Tor Detected: {vpn}. "
                f"Rooted/Jailbroken: {rooted}. Enrolled: {first_seen}, Last Seen: {last_seen}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_dev_{did}",
                entity_type="device",
                entity_id=did,
                title=f"Device {did}: {model} ({trust})",
                source_table="devices",
                source_id=did,
                timestamp=last_seen,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "device_id": did,
                    "customer_id": cid,
                    "device_model": model,
                    "trust_status": trust,
                    "ip_address": ip,
                    "ip_city": ip_city,
                    "is_vpn": vpn
                }
            )
            self._register_document(doc)

    def _index_beneficiaries(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT * FROM beneficiaries;")
        for row in cursor.fetchall():
            bid = row["beneficiary_id"]
            name = row["beneficiary_name"]
            inst = row["institution_name"]
            acct = row["account_or_phone"]
            btype = row["beneficiary_type"]
            city = row["registered_city"]
            mule = bool(row["is_known_mule"])

            text = (
                f"Beneficiary Counterparty: {name} (ID: {bid}). Institution: {inst}. "
                f"Account/MSISDN: {acct}. Classification: {btype}. Location: {city}. "
                f"Known Mule Syndicate Flag: {mule}. Created: {row['created_at']}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_ben_{bid}",
                entity_type="beneficiary",
                entity_id=bid,
                title=f"Beneficiary {bid}: {name} ({inst})",
                source_table="beneficiaries",
                source_id=bid,
                timestamp=row["created_at"],
                text=text,
                structured_fields=dict(row),
                metadata={
                    "beneficiary_id": bid,
                    "beneficiary_name": name,
                    "institution_name": inst,
                    "is_known_mule": mule,
                    "registered_city": city
                }
            )
            self._register_document(doc)

    def _index_baselines(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT b.*, c.full_name as customer_name
            FROM behavioural_baselines b
            JOIN customers c ON b.customer_id = c.customer_id;
        """)
        for row in cursor.fetchall():
            bid = row["baseline_id"]
            cid = row["customer_id"]
            cname = row["customer_name"]
            vol = row["avg_monthly_volume_usd"]
            tx_avg = row["avg_tx_amount_usd"]
            tx_max = row["max_single_tx_amount_usd"]
            hours = row["typical_active_hours_utc"]
            channels = row["common_channels"]
            cities = row["frequent_cities"]

            text = (
                f"Historical Behavioural Baseline Profile {bid} for Customer {cid} ({cname}). "
                f"Average Monthly Transacted Volume: ${vol:,.2f} USD. "
                f"Mean Transaction Amount: ${tx_avg:,.2f} USD. "
                f"Maximum Historical Single Transaction: ${tx_max:,.2f} USD. "
                f"Established Active Hours UTC: {hours}. Typical Channels: {channels}. "
                f"Established Geographic Cities: {cities}. Last Calculated: {row['last_calculated_at']}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_base_{bid}",
                entity_type="behavioural_baseline",
                entity_id=bid,
                title=f"Behavioural Baseline {bid} for {cname}",
                source_table="behavioural_baselines",
                source_id=bid,
                timestamp=row["last_calculated_at"],
                text=text,
                structured_fields=dict(row),
                metadata={
                    "baseline_id": bid,
                    "customer_id": cid,
                    "avg_monthly_volume_usd": vol,
                    "avg_tx_amount_usd": tx_avg,
                    "max_single_tx_amount_usd": tx_max
                }
            )
            self._register_document(doc)

    def _index_auth_activities(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT a.*, c.full_name as customer_name, d.device_model
            FROM auth_activities a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN devices d ON a.device_id = d.device_id;
        """)
        for row in cursor.fetchall():
            aid = row["activity_id"]
            cid = row["customer_id"]
            did = row["device_id"]
            model = row["device_model"]
            ev_type = row["event_type"]
            ch = row["channel"]
            status = row["status"]
            reason = row["failure_reason"] or "None"
            ts = row["timestamp"]
            ip = row["ip_address"]
            city = row["ip_city"]

            text = (
                f"Authentication Audit Record {aid}: Customer {cid} executed {ev_type} "
                f"via {ch} using device {did} ({model}). Outcome: {status} (Reason: {reason}). "
                f"IP Address: {ip} in {city} at {ts}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_auth_{aid}",
                entity_type="auth_activity",
                entity_id=aid,
                title=f"Auth Event {aid}: {ev_type} ({status})",
                source_table="auth_activities",
                source_id=aid,
                timestamp=ts,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "activity_id": aid,
                    "customer_id": cid,
                    "device_id": did,
                    "event_type": ev_type,
                    "status": status,
                    "channel": ch,
                    "city": city
                }
            )
            self._register_document(doc)

    def _index_transactions(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT t.*, c.full_name as customer_name, b.beneficiary_name, d.device_model, d.trust_status
            FROM transactions t
            JOIN customers c ON t.customer_id = c.customer_id
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            JOIN devices d ON t.device_id = d.device_id;
        """)
        for row in cursor.fetchall():
            tid = row["transaction_id"]
            cid = row["customer_id"]
            aid = row["account_id"]
            bid = row["beneficiary_id"]
            did = row["device_id"]
            amt = row["amount"]
            curr = row["currency"]
            usd = row["amount_usd_equivalent"]
            ch = row["channel"]
            ttype = row["transaction_type"]
            city = row["location_city"]
            status = row["status"]
            ts = row["timestamp"]
            cname = row["customer_name"]
            bname = row["beneficiary_name"]
            dmodel = row["device_model"]
            dtrust = row["trust_status"]

            text = (
                f"Financial Transaction {tid}: Amount {amt:,.2f} {curr} (${usd:,.2f} USD) transacted by "
                f"Customer {cid} ({cname}) from Account {aid}. Recipient: {bid} ({bname}). "
                f"Channel: {ch}. Transaction Type: {ttype}. Execution Location: {city}. "
                f"Status: {status}. Timestamp: {ts}. Originating Hardware: {did} ({dmodel}, Trust: {dtrust})."
            )
            doc = RetrievalDocument(
                document_id=f"doc_txn_{tid}",
                entity_type="transaction",
                entity_id=tid,
                title=f"Transaction {tid}: {amt:,.2f} {curr} (${usd:,.2f} USD)",
                source_table="transactions",
                source_id=tid,
                timestamp=ts,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "transaction_id": tid,
                    "customer_id": cid,
                    "account_id": aid,
                    "beneficiary_id": bid,
                    "device_id": did,
                    "amount": amt,
                    "currency": curr,
                    "amount_usd": usd,
                    "channel": ch,
                    "location_city": city,
                    "status": status
                }
            )
            self._register_document(doc)

    def _index_alerts(self, cursor: sqlite3.Cursor):
        cursor.execute("""
            SELECT a.*, c.full_name as customer_name, t.amount_usd_equivalent, t.currency
            FROM alerts a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN transactions t ON a.transaction_id = t.transaction_id;
        """)
        for row in cursor.fetchall():
            alid = row["alert_id"]
            tid = row["transaction_id"]
            cid = row["customer_id"]
            aid = row["account_id"]
            sev = row["severity"]
            score = row["composite_risk_score"]
            status = row["status"]
            scen = row["scenario_type"]
            reason = row["reason_summary"]
            ts = row["created_at"]
            cname = row["customer_name"]
            usd = row["amount_usd_equivalent"]

            text = (
                f"Fraud Alert Dossier {alid}: Triggered on Transaction {tid} (${usd:,.2f} USD) for Customer {cid} ({cname}). "
                f"Severity: {sev}. Composite Risk Score: {score}/100. Scenario Classification: {scen}. "
                f"Lifecycle Status: {status}. Reason Summary: {reason}. Associated Account: {aid}. Timestamp: {ts}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_alt_{alid}",
                entity_type="alert",
                entity_id=alid,
                title=f"Alert {alid}: [{sev}] {scen} (Score: {score})",
                source_table="alerts",
                source_id=alid,
                timestamp=ts,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "alert_id": alid,
                    "transaction_id": tid,
                    "customer_id": cid,
                    "account_id": aid,
                    "severity": sev,
                    "composite_risk_score": score,
                    "scenario_type": scen,
                    "status": status
                }
            )
            self._register_document(doc)

    def _index_fraud_signals(self, cursor: sqlite3.Cursor):
        cursor.execute("SELECT * FROM fraud_signals;")
        for row in cursor.fetchall():
            sid = row["signal_id"]
            alid = row["alert_id"]
            tid = row["transaction_id"]
            rcode = row["rule_code"]
            rname = row["rule_name"]
            rcat = row["rule_category"]
            sev = row["severity"]
            conf = row["confidence_score"]
            desc = row["signal_description"]
            ts = row["created_at"]

            text = (
                f"Deterministic Fraud Signal {sid}: Rule {rcode} ({rname}, Category: {rcat}). "
                f"Severity: {sev}. Forensic Confidence: {conf:.2f}. "
                f"Triggered on Transaction {tid} attached to Alert {alid}. "
                f"Signal Evidence Description: {desc}. Created: {ts}."
            )
            doc = RetrievalDocument(
                document_id=f"doc_sig_{sid}",
                entity_type="fraud_signal",
                entity_id=sid,
                title=f"Signal {sid}: [{rcode}] {rname} ({sev})",
                source_table="fraud_signals",
                source_id=sid,
                timestamp=ts,
                text=text,
                structured_fields=dict(row),
                metadata={
                    "signal_id": sid,
                    "alert_id": alid,
                    "transaction_id": tid,
                    "rule_code": rcode,
                    "rule_category": rcat,
                    "severity": sev,
                    "confidence_score": conf
                }
            )
            self._register_document(doc)

    def _index_clusters(self, cursor: sqlite3.Cursor):
        """Creates Relationship documents for shared devices and mule recipient clusters."""
        # 1. Shared Devices
        cursor.execute("""
            SELECT t.device_id, d.device_model, d.trust_status, COUNT(DISTINCT t.customer_id) as cust_cnt,
                   GROUP_CONCAT(DISTINCT t.customer_id) as cust_ids
            FROM transactions t
            JOIN devices d ON t.device_id = d.device_id
            GROUP BY t.device_id
            HAVING cust_cnt > 1;
        """)
        for row in cursor.fetchall():
            did = row["device_id"]
            model = row["device_model"]
            trust = row["trust_status"]
            cnt = row["cust_cnt"]
            cust_ids = row["cust_ids"].split(",") if row["cust_ids"] else []

            text = (
                f"Shared Device Syndicate Cluster: Hardware {did} ({model}, Trust: {trust}) is actively shared "
                f"across {cnt} distinct customer profiles: {', '.join(cust_ids)}. "
                f"This cross-account hardware sharing is characteristic of fraud rings or coordinated mule operators."
            )
            doc = RetrievalDocument(
                document_id=f"doc_rel_dev_{did}",
                entity_type="relationship",
                entity_id=did,
                title=f"Shared Device Cluster: {did} ({cnt} Customers)",
                source_table="devices",
                source_id=did,
                timestamp=None,
                text=text,
                structured_fields={
                    "relationship_type": "SHARED_DEVICE_CLUSTER",
                    "device_id": did,
                    "device_model": model,
                    "shared_customer_count": cnt,
                    "customer_ids": cust_ids
                },
                metadata={
                    "device_id": did,
                    "relationship_type": "SHARED_DEVICE_CLUSTER",
                    "customer_ids": cust_ids,
                    "scenario_type": "SHARED_DEVICE_RING",
                    "rule_code": "R-DEV-02"
                }
            )
            self._register_document(doc)

        # 2. Mule Inbound Clusters
        cursor.execute("""
            SELECT b.beneficiary_id, b.beneficiary_name, b.institution_name, b.is_known_mule,
                   COUNT(DISTINCT t.customer_id) as sender_cnt,
                   SUM(t.amount_usd_equivalent) as total_usd,
                   GROUP_CONCAT(DISTINCT t.customer_id) as sender_ids
            FROM transactions t
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            GROUP BY b.beneficiary_id
            HAVING sender_cnt > 3;
        """)
        for row in cursor.fetchall():
            bid = row["beneficiary_id"]
            name = row["beneficiary_name"]
            inst = row["institution_name"]
            mule = bool(row["is_known_mule"])
            cnt = row["sender_cnt"]
            total_usd = row["total_usd"] or 0.0
            senders = row["sender_ids"].split(",") if row["sender_ids"] else []

            text = (
                f"Mule Concentration Hub: Beneficiary {bid} ({name} at {inst}) receives incoming funds from "
                f"{cnt} distinct customer accounts ({', '.join(senders)}). Total aggregated incoming volume: "
                f"${total_usd:,.2f} USD. Known Mule Flag: {mule}. Demonstrates characteristic fan-in aggregation."
            )
            doc = RetrievalDocument(
                document_id=f"doc_rel_ben_{bid}",
                entity_type="relationship",
                entity_id=bid,
                title=f"Mule Aggregator Network: {name} ({cnt} Senders)",
                source_table="beneficiaries",
                source_id=bid,
                timestamp=None,
                text=text,
                structured_fields={
                    "relationship_type": "MULE_FAN_IN_CLUSTER",
                    "beneficiary_id": bid,
                    "beneficiary_name": name,
                    "sender_count": cnt,
                    "total_usd": total_usd,
                    "sender_ids": senders
                },
                metadata={
                    "beneficiary_id": bid,
                    "relationship_type": "MULE_FAN_IN_CLUSTER",
                    "customer_ids": senders,
                    "scenario_type": "MULE_FAN_IN",
                    "rule_code": "R-MULE-04"
                }
            )
            self._register_document(doc)

    def _index_rule_catalog(self):
        """Indexes the 11 Phase 3 Deterministic Forensic Rules."""
        rule_defs = [
            ("R-VEL-01", "VelocityBurstRule", "Velocity", "High transaction frequency in short rolling windows (<1h)."),
            ("R-DEV-02", "NewDeviceRule", "Device_Risk", "First observed transaction on a novel, unverified hardware device."),
            ("R-DEV-02-SHARE", "SharedDeviceRule", "Device_Risk", "Hardware fingerprint observed across multiple customer profiles."),
            ("R-GEO-03", "GeographicVelocityRule", "Geographic_Travel", "Physical distance between sequential transactions exceeds 500 km/h flight speed."),
            ("R-MULE-04", "NewBeneficiaryRule", "Mule_Network", "Rapid high-value transfer to newly enrolled recipient without prior history."),
            ("R-MULE-04-FAN", "SharedBeneficiaryRule", "Mule_Network", "Mule concentration hub: beneficiary receiving payments from >3 distinct customer senders."),
            ("R-ATO-05", "ATOPatternRule", "Credential_ATO", "Password reset or credential update followed by novel device enrollment and immediate account drain."),
            ("R-SMURF-06", "StructuringRule", "Structuring", "Multiple sequential transfers just below the $10,000 regulatory AML reporting ceiling."),
            ("R-VAL-07", "ValueSpikeRule", "Value_Spike", "Transaction amount exceeds 5x customer's 30-day rolling baseline median."),
            ("R-AUTH-08", "AuthenticationAnomalyRule", "Auth_Anomaly", "Multiple sequential PIN failures followed by successful credential bypass or high-value drain."),
            ("R-BEH-09", "BehaviouralDeviationRule", "Value_Spike", "Deviation from established historical baseline transacting hours, cities, or channels.")
        ]
        for rcode, rname, rcat, rdesc in rule_defs:
            text = (
                f"Deterministic Forensic Rule: [{rcode}] {rname}. Category: {rcat}. "
                f"Specification: {rdesc}. Executed deterministically in Phase 3 engine."
            )
            doc = RetrievalDocument(
                document_id=f"doc_rule_{rcode}",
                entity_type="rule_evidence",
                entity_id=rcode,
                title=f"Rule Specification [{rcode}]: {rname}",
                source_table="rules",
                source_id=rcode,
                timestamp=None,
                text=text,
                structured_fields={"rule_code": rcode, "rule_name": rname, "category": rcat, "description": rdesc},
                metadata={"rule_code": rcode, "rule_category": rcat}
            )
            self._register_document(doc)


# Global indexer instance
indexer = BankingIndexer()
