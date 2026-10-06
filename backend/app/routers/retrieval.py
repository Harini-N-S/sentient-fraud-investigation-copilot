"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Retrieval Router
-----------------------------------------------------------------------------
Dedicated endpoints for semantic retrieval, explainable document ranking,
and standardized forensic evidence packet generation.
Zero LLM dependencies.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.retrieval import RetrievalQueryRequest, RetrievalQueryResponse
from backend.app.retrieval import retriever, evidence_builder, indexer
from backend.app.retrieval.models import RetrievalDocument

router = APIRouter(prefix="/api/retrieval", tags=["Semantic Retrieval & Evidence"])


@router.post(
    "/query",
    response_model=RetrievalQueryResponse,
    summary="Query Semantic Retrieval & Evidence Layer"
)
def query_retrieval(request: RetrievalQueryRequest):
    """
    Retrieves grounded evidence from the synthetic banking database.
    - Resolves customer, account, transaction, device, beneficiary, alert, and signal entities.
    - Fuses exact matching, metadata filtering, inverted-index BM25 lexical similarity, and graph traversals.
    - Explains ranking reasons for every returned result.
    - Generates a standardized 4-tier grounded evidence packet with field-level provenance and explicit evidence gaps.
    """
    parsed_query, results = retriever.retrieve(
        query=request.query,
        entity_type=request.entity_type,
        entity_id=request.entity_id,
        filters=request.filters,
        limit=request.limit,
        max_depth=request.relationship_depth
    )

    evidence_packet = None
    if request.include_evidence_packet:
        evidence_packet = evidence_builder.build_for_query(
            query=request.query,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            filters=request.filters,
            max_depth=request.relationship_depth
        )

    return RetrievalQueryResponse(
        query=request.query,
        intent=parsed_query.intent,
        total_retrieved=len(results),
        resolved_entities=parsed_query.resolved_entities,
        results=results,
        evidence_packet=evidence_packet
    )


@router.get(
    "/documents/{document_id}",
    response_model=RetrievalDocument,
    summary="Get Normalized Retrieval Document"
)
def get_document(document_id: str):
    """Retrieves a normalized grounded retrieval document by unique document ID."""
    indexer.ensure_indexed()
    doc = indexer.documents.get(document_id.strip())
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retrieval document with ID '{document_id}' was not found in the index."
        )
    return doc
