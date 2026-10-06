"""
Transaction Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.app.schemas.signal import SignalSummary


class TransactionSummary(BaseModel):
    transaction_id: str = Field(..., description="Unique transaction ID (TXN-XXXXX)")
    account_id: str = Field(..., description="Source account ID")
    customer_id: str = Field(..., description="Originating customer ID")
    beneficiary_id: str = Field(..., description="Destination beneficiary ID")
    device_id: str = Field(..., description="Originating device ID")
    channel: str = Field(..., description="Banking channel (e.g. IllicoCash_App)")
    transaction_type: str = Field(..., description="Type of transaction")
    amount: float = Field(..., description="Nominal transaction amount")
    currency: str = Field(..., description="CDF or USD")
    amount_usd_equivalent: float = Field(..., description="Amount converted to USD equivalent")
    location_city: str = Field(..., description="City where transaction occurred")
    status: str = Field(..., description="Transaction status")
    timestamp: str = Field(..., description="Transaction execution timestamp")
    customer_name: Optional[str] = Field(None, description="Customer name")
    beneficiary_name: Optional[str] = Field(None, description="Beneficiary name")


class TransactionDetail(BaseModel):
    transaction: TransactionSummary
    customer: Dict[str, Any] = Field(..., description="Originating customer identity")
    account: Dict[str, Any] = Field(..., description="Debited account status & balance")
    beneficiary: Dict[str, Any] = Field(..., description="Destination beneficiary record")
    device: Dict[str, Any] = Field(..., description="Originating device metadata")
    recent_auth_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Prior authentication events")
    fraud_signals: List[SignalSummary] = Field(default_factory=list, description="Historical database signals linked to this transaction")
    related_alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Associated alerts")
    deterministic_evaluation: Optional[Dict[str, Any]] = Field(None, description="Fresh deterministic rules engine evaluation")
    evidence_packet: Optional[Dict[str, Any]] = Field(None, description="3-Tier forensic evidence dossier")
