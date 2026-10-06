"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Retrieval & Evidence API Schemas
-----------------------------------------------------------------------------
Pydantic v2 schemas for the semantic retrieval and forensic evidence layer.
Zero LLM dependencies.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.retrieval.models import (
    RetrievalDocument,
    ResolvedEntity,
    RetrievalResult,
    StandardEvidencePacket
)


class RetrievalQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Investigation search or query string")
    entity_type: Optional[str] = Field(None, description="Optional entity type filter (customer, account, transaction, device, beneficiary, alert)")
    entity_id: Optional[str] = Field(None, description="Optional target entity ID")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata filters (severity, scenario_type, rule_code, city, channel, currency)")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of retrieved documents to return")
    include_evidence_packet: bool = Field(True, description="Whether to assemble and return a standardized forensic evidence packet")
    relationship_depth: int = Field(2, ge=1, le=3, description="Maximum graph relationship traversal depth (1-hop or 2-hop)")


class RetrievalQueryResponse(BaseModel):
    query: str = Field(..., description="Original query string")
    intent: str = Field(..., description="Classified deterministic query intent")
    total_retrieved: int = Field(..., description="Number of ranked retrieval documents returned")
    resolved_entities: List[ResolvedEntity] = Field(default_factory=list, description="Entities recognized and resolved from database")
    results: List[RetrievalResult] = Field(default_factory=list, description="Ranked retrieval documents with explainable scoring")
    evidence_packet: Optional[StandardEvidencePacket] = Field(None, description="Standardized grounded forensic evidence packet")


class RelatedEntitiesResponse(BaseModel):
    entity_type: str = Field(..., description="Root entity type")
    entity_id: str = Field(..., description="Root entity ID")
    canonical_id: str = Field(..., description="Canonical entity ID")
    max_depth: int = Field(..., description="Max traversal depth evaluated")
    total_relationships: int = Field(..., description="Total direct and second-hop edges found")
    direct_relationships: List[Dict[str, Any]] = Field(default_factory=list, description="1-hop direct relational links")
    second_hop_relationships: List[Dict[str, Any]] = Field(default_factory=list, description="2-hop shared cluster links (shared devices, mule senders)")
    summary: str = Field(..., description="Deterministic relationship summary")
