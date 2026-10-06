"""
Entity Relationship Schemas
-----------------------------------------------------------------------------
Supports multi-hop link analysis across customers, accounts, transactions, devices, beneficiaries, and alerts.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EntityNode(BaseModel):
    entity_type: str = Field(..., description="customer, account, transaction, device, beneficiary, alert")
    entity_id: str = Field(..., description="Unique entity ID")
    label: str = Field(..., description="Human-readable node label / name")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Key node attributes")


class EntityEdge(BaseModel):
    source_type: str = Field(..., description="Source entity type")
    source_id: str = Field(..., description="Source entity ID")
    relationship: str = Field(..., description="Relationship predicate (e.g. OWNS, USES, TRANSFERS_TO, TRIGGERS)")
    target_type: str = Field(..., description="Target entity type")
    target_id: str = Field(..., description="Target entity ID")
    target_label: str = Field(..., description="Human-readable target label")
    direction: str = Field("outgoing", description="outgoing / incoming / bidirectional")
    details: Dict[str, Any] = Field(default_factory=dict, description="Relationship metadata (e.g. amount, count)")


class EntityRelationshipsResponse(BaseModel):
    entity_type: str = Field(..., description="Queried entity type")
    entity_id: str = Field(..., description="Queried entity ID")
    root_entity: Optional[Dict[str, Any]] = Field(None, description="Root node attributes")
    total_relationships: int = Field(..., description="Number of direct and derived links")
    relationships: List[EntityEdge] = Field(default_factory=list, description="List of graph links")
    second_hop_links: List[EntityEdge] = Field(default_factory=list, description="Shared multi-hop links (e.g. other customers sharing device)")
