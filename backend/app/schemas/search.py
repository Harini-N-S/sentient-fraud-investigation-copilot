"""
Deterministic Search Schemas
-----------------------------------------------------------------------------
Zero LLM. Deterministic database search across customer, account, transaction,
device, beneficiary, and alert entities with explainable ranking.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    entity_type: str = Field(..., description="customer, account, transaction, device, beneficiary, alert")
    entity_id: str = Field(..., description="Unique entity identifier")
    title: str = Field(..., description="Primary display title")
    subtitle: str = Field(..., description="Secondary descriptive information")
    match_field: str = Field(..., description="Column or attribute matched (e.g. customer_id, full_name, etc.)")
    match_value: str = Field(..., description="Matching text or fragment")
    details: Dict[str, Any] = Field(default_factory=dict, description="Key attributes for UI quick card rendering")
    relevance_score: Optional[float] = Field(None, description="Deterministic explainable relevance score [0.0 - 1.0]")
    relevance_reasons: Optional[List[str]] = Field(default_factory=list, description="Specific ranking factors")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query string")
    total_results: int = Field(..., description="Total matches found across entity types")
    results: List[SearchResultItem] = Field(default_factory=list, description="Ranked deterministic match list")
