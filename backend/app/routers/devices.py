"""
Devices Router
-----------------------------------------------------------------------------
Endpoints for querying device hardware fingerprints, trust status, and shared device networks.
"""

import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from backend.app.database import get_db
from backend.app.dependencies.deps import get_pagination_params
from backend.app.repositories.device_repo import DeviceRepository
from backend.app.schemas.device import DeviceSummary, DeviceDetail
from backend.app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.get("", response_model=PaginatedResponse[DeviceSummary], summary="List & Filter Devices")
def list_devices(
    device_type: Optional[str] = Query(None, description="Mobile_Android, Mobile_iOS, Desktop_Windows, Desktop_Mac"),
    trust_status: Optional[str] = Query(None, description="Trusted_Enrolled, New_Unverified, Suspicious_Blacklisted"),
    is_vpn_or_tor: Optional[int] = Query(None, description="1 if VPN/proxy, 0 if clean ISP"),
    is_rooted_jailbroken: Optional[int] = Query(None, description="1 if rooted/jailbroken, 0 if clean OS"),
    search: Optional[str] = Query(None, description="Search by device ID, model, IP address, or city"),
    sort_by: str = Query("last_seen_timestamp", description="Sort field: last_seen_timestamp, first_seen_timestamp, device_id"),
    sort_order: str = Query("DESC", description="Sort direction: ASC or DESC"),
    pagination: dict = Depends(get_pagination_params),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves paginated devices with filtering by hardware type, security flags, and location.
    """
    items, meta = DeviceRepository.get_devices(
        db=db,
        page=pagination["page"],
        page_size=pagination["page_size"],
        device_type=device_type,
        trust_status=trust_status,
        is_vpn_or_tor=is_vpn_or_tor,
        is_rooted_jailbroken=is_rooted_jailbroken,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return PaginatedResponse(
        items=[DeviceSummary(**item) for item in items],
        pagination=meta
    )


@router.get("/{device_id}", response_model=DeviceDetail, summary="Get Device Forensic Detail")
def get_device_detail(
    device_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Retrieves device profile, associated customers (for shared device analysis),
    transaction volumes, recent auth challenges, and linked alerts/signals.
    """
    detail = DeviceRepository.get_device_detail(db, device_id.strip())
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID '{device_id}' was not found in the database."
        )

    return DeviceDetail(**detail)
