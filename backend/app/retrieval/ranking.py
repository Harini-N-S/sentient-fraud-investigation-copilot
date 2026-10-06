"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Deterministic & Explainable Ranking Engine
-----------------------------------------------------------------------------
Combines BM25 lexical relevance, exact identifier matches, entity graph hops,
severity weighting, scenario matching, and counter-evidence detection.
Zero ML black-box scoring. 100% explainable reasons.
"""

import math
from typing import Dict, Any, List, Tuple
from backend.app.retrieval.models import RetrievalDocument, ParsedQuery, ResolvedEntity


class RetrievalRanker:
    """
    Computes explainable relevance scores and reasons for retrieved documents.
    """

    # BM25 Hyperparameters
    K1: float = 1.2
    B: float = 0.75

    @classmethod
    def compute_bm25_score(
        cls,
        doc_id: str,
        keywords: List[str],
        inverted_index: Dict[str, Dict[str, int]],
        doc_lengths: Dict[str, int],
        avg_doc_length: float,
        total_docs: int
    ) -> float:
        """
        Calculates classic BM25 lexical score for given document and query keywords.
        """
        if not keywords or total_docs == 0:
            return 0.0

        doc_len = doc_lengths.get(doc_id, 0)
        score = 0.0

        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in inverted_index:
                continue

            posting = inverted_index[kw_lower]
            df = len(posting)
            tf = posting.get(doc_id, 0)
            if tf == 0:
                continue

            # Standard Robertson-Spärck Jones IDF
            idf = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))
            if idf < 0:
                idf = 0.0

            # Term frequency saturation with document length normalization
            denom = tf + cls.K1 * (1.0 - cls.B + cls.B * (doc_len / avg_doc_length))
            tf_component = (tf * (cls.K1 + 1.0)) / denom if denom > 0 else 0.0

            score += idf * tf_component

        return score

    @classmethod
    def rank_document(
        cls,
        doc: RetrievalDocument,
        parsed_query: ParsedQuery,
        bm25_score: float,
        max_bm25_score: float = 10.0
    ) -> Tuple[float, List[str]]:
        """
        Evaluates a document against a parsed query and returns:
          (relevance_score [0.0 - 1.0], relevance_reasons)
        """
        score = 0.0
        reasons: List[str] = []
        meta = doc.metadata

        # Set of canonical IDs resolved from the query
        resolved_canonical_ids = {
            e.canonical_id for e in parsed_query.resolved_entities if e.confidence > 0
        }
        raw_query_upper = parsed_query.raw_query.upper()

        # 1. Exact Identifier Match (+0.35)
        if doc.entity_id.upper() in raw_query_upper or (doc.entity_id in resolved_canonical_ids):
            score += 0.35
            reasons.append(f"exact_identifier_match({doc.entity_type}:{doc.entity_id})")

        # 2. Primary Resolved Entity Target (+0.30)
        for entity in parsed_query.resolved_entities:
            if entity.confidence > 0 and entity.entity_type == doc.entity_type and entity.canonical_id == doc.entity_id:
                score += 0.30
                reasons.append("primary_resolved_entity")
                break

        # 3. Direct Relationship (1-Hop Foreign Key) (+0.25)
        # E.g. Query asked about CUS-00014, and this doc has customer_id = CUS-00014
        for entity in parsed_query.resolved_entities:
            if entity.confidence > 0:
                cid = entity.canonical_id
                if meta.get("customer_id") == cid and doc.entity_type != "customer":
                    score += 0.25
                    reasons.append(f"related_to_customer({cid})")
                    break
                elif meta.get("transaction_id") == cid and doc.entity_type != "transaction":
                    score += 0.25
                    reasons.append(f"related_to_transaction({cid})")
                    break
                elif meta.get("device_id") == cid and doc.entity_type != "device":
                    score += 0.25
                    reasons.append(f"related_to_device({cid})")
                    break
                elif meta.get("beneficiary_id") == cid and doc.entity_type != "beneficiary":
                    score += 0.25
                    reasons.append(f"related_to_beneficiary({cid})")
                    break
                elif meta.get("alert_id") == cid and doc.entity_type != "alert":
                    score += 0.25
                    reasons.append(f"related_to_alert({cid})")
                    break

        # 4. Scenario Type Match (+0.20)
        target_scenario = parsed_query.filters.get("scenario_type")
        if target_scenario:
            doc_scen = meta.get("scenario_type")
            if doc_scen == target_scenario:
                score += 0.20
                reasons.append(f"scenario_match({target_scenario})")
            elif target_scenario in doc.text:
                score += 0.12
                reasons.append(f"scenario_mention({target_scenario})")

        # 5. Rule Code Match (+0.18)
        target_rule = parsed_query.filters.get("rule_code")
        if target_rule:
            doc_rules = meta.get("rule_codes", [])
            if isinstance(doc_rules, str):
                doc_rules = [doc_rules]
            doc_single_rule = meta.get("rule_code")
            if doc_single_rule:
                doc_rules.append(doc_single_rule)

            if target_rule in [r.upper() for r in doc_rules]:
                score += 0.18
                reasons.append(f"rule_code_match({target_rule})")
            elif target_rule.upper() in doc.text.upper():
                score += 0.10
                reasons.append(f"rule_code_mention({target_rule})")

        # 6. Severity Boost
        doc_sev = meta.get("severity")
        target_sev = parsed_query.filters.get("severity")
        if target_sev and doc_sev == target_sev:
            score += 0.15
            reasons.append(f"filter_severity_match({target_sev})")
        elif doc_sev == "CRITICAL":
            score += 0.12
            reasons.append("critical_severity_alert")
        elif doc_sev == "HIGH":
            score += 0.08
            reasons.append("high_severity_alert")
        elif doc_sev == "MEDIUM":
            score += 0.04
            reasons.append("medium_severity_alert")

        # 7. BM25 Lexical Keyword Similarity (up to +0.20)
        if bm25_score > 0 and max_bm25_score > 0:
            norm_bm25 = min(bm25_score / max_bm25_score, 1.0)
            score += norm_bm25 * 0.20
            reasons.append(f"keyword_lexical_match(bm25={bm25_score:.2f})")

        # 8. Counter-Evidence & False-Positive Factor (+0.18)
        # When user asks about legitimate anomaly, false positive, or corporate payments
        if parsed_query.filters.get("scenario_type") == "LEGITIMATE_ANOMALY" or any(w in parsed_query.normalized_query for w in ["false positive", "legitimate", "corporate"]):
            if meta.get("segment") == "Corporate" or meta.get("trust_status") == "Trusted_Enrolled" or meta.get("kyc_status") == "Tier_3_Full" or meta.get("scenario_type") == "LEGITIMATE_ANOMALY":
                score += 0.18
                reasons.append("counter_evidence_mitigation")

        # 9. Cluster & Syndicate Factor (+0.15)
        if doc.entity_type == "relationship" and parsed_query.is_relational:
            score += 0.20
            reasons.append("relational_network_cluster")

        # Normalize score into range [0.0, 1.0]
        final_score = min(max(round(score, 3), 0.0), 1.0)

        # Deduplicate reasons while preserving order
        unique_reasons = []
        for r in reasons:
            if r not in unique_reasons:
                unique_reasons.append(r)

        return final_score, unique_reasons
