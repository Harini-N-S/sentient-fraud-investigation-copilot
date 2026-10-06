"""
Search Router
-----------------------------------------------------------------------------
GET /api/search?q=...
Unified deterministic and hybrid search engine across customers, accounts,
transactions, devices, beneficiaries, and alerts.
Zero LLM hallucination.
"""

import sqlite3
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from backend.app.database import get_db
from backend.app.repositories.search_repo import SearchRepository
from backend.app.retrieval import retriever
from backend.app.schemas.search import SearchResponse, SearchResultItem

router = APIRouter(prefix="/api/search", tags=["Unified Search"])


@router.get("", response_model=SearchResponse, summary="Unified Multi-Entity Search")
def search_entities(
    q: str = Query(..., min_length=1, description="Search query string (e.g. CUS-00014, iPhone, 4800, Kinshasa)"),
    entity_type: Optional[str] = Query(None, description="Optional entity filter: customer, account, transaction, device, beneficiary, alert"),
    severity: Optional[str] = Query(None, description="Optional severity filter: LOW, MEDIUM, HIGH, CRITICAL"),
    scenario: Optional[str] = Query(None, description="Optional fraud scenario filter: ATO_DRAIN, IMPOSSIBLE_TRAVEL, etc."),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of search results to return"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Executes fast, deterministic multi-table search across:
    - Customers (ID, name, phone, email)
    - Accounts (ID, owner, balance)
    - Transactions (ID, amount, city)
    - Devices (ID, model, IP, city)
    - Beneficiaries (ID, name, institution, phone/account)
    - Alerts (ID, scenario, reason summary)
    Prioritizes exact ID matches, prefix matches, and attaches explainable ranking reasons.
    """
    clean_q = q.strip()

    # If advanced filters are provided, execute hybrid retrieval
    if entity_type or severity or scenario:
        filters = {}
        if severity:
            filters["severity"] = severity
        if scenario:
            filters["scenario_type"] = scenario

        _, results = retriever.retrieve(
            query=clean_q,
            entity_type=entity_type,
            filters=filters,
            limit=limit
        )

        search_items = []
        for r in results:
            doc = r.document
            search_items.append(SearchResultItem(
                entity_type=doc.entity_type,
                entity_id=doc.entity_id,
                title=doc.title,
                subtitle=doc.text[:120] + "...",
                match_field="hybrid_index",
                match_value=clean_q,
                details=doc.structured_fields,
                relevance_score=r.relevance_score,
                relevance_reasons=r.relevance_reasons
            ))

        return SearchResponse(
            query=clean_q,
            total_results=len(search_items),
            results=search_items
        )

    # Standard fast multi-table database search
    results = SearchRepository.search_all(db=db, query=clean_q, limit=limit)
    items: List[SearchResultItem] = []

    for r in results:
        # Compute baseline explainable score and reasons
        is_exact = (r["entity_id"].lower() == clean_q.lower())
        score = 1.0 if is_exact else 0.75
        reasons = ["exact_identifier_match"] if is_exact else [f"matched_{r['match_field']}"]

        item = SearchResultItem(
            entity_type=r["entity_type"],
            entity_id=r["entity_id"],
            title=r["title"],
            subtitle=r["subtitle"],
            match_field=r["match_field"],
            match_value=r["match_value"],
            details=r.get("details", {}),
            relevance_score=score,
            relevance_reasons=reasons
        )
        items.append(item)

    return SearchResponse(
        query=clean_q,
        total_results=len(items),
        results=items
    )
