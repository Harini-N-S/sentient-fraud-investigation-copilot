"""
Fraud Alert Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.signal import SignalSummary


class AlertSummary(BaseModel):
    alert_id: str = Field(..., description="Unique alert ID (ALT-XXXXX)")
    transaction_id: str = Field(..., description="Associated transaction ID")
    customer_id: str = Field(..., description="Target customer ID")
    account_id: str = Field(..., description="Source account ID")
    severity: str = Field(..., description="Alert severity: LOW, MEDIUM, HIGH, CRITICAL")
    composite_risk_score: int = Field(..., description="Calculated composite risk score [0 - 100]")
    status: str = Field(..., description="Investigation status")
    reason_summary: str = Field(..., description="Concise explanation of alert trigger")
    scenario_type: str = Field(..., description="Fraud typological pattern")
    assigned_analyst: Optional[str] = Field(None, description="Analyst assigned to review")
    created_at: str = Field(..., description="Alert generation timestamp")
    customer_name: Optional[str] = Field(None, description="Full customer name")
    transaction_amount_usd: Optional[float] = Field(None, description="Amount in USD equivalent")
    signal_count: Optional[int] = Field(None, description="Number of contributing signals")


class AlertDetail(BaseModel):
    alert: AlertSummary
    customer: Dict[str, Any] = Field(..., description="Customer profile summary")
    account: Dict[str, Any] = Field(..., description="Source account details")
    transaction: Dict[str, Any] = Field(..., description="Triggering transaction details")
    signals: List[SignalSummary] = Field(..., description="All triggered fraud signals")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Forensic evidence dossier")
    related_entities: Optional[List[Dict[str, Any]]] = Field(None, description="Directly related entities (device, beneficiary)")
