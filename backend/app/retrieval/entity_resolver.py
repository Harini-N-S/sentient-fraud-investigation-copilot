"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Deterministic Entity Resolver
-----------------------------------------------------------------------------
Resolves customer, account, transaction, device, beneficiary, alert, and signal
identifiers and natural-language references to verified database entities.
Zero LLM dependencies.
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from backend.app.retrieval.models import ResolvedEntity


class EntityResolver:
    """
    Deterministic entity resolution engine.
    Extracts structured banking identifiers and natural language entity mentions,
    validates them against SQLite ground truth, and reports confidence and ambiguity.
    """

    # Primary ID Regex Patterns (supports CUS-, CUST-, with zero-padding variations)
    ID_PATTERNS: List[Tuple[str, str, re.Pattern]] = [
        # (entity_type, table_name, compiled_regex)
        ("customer", "customers", re.compile(r"\b(?:CUST?)[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("account", "accounts", re.compile(r"\bACC[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("transaction", "transactions", re.compile(r"\bTXN[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("device", "devices", re.compile(r"\bDEV[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("beneficiary", "beneficiaries", re.compile(r"\bBEN[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("alert", "alerts", re.compile(r"\bALT[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("signal", "fraud_signals", re.compile(r"\bSIG[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("behavioural_baseline", "behavioural_baselines", re.compile(r"\bBASE[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
        ("auth_activity", "auth_activities", re.compile(r"\bAUTH[-_]?0*(\d{1,5})\b", re.IGNORECASE)),
    ]

    PREFIX_MAP = {
        "customer": "CUS",
        "account": "ACC",
        "transaction": "TXN",
        "device": "DEV",
        "beneficiary": "BEN",
        "alert": "ALT",
        "signal": "SIG",
        "behavioural_baseline": "BASE",
        "auth_activity": "AUTH"
    }

    # Natural Language Reference Phrases
    NL_PATTERNS = [
        ("customer", re.compile(r"\b(?:customer|client|account holder)\s+([A-Za-z\s'\-]+?)(?:\s+(?:flagged|account|transaction|alert|device|baseline|using|with|\?|$))", re.IGNORECASE)),
        ("beneficiary", re.compile(r"\b(?:beneficiary|recipient|receiver)\s+([A-Za-z0-9\s'\-]+?)(?:\s+(?:used|flagged|account|transaction|alert|with|\?|$))", re.IGNORECASE)),
        ("device", re.compile(r"\b(?:device|hardware|phone|laptop|macbook)\s+([A-Za-z0-9\s\-]+?)(?:\s+(?:used|flagged|shared|with|\?|$))", re.IGNORECASE)),
    ]

    @classmethod
    def resolve_text(cls, db: sqlite3.Connection, text: str) -> List[ResolvedEntity]:
        """
        Scans input query text, extracts all entity references, verifies them against SQLite,
        and returns a deduplicated list of ResolvedEntity records.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        resolved: List[ResolvedEntity] = []
        seen_keys = set()

        cursor = db.cursor()

        # 1. Structured Identifier Extraction & Verification
        for entity_type, table_name, pattern in cls.ID_PATTERNS:
            for match in pattern.finditer(clean_text):
                matched_raw = match.group(0)
                num = int(match.group(1))
                prefix = cls.PREFIX_MAP[entity_type]
                canonical_id = f"{prefix}-{num:05d}"

                key = (entity_type, canonical_id)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                # Query database for exact existence
                entity_details = cls._fetch_entity_details(cursor, entity_type, table_name, canonical_id)
                if entity_details:
                    is_exact_match = (matched_raw.upper() == canonical_id.upper())
                    method = "exact_id" if is_exact_match else "normalized_id"
                    resolved.append(ResolvedEntity(
                        entity_type=entity_type,
                        entity_id=matched_raw,
                        canonical_id=canonical_id,
                        confidence=1.0,
                        matching_method=method,
                        matched_text=matched_raw,
                        is_ambiguous=False,
                        candidates=[],
                        details=entity_details
                    ))
                else:
                    # Entity referenced with a valid ID pattern but not found in DB
                    resolved.append(ResolvedEntity(
                        entity_type=entity_type,
                        entity_id=matched_raw,
                        canonical_id=canonical_id,
                        confidence=0.0,
                        matching_method="unknown_identifier",
                        matched_text=matched_raw,
                        is_ambiguous=False,
                        candidates=[],
                        details=None
                    ))

        # 2. Natural Language Name Matching (Customer full names)
        # Check explicit "customer <name>" patterns or standalone customer names
        cls._resolve_natural_language_names(cursor, clean_text, resolved, seen_keys)

        return resolved

    @classmethod
    def resolve_single(cls, db: sqlite3.Connection, entity_type: str, entity_id: str) -> ResolvedEntity:
        """
        Resolves a single provided entity type and ID with canonical normalization.
        """
        etype = entity_type.lower().strip()
        clean_id = entity_id.strip()

        # Check if known prefix pattern
        prefix = cls.PREFIX_MAP.get(etype)
        canonical_id = clean_id
        if prefix:
            match = re.search(r"(\d{1,5})", clean_id)
            if match:
                canonical_id = f"{prefix}-{int(match.group(1)):05d}"

        table_map = {
            "customer": "customers",
            "account": "accounts",
            "transaction": "transactions",
            "device": "devices",
            "beneficiary": "beneficiaries",
            "alert": "alerts",
            "signal": "fraud_signals",
            "behavioural_baseline": "behavioural_baselines",
            "auth_activity": "auth_activities"
        }
        table_name = table_map.get(etype, f"{etype}s")

        cursor = db.cursor()
        details = cls._fetch_entity_details(cursor, etype, table_name, canonical_id)
        if details:
            return ResolvedEntity(
                entity_type=etype,
                entity_id=clean_id,
                canonical_id=canonical_id,
                confidence=1.0,
                matching_method="exact_id" if clean_id.upper() == canonical_id.upper() else "normalized_id",
                matched_text=clean_id,
                is_ambiguous=False,
                candidates=[],
                details=details
            )
        else:
            return ResolvedEntity(
                entity_type=etype,
                entity_id=clean_id,
                canonical_id=canonical_id,
                confidence=0.0,
                matching_method="unknown_identifier",
                matched_text=clean_id,
                is_ambiguous=False,
                candidates=[],
                details=None
            )

    @classmethod
    def _fetch_entity_details(cls, cursor: sqlite3.Cursor, entity_type: str, table_name: str, canonical_id: str) -> Optional[Dict[str, Any]]:
        """Queries the database table for primary attributes of an entity."""
        try:
            if entity_type == "customer":
                cursor.execute("""
                    SELECT customer_id, full_name, customer_segment, registered_city, risk_category, kyc_status, primary_phone, email
                    FROM customers WHERE customer_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "customer_id": r[0], "full_name": r[1], "customer_segment": r[2],
                        "registered_city": r[3], "risk_category": r[4], "kyc_status": r[5],
                        "primary_phone": r[6], "email": r[7]
                    }

            elif entity_type == "account":
                cursor.execute("""
                    SELECT account_id, customer_id, account_type, currency, current_balance, available_balance, account_status
                    FROM accounts WHERE account_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "account_id": r[0], "customer_id": r[1], "account_type": r[2],
                        "currency": r[3], "current_balance": r[4], "available_balance": r[5], "account_status": r[6]
                    }

            elif entity_type == "transaction":
                cursor.execute("""
                    SELECT transaction_id, customer_id, account_id, beneficiary_id, device_id,
                           amount, currency, amount_usd_equivalent, channel, location_city, status, timestamp
                    FROM transactions WHERE transaction_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "transaction_id": r[0], "customer_id": r[1], "account_id": r[2],
                        "beneficiary_id": r[3], "device_id": r[4], "amount": r[5],
                        "currency": r[6], "amount_usd_equivalent": r[7], "channel": r[8],
                        "location_city": r[9], "status": r[10], "timestamp": r[11]
                    }

            elif entity_type == "device":
                cursor.execute("""
                    SELECT device_id, primary_customer_id, device_type, device_model, trust_status, ip_address, ip_city
                    FROM devices WHERE device_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "device_id": r[0], "primary_customer_id": r[1], "device_type": r[2],
                        "device_model": r[3], "trust_status": r[4], "ip_address": r[5], "ip_city": r[6]
                    }

            elif entity_type == "beneficiary":
                cursor.execute("""
                    SELECT beneficiary_id, beneficiary_name, institution_name, account_or_phone, beneficiary_type, is_known_mule
                    FROM beneficiaries WHERE beneficiary_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "beneficiary_id": r[0], "beneficiary_name": r[1], "institution_name": r[2],
                        "account_or_phone": r[3], "beneficiary_type": r[4], "is_known_mule": bool(r[5])
                    }

            elif entity_type == "alert":
                cursor.execute("""
                    SELECT alert_id, transaction_id, customer_id, account_id, severity, composite_risk_score, status, scenario_type, reason_summary
                    FROM alerts WHERE alert_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "alert_id": r[0], "transaction_id": r[1], "customer_id": r[2],
                        "account_id": r[3], "severity": r[4], "composite_risk_score": r[5],
                        "status": r[6], "scenario_type": r[7], "reason_summary": r[8]
                    }

            elif entity_type == "signal":
                cursor.execute("""
                    SELECT signal_id, alert_id, transaction_id, rule_code, rule_name, rule_category, severity, confidence_score, signal_description
                    FROM fraud_signals WHERE signal_id = ?;
                """, (canonical_id,))
                r = cursor.fetchone()
                if r:
                    return {
                        "signal_id": r[0], "alert_id": r[1], "transaction_id": r[2],
                        "rule_code": r[3], "rule_name": r[4], "rule_category": r[5],
                        "severity": r[6], "confidence_score": r[7], "signal_description": r[8]
                    }

            else:
                pk_map = {
                    "behavioural_baseline": "baseline_id",
                    "auth_activity": "activity_id"
                }
                pk_col = pk_map.get(entity_type, f"{entity_type}_id")
                cursor.execute(f"SELECT * FROM {table_name} WHERE {pk_col} = ?;", (canonical_id,))
                r = cursor.fetchone()
                if r:
                    col_names = [d[0] for d in cursor.description]
                    return dict(zip(col_names, r))

        except sqlite3.OperationalError:
            return None

        return None

    @classmethod
    def _resolve_natural_language_names(
        cls, cursor: sqlite3.Cursor, text: str, resolved: List[ResolvedEntity], seen_keys: set
    ):
        """
        Detects customer and beneficiary names mentioned in queries.
        Handles both single matches (high confidence) and ambiguous multiple matches.
        """
        # Look for explicit name mentions
        name_patterns = [
            (r"\b(?:customer|client|user)\s+([A-Za-z\s'\-]+?)(?:\s+(?:flagged|account|transaction|alert|device|baseline|using|with|\?|$))", "customer"),
            (r"\b(?:beneficiary|recipient|receiver)\s+([A-Za-z0-9\s'\-]+?)(?:\s+(?:used|flagged|account|transaction|alert|with|\?|$))", "beneficiary")
        ]

        extracted_phrases: List[Tuple[str, str]] = []
        for pattern_str, etype in name_patterns:
            for match in re.finditer(pattern_str, text, re.IGNORECASE):
                phrase = match.group(1).strip()
                if len(phrase) >= 3 and not phrase.upper().startswith(("CUS-", "BEN-", "DEV-", "ACC-", "TXN-", "ALT-")):
                    extracted_phrases.append((phrase, etype))

        # Also search against distinct names if full text has common DRC names
        # Let's inspect extracted phrases
        for phrase, etype in extracted_phrases:
            if etype == "customer":
                cls._match_customer_name(cursor, phrase, resolved, seen_keys)
            elif etype == "beneficiary":
                cls._match_beneficiary_name(cursor, phrase, resolved, seen_keys)

        # Fallback: if no structured ID was found in resolved, try searching customer names in text
        if not any(r.confidence > 0 for r in resolved):
            # Tokenize words to test known multi-word customer names
            words = text.split()
            if len(words) >= 2:
                for i in range(len(words) - 1):
                    two_word_candidate = f"{words[i]} {words[i+1]}".strip("?,.!;:\"'()")
                    if len(two_word_candidate) >= 6:
                        cls._match_customer_name(cursor, two_word_candidate, resolved, seen_keys)

    @classmethod
    def _match_customer_name(cls, cursor: sqlite3.Cursor, name: str, resolved: List[ResolvedEntity], seen_keys: set):
        """Matches a customer name with exact or substring searches, handling ambiguity."""
        cursor.execute("""
            SELECT customer_id, full_name, customer_segment, registered_city, risk_category
            FROM customers
            WHERE full_name LIKE ?;
        """, (f"%{name}%",))
        rows = cursor.fetchall()
        if not rows:
            return

        candidates = [
            {"customer_id": r[0], "full_name": r[1], "customer_segment": r[2], "registered_city": r[3], "risk_category": r[4]}
            for r in rows
        ]

        # Exact match check
        exact_matches = [c for c in candidates if c["full_name"].lower() == name.lower()]
        if len(exact_matches) == 1:
            match = exact_matches[0]
            key = ("customer", match["customer_id"])
            if key not in seen_keys:
                seen_keys.add(key)
                resolved.append(ResolvedEntity(
                    entity_type="customer",
                    entity_id=match["customer_id"],
                    canonical_id=match["customer_id"],
                    confidence=0.95,
                    matching_method="exact_name",
                    matched_text=name,
                    is_ambiguous=False,
                    candidates=[],
                    details=match
                ))
        elif len(exact_matches) > 1:
            # Multiple exact name duplicates
            resolved.append(ResolvedEntity(
                entity_type="customer",
                entity_id="AMBIGUOUS",
                canonical_id="AMBIGUOUS",
                confidence=0.50,
                matching_method="ambiguous_match",
                matched_text=name,
                is_ambiguous=True,
                candidates=exact_matches,
                details=None
            ))
        elif len(candidates) == 1:
            match = candidates[0]
            key = ("customer", match["customer_id"])
            if key not in seen_keys:
                seen_keys.add(key)
                resolved.append(ResolvedEntity(
                    entity_type="customer",
                    entity_id=match["customer_id"],
                    canonical_id=match["customer_id"],
                    confidence=0.85,
                    matching_method="name_substring",
                    matched_text=name,
                    is_ambiguous=False,
                    candidates=[],
                    details=match
                ))
        elif len(candidates) > 1:
            # Ambiguous substring match
            resolved.append(ResolvedEntity(
                entity_type="customer",
                entity_id="AMBIGUOUS",
                canonical_id="AMBIGUOUS",
                confidence=0.40,
                matching_method="ambiguous_substring",
                matched_text=name,
                is_ambiguous=True,
                candidates=candidates[:5],
                details=None
            ))

    @classmethod
    def _match_beneficiary_name(cls, cursor: sqlite3.Cursor, name: str, resolved: List[ResolvedEntity], seen_keys: set):
        """Matches a beneficiary name with exact or substring searches."""
        cursor.execute("""
            SELECT beneficiary_id, beneficiary_name, institution_name, registered_city, is_known_mule
            FROM beneficiaries
            WHERE beneficiary_name LIKE ?;
        """, (f"%{name}%",))
        rows = cursor.fetchall()
        if not rows:
            return

        candidates = [
            {"beneficiary_id": r[0], "beneficiary_name": r[1], "institution_name": r[2], "registered_city": r[3], "is_known_mule": bool(r[4])}
            for r in rows
        ]

        if len(candidates) == 1:
            match = candidates[0]
            key = ("beneficiary", match["beneficiary_id"])
            if key not in seen_keys:
                seen_keys.add(key)
                resolved.append(ResolvedEntity(
                    entity_type="beneficiary",
                    entity_id=match["beneficiary_id"],
                    canonical_id=match["beneficiary_id"],
                    confidence=0.90,
                    matching_method="beneficiary_name",
                    matched_text=name,
                    is_ambiguous=False,
                    candidates=[],
                    details=match
                ))
        else:
            resolved.append(ResolvedEntity(
                entity_type="beneficiary",
                entity_id="AMBIGUOUS",
                canonical_id="AMBIGUOUS",
                confidence=0.45,
                matching_method="ambiguous_beneficiary_name",
                matched_text=name,
                is_ambiguous=True,
                candidates=candidates[:5],
                details=None
            ))
