"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Schemas & Data Contracts
-----------------------------------------------------------------------------
Defines strict Pydantic schemas for Copilot investigation requests,
conversational session state, evidence references, and grounded 8-section
investigation responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class RiskAssessment(BaseModel):
    """
    Deterministic risk assessment preserved from the Phase 3 fraud engine.
    The LLM is NOT permitted to alter or invent official risk scores.
    """
    severity: str = Field(..., description="Official alert severity: CRITICAL, HIGH, MEDIUM, LOW, or NONE")
    risk_score: int = Field(..., ge=0, le=100, description="Deterministic composite risk score [0-100]")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Forensic confidence in assessment [0.0-1.0]")


class EvidenceReference(BaseModel):
    """
    Structured reference to an immutable database record or calculated metric.
    """
    source_id: str = Field(..., description="Primary identifier: TXN-00801, ALT-00001, AUTH-00389, DEV-00127, etc.")
    source_table: str = Field(..., description="Source database table: transactions, alerts, auth_activity, devices, etc.")
    field: Optional[str] = Field(None, description="Specific column or metric name if applicable")
    description: Optional[str] = Field(None, description="Brief description of the record")


class InvestigationEvidenceItem(BaseModel):
    """
    Individual factual supporting evidence claim grounded in retrieved data.
    """
    source_id: str = Field(..., description="Primary identifier supporting this claim")
    source_table: str = Field(..., description="Database table or calculation origin")
    statement: str = Field(..., description="Factual evidence statement")
    citation: str = Field(..., description="Formatted bracket citation: [Source: ID]")


class InvestigationCounterEvidenceItem(BaseModel):
    """
    Individual counter-evidence claim indicating legitimate activity or mitigating suspicion.
    Mandatory for false-positive evaluation and balanced investigation.
    """
    source_id: str = Field(..., description="Primary identifier supporting mitigation")
    source_table: str = Field(..., description="Source table: customers, baselines, auth_activity, devices, etc.")
    statement: str = Field(..., description="Mitigating fact statement")
    citation: str = Field(..., description="Formatted bracket citation: [Source: ID]")


class InvestigationGapItem(BaseModel):
    """
    Explicitly documented evidence gap preventing speculation.
    """
    gap_type: str = Field(..., description="Category of missing data: UNKNOWN_ENTITY, AMBIGUOUS_ENTITY, MISSING_BASELINE, NO_RELATED_ALERTS, etc.")
    description: str = Field(..., description="Detailed description of what is missing")
    impact: str = Field(..., description="Forensic impact on the investigation")


class CopilotInvestigationResponse(BaseModel):
    """
    Comprehensive structured forensic investigation response.
    Enforces the 8 required investigation sections with strict provenance grounding.
    """
    question: str = Field(..., description="The analyst question addressed")
    session_id: Optional[str] = Field(None, description="Conversational session identifier")
    resolved_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Resolved entity identifiers and types")
    
    # 1. SUMMARY
    summary: str = Field(..., description="Objective narrative of what occurred based strictly on retrieved facts")
    
    # RISK ASSESSMENT (Deterministic preservation)
    risk_assessment: RiskAssessment = Field(..., description="Authoritative risk assessment from Phase 3 deterministic engine")
    
    # 2. SUPPORTING EVIDENCE
    supporting_evidence: List[InvestigationEvidenceItem] = Field(default_factory=list, description="Evidence supporting fraud or anomaly hypothesis")
    
    # 3. COUNTER-EVIDENCE
    counter_evidence: List[InvestigationCounterEvidenceItem] = Field(default_factory=list, description="Evidence mitigating suspicion or supporting legitimate behavior")
    
    # 4. BEHAVIOURAL DEVIATION
    behavioural_deviation: List[str] = Field(default_factory=list, description="Comparison of activity against customer historical baseline")
    
    # 5. RELATED ACTIVITY
    related_activity: List[str] = Field(default_factory=list, description="Connected transactions, shared devices, mule beneficiaries, or linked alerts")
    
    # 6. EVIDENCE GAPS
    evidence_gaps: List[InvestigationGapItem] = Field(default_factory=list, description="Documented missing data points or unverified parameters")
    
    # 7. NEXT INVESTIGATION STEPS
    investigation_next_steps: List[str] = Field(default_factory=list, description="Specific grounded investigative recommendations for human analyst")
    
    # 8. ESCALATION RECOMMENDATION
    escalation_recommendation: str = Field(..., description="Evidence-backed recommendation regarding escalation to senior fraud officer / AML team")
    
    # SOURCE PROVENANCE
    source_references: List[EvidenceReference] = Field(default_factory=list, description="Deduplicated list of database records cited in the findings")
    
    # QUALITY & GROUNDING METADATA
    provenance_validated: bool = Field(True, description="True if all citations were strictly verified against evidence packet")
    invalid_citations_removed: List[str] = Field(default_factory=list, description="Any ungrounded citations detected and filtered out")
    ambiguity_detected: bool = Field(False, description="True if entity resolution encountered multiple candidate records")
    unknown_entity_detected: bool = Field(False, description="True if query referenced an unknown identifier")
    insufficient_evidence_detected: bool = Field(False, description="True if no suspicious activity or alerts exist for target")
    model_used: str = Field(..., description="Name of LLM or Mock adapter used for generation")
    processing_time_ms: float = Field(default=0.0, description="Pipeline execution duration in milliseconds")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CopilotInvestigateRequest(BaseModel):
    """
    Request payload for Copilot investigation.
    """
    question: str = Field(..., min_length=3, max_length=1000, description="Analyst investigation question")
    session_id: Optional[str] = Field(None, description="Optional conversation session ID to maintain investigation context")
    entity_type: Optional[str] = Field(None, description="Optional explicit entity type override (customer, transaction, alert, device)")
    entity_id: Optional[str] = Field(None, description="Optional explicit entity identifier override (e.g. CUS-00014, TXN-00801)")
    use_mock: Optional[bool] = Field(None, description="Force use mock adapter (defaults to settings.copilot_use_mock or False)")


class CopilotExplainEntityRequest(BaseModel):
    """
    Request payload for targeted entity explanation endpoints.
    """
    session_id: Optional[str] = Field(None, description="Optional conversational session ID")
    use_mock: Optional[bool] = Field(None, description="Force use mock adapter")
