"""
System Overview Schemas
-----------------------------------------------------------------------------
Aggregate metrics for the future Sentient Command Centre dashboard.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class AlertSeverityBreakdown(BaseModel):
    critical: int = Field(0, description="Count of CRITICAL alerts")
    high: int = Field(0, description="Count of HIGH alerts")
    medium: int = Field(0, description="Count of MEDIUM alerts")
    low: int = Field(0, description="Count of LOW alerts")


class OverviewResponse(BaseModel):
    total_customers: int = Field(..., description="Total synthetic customers")
    total_accounts: int = Field(..., description="Total synthetic accounts")
    total_transactions: int = Field(..., description="Total recorded transactions")
    total_alerts: int = Field(..., description="Total generated fraud alerts")
    total_fraud_signals: int = Field(..., description="Total detected rule signals")
    critical_alerts: int = Field(..., description="Total CRITICAL severity alerts")
    high_alerts: int = Field(..., description="Total HIGH severity alerts")
    medium_alerts: int = Field(..., description="Total MEDIUM severity alerts")
    low_alerts: int = Field(..., description="Total LOW severity alerts")
    alerts_by_status: Dict[str, int] = Field(..., description="Alert counts broken down by triage status")
    total_volume_usd: float = Field(..., description="Total transaction volume in USD equivalent")
    total_flagged_volume_usd: float = Field(..., description="Total volume of alerted transactions in USD")
    known_mules_count: int = Field(..., description="Count of known mule beneficiary accounts")
    suspicious_devices_count: int = Field(..., description="Count of blacklisted or suspicious devices")
    alerts_by_scenario: Dict[str, int] = Field(default_factory=dict, description="Alert counts broken down by scenario")
    top_mule_beneficiaries: List[Dict[str, Any]] = Field(default_factory=list, description="Top mule beneficiaries by incoming volume")
    generated_at: str = Field(..., description="Timestamp of metric calculation")
