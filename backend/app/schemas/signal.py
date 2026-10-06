"""
Fraud Signal Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SignalSummary(BaseModel):
    signal_id: str = Field(..., description="Unique signal identifier")
    alert_id: str = Field(..., description="Associated alert ID")
    transaction_id: str = Field(..., description="Associated transaction ID")
    rule_code: str = Field(..., description="Deterministic rule code (e.g. R-VEL-01)")
    rule_name: str = Field(..., description="Descriptive rule name")
    rule_category: str = Field(..., description="Fraud category classification")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    confidence_score: float = Field(..., description="Rule firing confidence [0.0 - 1.0]")
    signal_description: str = Field(..., description="Deterministic forensic rationale")
    created_at: str = Field(..., description="Signal generation timestamp")


class SignalDetail(BaseModel):
    signal: SignalSummary
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    transaction_amount_usd: Optional[float] = None
    transaction_city: Optional[str] = None
    alert_severity: Optional[str] = None
    alert_status: Optional[str] = None
    calculated_values: Optional[Dict[str, Any]] = None
    evidence: Optional[Dict[str, Any]] = None
