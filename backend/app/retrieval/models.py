"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Semantic Retrieval & Evidence Layer - Data Models
-----------------------------------------------------------------------------
Defines normalized retrieval documents, resolved entities, parsed queries,
explainable ranking results, evidence items with strict provenance,
evidence gaps, and standardized forensic evidence packets.
Zero LLM dependencies.
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RetrievalDocument(BaseModel):
    """
    Normalized retrieval document generated from structured banking tables.
    Each document captures essential context for investigation and retrieval.
    """
    document_id: str = Field(..., description="Unique document ID (e.g. doc_cus_CUS-00014, doc_txn_TXN-00801)")
    entity_type: str = Field(..., description="customer, account, transaction, device, beneficiary, auth_activity, behavioural_baseline, alert, fraud_signal, rule_evidence, relationship")
    entity_id: str = Field(..., description="Primary entity identifier")
    title: str = Field(..., description="Human-readable title")
    source_table: str = Field(..., description="Underlying database table name")
    source_id: str = Field(..., description="Primary key value in source table")
    timestamp: Optional[str] = Field(None, description="Event or creation timestamp in ISO 8601")
    text: str = Field(..., description="Comprehensive grounded text representation")
    structured_fields: Dict[str, Any] = Field(default_factory=dict, description="Exact key-value attributes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Indexed metadata for fast filtering")


class ResolvedEntity(BaseModel):
    """
    Output of deterministic entity resolution.
    Captures entity identity, confidence, matching method, and candidate ambiguity.
    """
    entity_type: str = Field(..., description="Entity type: customer, account, transaction, device, beneficiary, alert, signal")
    entity_id: str = Field(..., description="Extracted or resolved identifier")
    canonical_id: str = Field(..., description="Normalized database primary key (e.g. CUS-00014)")
    confidence: float = Field(..., description="Resolution confidence [0.0 - 1.0]")
    matching_method: str = Field(..., description="exact_id, normalized_id, exact_name, name_substring, alias_pattern, ambiguous_match, unknown_identifier")
    matched_text: str = Field(..., description="Original text fragment that triggered the match")
    is_ambiguous: bool = Field(False, description="True if multiple entities match the same reference")
    candidates: List[Dict[str, Any]] = Field(default_factory=list, description="Candidate entities when ambiguous")
    details: Optional[Dict[str, Any]] = Field(None, description="Basic profile details of resolved entity")


class ParsedQuery(BaseModel):
    """
    Output of deterministic query parser.
    Extracts query intent, recognized entities, attribute filters, and keywords.
    """
    raw_query: str = Field(..., description="Original user or copilot query")
    normalized_query: str = Field(..., description="Cleaned and tokenized query")
    intent: str = Field(..., description="INVESTIGATE_ENTITY, FIND_RELATIONSHIPS, FILTER_TRANSACTIONS, FILTER_ALERTS, SCENARIO_SEARCH, GENERAL_SEARCH")
    resolved_entities: List[ResolvedEntity] = Field(default_factory=list, description="Entities recognized in the query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Extracted filters: severity, scenario, rule_code, city, channel, currency, etc.")
    keywords: List[str] = Field(default_factory=list, description="Content keywords for lexical matching")
    is_relational: bool = Field(False, description="True if query explicitly asks for relationship links or networks")
    relationship_target: Optional[str] = Field(None, description="Target relationship: devices, beneficiaries, co_users, transactions, alerts")


class EvidenceItem(BaseModel):
    """
    Individual evidence datum maintaining strict provenance to the SQLite database.
    """
    type: str = Field(..., description="EXACT_DATA, CALCULATED, RETRIEVED_EVIDENCE, COUNTER_EVIDENCE")
    source_table: str = Field(..., description="Database table or calculation engine name")
    source_id: str = Field(..., description="Source record primary key")
    field: str = Field(..., description="Specific column or metric name")
    value: Any = Field(..., description="Actual data value (number, string, boolean, etc.)")
    description: str = Field(..., description="Human-readable explanation of this evidence item")
    timestamp: Optional[str] = Field(None, description="Timestamp associated with this evidence")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Audit provenance details (query, parameters, formula)")


class EvidenceGap(BaseModel):
    """
    Explicitly identifies absent or insufficient evidence instead of fabricating assumptions.
    """
    gap_type: str = Field(..., description="MISSING_BASELINE, UNVERIFIED_DEVICE, LACK_OF_AUTH_RECORDS, INSUFFICIENT_TRANSACTION_HISTORY, AMBIGUOUS_ENTITY, INSUFFICIENT_EVIDENCE_FOR_ATO, UNKNOWN_ENTITY, NO_RELATED_ALERTS")
    description: str = Field(..., description="Clear explanation of what evidence is missing")
    impact: str = Field(..., description="How this missing evidence affects forensic confidence")
    missing_sources: List[str] = Field(default_factory=list, description="Tables or logs checked where evidence was absent")


class RetrievalResult(BaseModel):
    """
    Individual ranked search/retrieval result with explainable scoring.
    """
    document: RetrievalDocument = Field(..., description="Retrieved normalized document")
    relevance_score: float = Field(..., description="Explainable relevance score [0.0 - 1.0]")
    relevance_reasons: List[str] = Field(default_factory=list, description="Specific deterministic factors driving the score")
    provenance: Dict[str, Any] = Field(default_factory=dict, description="Source provenance metadata")


class StandardEvidencePacket(BaseModel):
    """
    Comprehensive standardized forensic evidence packet.
    Follows strict 4-category taxonomy with provenance and explicit evidence gaps.
    """
    query: str = Field(..., description="Original investigation query")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    target_entity: Optional[Dict[str, Any]] = Field(None, description="Primary resolved target entity if applicable")
    resolved_entities: List[ResolvedEntity] = Field(default_factory=list)
    exact_data: List[EvidenceItem] = Field(default_factory=list, description="Tier 1: Immutable database records with field-level provenance")
    calculated_information: List[EvidenceItem] = Field(default_factory=list, description="Tier 2: Mathematical formulas, ratios, velocity scores")
    retrieved_evidence: List[EvidenceItem] = Field(default_factory=list, description="Tier 3: Graph linkages, historical baselines, logs, alerts")
    counter_evidence: List[EvidenceItem] = Field(default_factory=list, description="Mitigating facts supporting false-positive or legitimate behavior")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="Bounded graph connections (1-hop and 2-hop)")
    evidence_gaps: List[EvidenceGap] = Field(default_factory=list, description="Explicitly documented missing data points")
    source_references: List[Dict[str, Any]] = Field(default_factory=list, description="Deduplicated list of database records cited")
    relevance_metadata: Dict[str, Any] = Field(default_factory=dict, description="Scoring and expansion limits used")
    deterministic_summary: Optional[str] = Field(None, description="Deterministic rule-based summary without LLM hallucinations")
