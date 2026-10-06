"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Hybrid Retriever
-----------------------------------------------------------------------------
Coordinates entity resolution, structured metadata filtering, inverted index
BM25 scoring, relationship graph expansion, and explainable ranking.
Zero LLM dependencies.
"""

import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Set
from backend.app.config import settings
from backend.app.retrieval.models import (
    RetrievalDocument,
    ParsedQuery,
    ResolvedEntity,
    RetrievalResult
)
from backend.app.retrieval.indexer import indexer
from backend.app.retrieval.query_parser import QueryParser
from backend.app.retrieval.entity_resolver import EntityResolver
from backend.app.retrieval.ranking import RetrievalRanker


class HybridRetriever:
    """
    Modular, reproducible hybrid retrieval service.
    Fuses exact identifier lookups, structured metadata filters,
    lexical BM25 ranking, and relationship graph traversals.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(settings.database_path)

    def retrieve(
        self,
        query: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        min_score: float = 0.05,
        max_depth: int = 2
    ) -> Tuple[ParsedQuery, List[RetrievalResult]]:
        """
        Executes hybrid retrieval over the banking database documents.
        Returns parsed query metadata and sorted, explainable RetrievalResults.
        """
        indexer.ensure_indexed()

        conn = sqlite3.connect(self.db_path)
        try:
            # 1. Parse query and resolve entities
            parsed = QueryParser.parse(conn, query)

            # Inject explicit entity if provided
            if entity_type and entity_id:
                explicit_resolved = EntityResolver.resolve_single(conn, entity_type, entity_id)
                # Avoid duplicate entity entries
                if not any(e.canonical_id == explicit_resolved.canonical_id for e in parsed.resolved_entities):
                    parsed.resolved_entities.insert(0, explicit_resolved)

            # Merge explicit filters
            if filters:
                parsed.filters.update(filters)

            # 2. Collect Candidate Documents across all vectors
            candidates: Dict[str, RetrievalDocument] = {}
            bm25_scores: Dict[str, float] = {}

            # 2a. Direct Entity Lookups
            for ent in parsed.resolved_entities:
                if ent.confidence > 0:
                    # Look up exact docs
                    for doc in indexer.by_entity.get((ent.entity_type, ent.canonical_id), []):
                        candidates[doc.document_id] = doc

                    # 1-Hop Foreign Key Lookups
                    if ent.entity_type == "customer":
                        for doc in indexer.by_customer.get(ent.canonical_id, []):
                            candidates[doc.document_id] = doc
                    elif ent.entity_type == "device":
                        for doc in indexer.by_device.get(ent.canonical_id, []):
                            candidates[doc.document_id] = doc
                    elif ent.entity_type == "beneficiary":
                        for doc in indexer.by_beneficiary.get(ent.canonical_id, []):
                            candidates[doc.document_id] = doc
                    elif ent.entity_type == "transaction":
                        for doc in indexer.by_transaction.get(ent.canonical_id, []):
                            candidates[doc.document_id] = doc
                    elif ent.entity_type == "alert":
                        for doc in indexer.by_alert.get(ent.canonical_id, []):
                            candidates[doc.document_id] = doc

                    # 2-Hop Relationship Lookups if depth >= 2
                    if max_depth >= 2:
                        self._expand_two_hop_candidates(ent, candidates)

            # 2b. Structured Filter Candidates
            if "severity" in parsed.filters:
                sev_target = parsed.filters["severity"].upper()
                for doc in indexer.by_severity.get(sev_target, []):
                    candidates[doc.document_id] = doc

            if "scenario_type" in parsed.filters:
                scen_target = parsed.filters["scenario_type"]
                for doc in indexer.by_scenario.get(scen_target, []):
                    candidates[doc.document_id] = doc

            if "rule_code" in parsed.filters:
                rcode_target = parsed.filters["rule_code"].upper()
                for doc in indexer.by_rule_code.get(rcode_target, []):
                    candidates[doc.document_id] = doc

            # 2c. Lexical BM25 Inverted Index Search
            total_docs = len(indexer.documents)
            for kw in parsed.keywords:
                kw_lower = kw.lower()
                posting = indexer.inverted_index.get(kw_lower, {})
                for doc_id in posting:
                    if doc_id in indexer.documents:
                        candidates[doc_id] = indexer.documents[doc_id]

            # Compute BM25 for all candidates
            for doc_id in candidates:
                bm25 = RetrievalRanker.compute_bm25_score(
                    doc_id=doc_id,
                    keywords=parsed.keywords,
                    inverted_index=indexer.inverted_index,
                    doc_lengths=indexer.doc_lengths,
                    avg_doc_length=indexer.avg_doc_length,
                    total_docs=total_docs
                )
                bm25_scores[doc_id] = bm25

            # If no candidates found (empty query or unmatched keywords), load top alerts/transactions
            if not candidates:
                for doc in list(indexer.by_type.get("alert", []))[:20]:
                    candidates[doc.document_id] = doc
                    bm25_scores[doc.document_id] = 0.0

            # 3. Score and Rank all Candidates
            max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
            if max_bm25 <= 0.0:
                max_bm25 = 1.0

            ranked_results: List[RetrievalResult] = []
            for doc_id, doc in candidates.items():
                score, reasons = RetrievalRanker.rank_document(
                    doc=doc,
                    parsed_query=parsed,
                    bm25_score=bm25_scores.get(doc_id, 0.0),
                    max_bm25_score=max_bm25
                )

                # Include if score >= min_score or if it's an exact resolved entity
                is_exact = any(e.canonical_id == doc.entity_id for e in parsed.resolved_entities if e.confidence > 0)
                if score >= min_score or is_exact:
                    ranked_results.append(RetrievalResult(
                        document=doc,
                        relevance_score=score,
                        relevance_reasons=reasons,
                        provenance={
                            "source_table": doc.source_table,
                            "source_id": doc.source_id,
                            "query_intent": parsed.intent,
                            "scoring_factors": reasons
                        }
                    ))

            # 4. Sort descending by relevance score
            ranked_results.sort(key=lambda r: r.relevance_score, reverse=True)

            # 5. Apply limit
            limited_results = ranked_results[:limit]

            return parsed, limited_results

        finally:
            conn.close()

    def _expand_two_hop_candidates(self, ent: ResolvedEntity, candidates: Dict[str, RetrievalDocument]):
        """Traverses 2-hop edges for clusters (shared devices, mule senders)."""
        # Device -> co-using customers
        if ent.entity_type == "device":
            cluster_doc = indexer.documents.get(f"doc_rel_dev_{ent.canonical_id}")
            if cluster_doc:
                candidates[cluster_doc.document_id] = cluster_doc
                co_users = cluster_doc.structured_fields.get("customer_ids", [])
                for cuid in co_users[:5]:
                    for cdoc in indexer.by_customer.get(cuid, []):
                        candidates[cdoc.document_id] = cdoc

        # Beneficiary -> sender customers
        elif ent.entity_type == "beneficiary":
            mule_doc = indexer.documents.get(f"doc_rel_ben_{ent.canonical_id}")
            if mule_doc:
                candidates[mule_doc.document_id] = mule_doc
                senders = mule_doc.structured_fields.get("sender_ids", [])
                for suid in senders[:5]:
                    for sdoc in indexer.by_customer.get(suid, []):
                        candidates[sdoc.document_id] = sdoc

        # Customer -> device clusters
        elif ent.entity_type == "customer":
            # Check if customer uses any shared device
            for doc in indexer.by_customer.get(ent.canonical_id, []):
                if doc.entity_type == "device":
                    dev_id = doc.entity_id
                    rel_doc = indexer.documents.get(f"doc_rel_dev_{dev_id}")
                    if rel_doc:
                        candidates[rel_doc.document_id] = rel_doc


# Global hybrid retriever instance
retriever = HybridRetriever()
