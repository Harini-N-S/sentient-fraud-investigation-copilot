"""
Deterministic Evaluation Schemas
-----------------------------------------------------------------------------
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TransactionEvaluationResponse(BaseModel):
    transaction_id: str = Field(..., description="Evaluated transaction ID")
    customer_id: str = Field(..., description="Customer ID")
    is_flagged: bool = Field(..., description="True if composite risk triggers threshold")
    risk_score: int = Field(..., description="Composite risk score [0 - 100]")
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    scenario_type: str = Field(..., description="Identified fraud scenario pattern")
    reason_summary: str = Field(..., description="Deterministic explanation of assessment")
    signals: List[Dict[str, Any]] = Field(default_factory=list, description="All fired deterministic signals")
    scoring_breakdown: List[Dict[str, Any]] = Field(default_factory=list, description="Contribution of each signal to total score")
    evidence_packet: Optional[Dict[str, Any]] = Field(None, description="Forensic evidence dossier")


class CustomerEvaluationResponse(BaseModel):
    customer_id: str = Field(..., description="Evaluated customer ID")
    evaluated_transactions_count: int = Field(..., description="Number of evaluated recent transactions")
    flagged_transactions_count: int = Field(..., description="Number of transactions flagged with risk")
    highest_risk_score: int = Field(..., description="Peak risk score observed")
    overall_severity: str = Field(..., description="Peak severity observed across evaluated transactions")
    total_signals_detected: int = Field(..., description="Total count of deterministic signals fired")
    transaction_evaluations: List[TransactionEvaluationResponse] = Field(default_factory=list, description="Detailed per-transaction evaluation results")
    contributing_signals: List[Dict[str, Any]] = Field(default_factory=list, description="Aggregated unique signals observed")
    summary: str = Field(..., description="Deterministic narrative summary of customer risk profile")
