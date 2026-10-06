"""
Entity Relationships & Evidence Router
-----------------------------------------------------------------------------
GET /api/entities/{entity_type}/{entity_id}/relationships
GET /api/entities/{entity_type}/{entity_id}/evidence
GET /api/entities/{entity_type}/{entity_id}/related
Explores 1-hop and 2-hop topological connections and constructs grounded
forensic evidence dossiers across customers, accounts, transactions,
devices, beneficiaries, and alerts.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.repositories.entity_repo import EntityRepository
from backend.app.schemas.entity import EntityRelationshipsResponse
from backend.app.schemas.retrieval import RelatedEntitiesResponse
from backend.app.retrieval import evidence_builder, EntityResolver
from backend.app.retrieval.models import StandardEvidencePacket

router = APIRouter(prefix="/api/entities", tags=["Entities & Graph Relationships"])


@router.get(
    "/{entity_type}/{entity_id}/relationships",
    response_model=EntityRelationshipsResponse,
    summary="Explore Entity Graph Relationships"
)
def get_entity_relationships(
    entity_type: str,
    entity_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Computes graph-style relational links across the banking topology.
    Supports entity types: customer, account, transaction, device, beneficiary, alert.
    Discovers:
    - Direct connections (e.g. customer -> accounts, customer -> devices, customer -> beneficiaries)
    - 2-hop shared connections (e.g. other customers sharing the same device, other customers paying the same mule)
    All relationships are deterministically calculated from database foreign keys.
    """
    try:
        relationships = EntityRepository.get_entity_relationships(
            db=db,
            entity_type=entity_type,
            entity_id=entity_id.strip()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    if not relationships:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_type.capitalize()} with ID '{entity_id}' was not found in the database."
        )

    return EntityRelationshipsResponse(**relationships)


@router.get(
    "/{entity_type}/{entity_id}/evidence",
    response_model=StandardEvidencePacket,
    summary="Get Standardized Forensic Evidence Packet for Entity"
)
def get_entity_evidence(
    entity_type: str,
    entity_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Constructs the standardized forensic evidence packet for ANY supported banking entity:
    - customer: 360 profile, accounts, baseline, devices, auth history, transactions, alerts, and mitigating factors.
    - transaction: ledger entry, sender, recipient, device, triggered rules, and alerts.
    - alert: composite score, lifecycle, reason, signals, and underlying transaction.
    - device: hardware specs, trust status, and co-users sharing the device.
    - beneficiary: counterparty specs, mule flag, sender aggregation, and volume.
    - account: ledger balances, ownership, and activity.
    """
    clean_type = entity_type.lower().strip()
    valid_types = {"customer", "account", "transaction", "device", "beneficiary", "alert"}
    if clean_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported entity type '{entity_type}'. Must be one of: {sorted(list(valid_types))}"
        )

    resolved = EntityResolver.resolve_single(db, clean_type, entity_id.strip())
    if resolved.confidence == 0.0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{clean_type.capitalize()} with ID '{entity_id}' was not found in the database; cannot assemble evidence packet."
        )

    packet = evidence_builder.build_for_entity(clean_type, resolved.canonical_id)
    return packet


@router.get(
    "/{entity_type}/{entity_id}/related",
    response_model=RelatedEntitiesResponse,
    summary="Get Controlled Related Entities"
)
def get_related_entities(
    entity_type: str,
    entity_id: str,
    max_depth: int = Query(2, ge=1, le=3, description="Maximum traversal depth (1 or 2 hops)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum related items to return"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Controlled relationship traversal endpoint.
    Retrieves bounded 1-hop and 2-hop related entities without recursive graph explosion.
    """
    clean_type = entity_type.lower().strip()
    valid_types = {"customer", "account", "transaction", "device", "beneficiary", "alert"}
    if clean_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported entity type '{entity_type}'. Must be one of: {sorted(list(valid_types))}"
        )

    resolved = EntityResolver.resolve_single(db, clean_type, entity_id.strip())
    if resolved.confidence == 0.0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{clean_type.capitalize()} with ID '{entity_id}' was not found in the database."
        )

    relationships = EntityRepository.get_entity_relationships(
        db=db,
        entity_type=clean_type,
        entity_id=resolved.canonical_id
    )

    if not relationships:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{clean_type.capitalize()} with ID '{entity_id}' was not found in the database."
        )

    direct = relationships.get("relationships", [])[:limit]
    second_hop = relationships.get("second_hop_relationships", [])[:limit] if max_depth >= 2 else []
    total = len(direct) + len(second_hop)

    summary = (
        f"Entity {clean_type.upper()} {resolved.canonical_id} has {len(direct)} direct 1-hop connections "
        f"and {len(second_hop)} 2-hop shared cluster connections within max depth {max_depth}."
    )

    return RelatedEntitiesResponse(
        entity_type=clean_type,
        entity_id=entity_id,
        canonical_id=resolved.canonical_id,
        max_depth=max_depth,
        total_relationships=total,
        direct_relationships=direct,
        second_hop_relationships=second_hop,
        summary=summary
    )
