"""
Beneficiary Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BeneficiarySummary(BaseModel):
    beneficiary_id: str = Field(..., description="Unique beneficiary ID (BEN-XXXXX)")
    beneficiary_name: str = Field(..., description="Legal or registered beneficiary name")
    institution_name: str = Field(..., description="Bank or telco wallet institution")
    account_or_phone: str = Field(..., description="Account number or MSISDN")
    beneficiary_type: str = Field(..., description="Individual_Peer, Merchant_Store, Corporate_Vendor, Mobile_Money_Agent")
    registered_city: str = Field(..., description="Registered city")
    is_known_mule: int = Field(..., description="1 if confirmed or tagged as mule, else 0")
    created_at: str = Field(..., description="Record creation timestamp")
    interacting_customer_count: Optional[int] = Field(None, description="Number of distinct customer senders")
    total_volume_usd: Optional[float] = Field(None, description="Total incoming volume received in USD")


class BeneficiaryDetail(BaseModel):
    beneficiary: BeneficiarySummary
    interacting_customers: List[Dict[str, Any]] = Field(default_factory=list, description="Customers who sent funds to this beneficiary")
    transaction_count: int = Field(..., description="Total transactions received")
    total_volume_usd: float = Field(..., description="Total USD volume received")
    recent_transactions: List[Dict[str, Any]] = Field(default_factory=list, description="Recent incoming transactions")
    related_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Alerts associated with this beneficiary")
    related_signals: List[Dict[str, Any]] = Field(default_factory=list, description="Signals associated with this beneficiary")
