"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Semantic Retrieval & Evidence Layer
-----------------------------------------------------------------------------
Exposes the modular hybrid retrieval engine, deterministic entity resolver,
indexer, explainable ranker, and standardized forensic evidence packet builder.
Zero LLM dependencies.
"""

from backend.app.retrieval.models import (
    RetrievalDocument,
    ResolvedEntity,
    ParsedQuery,
    EvidenceItem,
    EvidenceGap,
    RetrievalResult,
    StandardEvidencePacket
)
from backend.app.retrieval.entity_resolver import EntityResolver
from backend.app.retrieval.query_parser import QueryParser
from backend.app.retrieval.indexer import indexer, BankingIndexer
from backend.app.retrieval.ranking import RetrievalRanker
from backend.app.retrieval.retriever import retriever, HybridRetriever
from backend.app.retrieval.evidence_builder import evidence_builder, ForensicEvidenceBuilder

__all__ = [
    "RetrievalDocument",
    "ResolvedEntity",
    "ParsedQuery",
    "EvidenceItem",
    "EvidenceGap",
    "RetrievalResult",
    "StandardEvidencePacket",
    "EntityResolver",
    "QueryParser",
    "indexer",
    "BankingIndexer",
    "RetrievalRanker",
    "retriever",
    "HybridRetriever",
    "evidence_builder",
    "ForensicEvidenceBuilder"
]
