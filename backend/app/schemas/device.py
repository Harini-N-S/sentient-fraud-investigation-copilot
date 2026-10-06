"""
Device Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DeviceSummary(BaseModel):
    device_id: str = Field(..., description="Unique device ID (DEV-XXXXX)")
    primary_customer_id: str = Field(..., description="Customer who enrolled or primarily uses this device")
    device_type: str = Field(..., description="Device category (e.g. Mobile_Android)")
    device_model: str = Field(..., description="Hardware model name")
    os_version: str = Field(..., description="Operating system version")
    device_fingerprint_hash: str = Field(..., description="Cryptographic hardware fingerprint")
    ip_address: str = Field(..., description="Last observed IP address")
    ip_city: str = Field(..., description="Geo-located IP city")
    is_vpn_or_tor: int = Field(..., description="1 if proxy/VPN/Tor detected, else 0")
    is_rooted_jailbroken: int = Field(..., description="1 if OS compromise detected, else 0")
    trust_status: str = Field(..., description="Trusted_Enrolled, New_Unverified, Suspicious_Blacklisted")
    first_seen_timestamp: str = Field(..., description="First observed activity timestamp")
    last_seen_timestamp: str = Field(..., description="Most recent activity timestamp")
    associated_customer_count: Optional[int] = Field(None, description="Number of distinct customers using this device")


class DeviceDetail(BaseModel):
    device: DeviceSummary
    associated_customers: List[Dict[str, Any]] = Field(default_factory=list, description="All customers who transacted on this device")
    transaction_count: int = Field(..., description="Total transactions originating from this device")
    total_volume_usd: float = Field(..., description="Total USD volume transacted on this device")
    recent_transactions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent transactions executed")
    recent_auth_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent logins and auth challenges")
    related_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Alerts triggered on this device")
    related_signals: List[Dict[str, Any]] = Field(default_factory=list, description="Fraud signals citing this device")
