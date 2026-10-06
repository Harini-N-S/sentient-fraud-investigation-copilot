"""
Customer Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CustomerSummary(BaseModel):
    customer_id: str = Field(..., description="Unique customer ID (CUS-XXXXX)")
    full_name: str = Field(..., description="Customer full legal name")
    customer_segment: str = Field(..., description="Retail, SME, Corporate, HNWI, AgencyBankingOperator")
    kyc_status: str = Field(..., description="KYC compliance tier")
    primary_phone: str = Field(..., description="Primary MSISDN")
    email: str = Field(..., description="Primary email address")
    registered_city: str = Field(..., description="DRC registered domicile city")
    risk_category: str = Field(..., description="Baseline risk category: Low, Medium, High")
    created_at: str = Field(..., description="Onboarding timestamp")
    registration_date: Optional[str] = Field(None, description="Alias for onboarding timestamp")
    is_active: bool = Field(True, description="Active account status")
    account_count: Optional[int] = Field(None, description="Number of linked accounts")
    total_balance_usd: Optional[float] = Field(None, description="Aggregate balance across accounts in USD")


class CustomerDossier(BaseModel):
    customer: CustomerSummary
    accounts: List[Dict[str, Any]] = Field(default_factory=list, description="All customer accounts")
    activity_summary: Dict[str, Any] = Field(..., description="Lifetime transaction volume, frequency, and metrics")
    recent_transactions: List[Dict[str, Any]] = Field(default_factory=list, description="Latest transaction history")
    behavioural_baseline: Optional[Dict[str, Any]] = Field(None, description="Historical behavioural baseline profile")
    devices: List[Dict[str, Any]] = Field(default_factory=list, description="Associated devices")
    beneficiaries: List[Dict[str, Any]] = Field(default_factory=list, description="Interacted beneficiaries")
    recent_auth_events: List[Dict[str, Any]] = Field(default_factory=list, description="Recent authentication audit trail")
    risk: Dict[str, Any] = Field(..., description="Alerts, signals, and calculated risk metrics")
    relationships: Dict[str, Any] = Field(..., description="Shared devices, shared beneficiaries, network links")
