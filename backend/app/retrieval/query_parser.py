"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Deterministic Query Parser
-----------------------------------------------------------------------------
Parses natural language and structured investigation queries into typed
intents, recognized entities, metadata filters, and search keywords.
Zero LLM dependencies.
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional
from backend.app.retrieval.models import ParsedQuery, ResolvedEntity
from backend.app.retrieval.entity_resolver import EntityResolver


class QueryParser:
    """
    Deterministic rule-based query parser.
    Extracts intents, filters, and entities without any LLM inference.
    """

    STOPWORDS = {
        "the", "a", "an", "and", "or", "in", "on", "at", "by", "for", "with",
        "about", "against", "between", "into", "through", "during", "before",
        "after", "above", "below", "to", "from", "up", "down", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "do",
        "does", "did", "what", "which", "who", "whom", "this", "that", "these",
        "those", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "can", "will", "just", "show",
        "get", "find", "list", "give", "tell", "me", "please"
    }

    SEVERITY_KEYWORDS = {
        "critical": "CRITICAL",
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW"
    }

    SCENARIO_KEYWORDS = {
        "impossible travel": "IMPOSSIBLE_TRAVEL",
        "geographic travel": "IMPOSSIBLE_TRAVEL",
        "account takeover": "ATO_DRAIN",
        "ato": "ATO_DRAIN",
        "password reset": "ATO_DRAIN",
        "shared device": "SHARED_DEVICE_RING",
        "device ring": "SHARED_DEVICE_RING",
        "syndicate": "SHARED_DEVICE_RING",
        "mule": "MULE_FAN_IN",
        "mule fan in": "MULE_FAN_IN",
        "mule aggregator": "MULE_FAN_IN",
        "structuring": "STRUCTURING_SMURF",
        "smurfing": "STRUCTURING_SMURF",
        "smurf": "STRUCTURING_SMURF",
        "velocity": "VELOCITY_BURST",
        "velocity burst": "VELOCITY_BURST",
        "brute force": "BRUTE_FORCE_DRAIN",
        "failed login": "BRUTE_FORCE_DRAIN",
        "invalid pin": "BRUTE_FORCE_DRAIN",
        "behavioural deviation": "UNUSUAL_BEHAVIOUR",
        "behavioral deviation": "UNUSUAL_BEHAVIOUR",
        "unusual behaviour": "UNUSUAL_BEHAVIOUR",
        "legitimate": "LEGITIMATE_ANOMALY",
        "false positive": "LEGITIMATE_ANOMALY",
        "corporate payment": "LEGITIMATE_ANOMALY",
        "vip payment": "LEGITIMATE_ANOMALY",
    }

    RULE_CODE_MAP = {
        "r-vel-01": "R-VEL-01",
        "r-dev-02": "R-DEV-02",
        "r-geo-03": "R-GEO-03",
        "r-mule-04": "R-MULE-04",
        "r-ato-05": "R-ATO-05",
        "r-smurf-06": "R-SMURF-06",
        "r-val-07": "R-VAL-07",
        "r-auth-08": "R-AUTH-08",
        "r-beh-09": "R-BEH-09",
    }

    CITIES = {"kinshasa", "lubumbashi", "kolwezi", "goma", "matadi", "bukavu"}
    CHANNELS = {
        "illicocash": "IllicoCash_App",
        "illicocash_app": "IllicoCash_App",
        "rawbankonline": "RawbankOnline_Web",
        "rawbankonline_web": "RawbankOnline_Web",
        "atm": "ATM_Cardless",
        "atm_cardless": "ATM_Cardless",
        "agency": "Agency_Express_POS",
        "agency_express_pos": "Agency_Express_POS",
        "swift": "SWIFT_Wire",
        "swift_wire": "SWIFT_Wire"
    }

    CURRENCIES = {"cdf": "CDF", "usd": "USD"}

    @classmethod
    def parse(cls, db: sqlite3.Connection, query: str) -> ParsedQuery:
        """
        Parses the input string into a structured ParsedQuery model.
        """
        raw_query = query.strip()
        normalized = " ".join(raw_query.lower().replace("?", " ").replace("!", " ").replace(",", " ").split())

        # 1. Resolve entities mentioned
        resolved_entities = EntityResolver.resolve_text(db, raw_query)

        # 2. Extract structured filters
        filters: Dict[str, Any] = {}

        # Severity filter
        for word, sev in cls.SEVERITY_KEYWORDS.items():
            if re.search(rf"\b{word}\b", normalized):
                filters["severity"] = sev
                break

        # Scenario filter
        for phrase, scen in cls.SCENARIO_KEYWORDS.items():
            if phrase in normalized:
                filters["scenario_type"] = scen
                break

        # Rule code filter
        for rule_text, rule_code in cls.RULE_CODE_MAP.items():
            if rule_text in normalized:
                filters["rule_code"] = rule_code
                break

        # City filter
        for city in cls.CITIES:
            if re.search(rf"\b{city}\b", normalized):
                filters["city"] = city.capitalize()
                break

        # Channel filter
        for ch_key, ch_val in cls.CHANNELS.items():
            if ch_key in normalized:
                filters["channel"] = ch_val
                break

        # Currency filter
        for curr_key, curr_val in cls.CURRENCIES.items():
            if re.search(rf"\b{curr_key}\b", normalized):
                filters["currency"] = curr_val
                break

        # Amount range filter (e.g. "over 5000", "above 10000", "greater than 4000")
        min_amt_match = re.search(r"(?:over|above|greater than|>)\s*\$?([0-9,]+(?:\.[0-9]+)?)", normalized)
        if min_amt_match:
            try:
                filters["min_amount_usd"] = float(min_amt_match.group(1).replace(",", ""))
            except ValueError:
                pass

        max_amt_match = re.search(r"(?:under|below|less than|<)\s*\$?([0-9,]+(?:\.[0-9]+)?)", normalized)
        if max_amt_match:
            try:
                filters["max_amount_usd"] = float(max_amt_match.group(1).replace(",", ""))
            except ValueError:
                pass

        # 3. Detect Relationship target & intent
        is_relational = False
        rel_target = None

        if any(w in normalized for w in ["sharing", "shared", "also used", "network", "ring", "cluster", "co-users"]):
            is_relational = True
            if "device" in normalized or any(e.entity_type == "device" for e in resolved_entities):
                rel_target = "co_users"
            elif "beneficiary" in normalized or any(e.entity_type == "beneficiary" for e in resolved_entities):
                rel_target = "senders"
            else:
                rel_target = "related_entities"

        elif "devices used by" in normalized or "devices for" in normalized:
            is_relational = True
            rel_target = "devices"

        elif "beneficiaries used by" in normalized or "beneficiaries for" in normalized:
            is_relational = True
            rel_target = "beneficiaries"

        elif "transactions involving" in normalized or "transactions for" in normalized:
            is_relational = True
            rel_target = "transactions"

        elif "alerts for" in normalized:
            is_relational = True
            rel_target = "alerts"

        # 4. Intent Classification
        if any(w in normalized for w in ["why", "flagged", "evidence", "investigate", "reason", "dossier", "explanation"]):
            intent = "INVESTIGATE_ENTITY"
        elif is_relational:
            intent = "FIND_RELATIONSHIPS"
        elif "filters" in filters and ("scenario_type" in filters or "rule_code" in filters):
            intent = "SCENARIO_SEARCH"
        elif "alert" in normalized or ("severity" in filters and "transaction" not in normalized):
            intent = "FILTER_ALERTS"
        elif "transaction" in normalized or "min_amount_usd" in filters:
            intent = "FILTER_TRANSACTIONS"
        elif resolved_entities and any(e.confidence >= 0.8 for e in resolved_entities):
            intent = "INVESTIGATE_ENTITY"
        else:
            intent = "GENERAL_SEARCH"

        # 5. Extract Keywords
        words = re.findall(r"[A-Za-z0-9\-_]+", normalized)
        keywords = [
            w for w in words
            if w not in cls.STOPWORDS
            and len(w) >= 3
            and not w.startswith(("cus-", "acc-", "txn-", "dev-", "ben-", "alt-", "sig-"))
        ]

        return ParsedQuery(
            raw_query=raw_query,
            normalized_query=normalized,
            intent=intent,
            resolved_entities=resolved_entities,
            filters=filters,
            keywords=keywords,
            is_relational=is_relational,
            relationship_target=rel_target
        )
