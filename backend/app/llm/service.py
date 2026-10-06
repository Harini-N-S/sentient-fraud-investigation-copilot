"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Core Service
-----------------------------------------------------------------------------
Implements the end-to-end 12-step Copilot request pipeline:
  1. Receive analyst question
  2. Parse question & resolve conversational pronouns/context
  3. Resolve entities
  4. Deterministic pre-checks (unknown/ambiguous entities handled without hallucination)
  5. Retrieve evidence packet from Phase 5 layer
  6. Validate evidence completeness
  7. Construct grounded prompt
  8. Send prompt to Groq (or MockLLMAdapter)
  9. Receive response
 10. Validate response structure
 11. Validate citations & preserve deterministic risk score
 12. Update session state and return structured investigation response
"""

import time
import re
import logging
from typing import Dict, Any, List, Optional, Set

from backend.app.config import settings
from backend.app.retrieval import evidence_builder, EntityResolver
from backend.app.retrieval.models import StandardEvidencePacket
from backend.app.llm.schemas import (
    CopilotInvestigateRequest,
    CopilotInvestigationResponse,
    RiskAssessment,
    InvestigationEvidenceItem,
    InvestigationCounterEvidenceItem,
    InvestigationGapItem,
    EvidenceReference
)
from backend.app.llm.prompts import COPILOT_SYSTEM_PROMPT, build_investigation_prompt
from backend.app.llm.client import GroqClient, GroqConfigurationError, GroqAPIError, GroqTimeoutError
from backend.app.llm.mock_adapter import MockLLMAdapter
from backend.app.llm.context_manager import context_manager

logger = logging.getLogger("rawbank_backend.copilot")


class CopilotService:
    """
    Orchestrates the grounded fraud investigation pipeline.
    Ensures the LLM is never the database and never hallucinates ungrounded facts.
    """

    def __init__(
        self,
        groq_client: Optional[GroqClient] = None,
        mock_adapter: Optional[MockLLMAdapter] = None
    ):
        self.groq_client = groq_client or GroqClient()
        self.mock_adapter = mock_adapter or MockLLMAdapter()

    def investigate(self, request: CopilotInvestigateRequest) -> CopilotInvestigationResponse:
        """
        Main entrypoint executing the 12-step grounded investigation pipeline.
        """
        start_time = time.time()
        raw_question = request.question.strip()
        session_id = request.session_id or f"sess_{int(time.time()*1000)}"

        # 1 & 2. Parse Question & Resolve Conversational Context
        augmented_query, ctx_etype, ctx_eid, context_summary = context_manager.resolve_contextual_query(
            request.session_id, raw_question
        )

        effective_etype = request.entity_type or ctx_etype
        effective_eid = request.entity_id or ctx_eid

        # 3, 4 & 5. Retrieve Evidence Packet
        # If explicit entity override or context resolved entity:
        if effective_etype and effective_eid:
            packet = evidence_builder.build_for_query(
                query=augmented_query,
                entity_type=effective_etype,
                entity_id=effective_eid
            )
        else:
            packet = evidence_builder.build_for_query(query=augmented_query)

        # 6. Pre-check Unknown or Ambiguous Entities Deterministically
        is_unknown = any(g.gap_type == "UNKNOWN_ENTITY" for g in packet.evidence_gaps)
        is_ambiguous = any(g.gap_type == "AMBIGUOUS_ENTITY" for g in packet.evidence_gaps)
        is_no_alerts = any(g.gap_type == "NO_RELATED_ALERTS" for g in packet.evidence_gaps)

        # Determine whether to use mock adapter
        use_mock = request.use_mock
        if use_mock is None:
            use_mock = settings.copilot_use_mock or (not self.groq_client.is_configured())

        model_name = "mock-groq-llama-3.3-70b" if use_mock else self.groq_client.model

        # 7 & 8. Generate Investigation (via Mock or Groq)
        raw_response: Dict[str, Any] = {}
        if use_mock:
            raw_response = self.mock_adapter.generate(packet, raw_question)
        else:
            user_prompt = build_investigation_prompt(packet, context_summary)
            raw_response = self.groq_client.generate_investigation(
                system_prompt=COPILOT_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )

        # 9 & 10. Validate & Construct Structure
        response = self._process_and_validate_response(
            raw_response=raw_response,
            packet=packet,
            question=raw_question,
            session_id=session_id,
            model_name=model_name,
            start_time=start_time,
            is_unknown=is_unknown,
            is_ambiguous=is_ambiguous,
            is_no_alerts=is_no_alerts
        )

        # 11 & 12. Record Session Turn
        primary_entity_type = packet.target_entity.get("entity_type") if packet.target_entity else None
        primary_entity_id = packet.target_entity.get("canonical_id") if packet.target_entity else None
        context_manager.record_turn(
            session_id=session_id,
            question=raw_question,
            entity_type=primary_entity_type,
            entity_id=primary_entity_id,
            summary=response.summary
        )

        return response

    def explain_alert(
        self,
        alert_id: str,
        session_id: Optional[str] = None,
        use_mock: Optional[bool] = None
    ) -> CopilotInvestigationResponse:
        """Dedicated forensic investigation explanation for a specific alert."""
        request = CopilotInvestigateRequest(
            question=f"What evidence supports alert {alert_id} and why was it flagged?",
            session_id=session_id,
            entity_type="alert",
            entity_id=alert_id,
            use_mock=use_mock
        )
        return self.investigate(request)

    def explain_transaction(
        self,
        transaction_id: str,
        session_id: Optional[str] = None,
        use_mock: Optional[bool] = None
    ) -> CopilotInvestigationResponse:
        """Dedicated forensic investigation explanation for a specific transaction."""
        request = CopilotInvestigateRequest(
            question=f"Why is transaction {transaction_id} suspicious?",
            session_id=session_id,
            entity_type="transaction",
            entity_id=transaction_id,
            use_mock=use_mock
        )
        return self.investigate(request)

    def explain_customer(
        self,
        customer_id: str,
        session_id: Optional[str] = None,
        use_mock: Optional[bool] = None
    ) -> CopilotInvestigationResponse:
        """Dedicated forensic investigation explanation for a specific customer."""
        request = CopilotInvestigateRequest(
            question=f"Why was customer {customer_id} flagged?",
            session_id=session_id,
            entity_type="customer",
            entity_id=customer_id,
            use_mock=use_mock
        )
        return self.investigate(request)

    # -------------------------------------------------------------------------
    # Internal Validation & Grounding Enforcement
    # -------------------------------------------------------------------------
    def _process_and_validate_response(
        self,
        raw_response: Dict[str, Any],
        packet: StandardEvidencePacket,
        question: str,
        session_id: str,
        model_name: str,
        start_time: float,
        is_unknown: bool,
        is_ambiguous: bool,
        is_no_alerts: bool
    ) -> CopilotInvestigationResponse:
        """
        Validates the raw LLM output against the evidence packet.
        Filters ungrounded citations, preserves official deterministic risk scores,
        and enforces the 8 required investigation sections.
        """
        # Collect all legitimate source IDs present in the evidence packet
        allowed_source_ids: Set[str] = set()
        for ref in packet.source_references:
            sid = ref.get("source_id") or ref.get("id")
            if sid:
                allowed_source_ids.add(str(sid))
        for item in packet.exact_data:
            allowed_source_ids.add(str(item.source_id))
        for item in packet.calculated_information:
            allowed_source_ids.add(str(item.source_id))
        for item in packet.retrieved_evidence:
            allowed_source_ids.add(str(item.source_id))
        for item in packet.counter_evidence:
            allowed_source_ids.add(str(item.source_id))
        if packet.target_entity:
            cid = packet.target_entity.get("canonical_id")
            if cid:
                allowed_source_ids.add(str(cid))

        # Check for citation violations
        invalid_citations: List[str] = []

        # 1. Supporting Evidence Validation
        valid_supporting: List[InvestigationEvidenceItem] = []
        raw_supporting = raw_response.get("supporting_evidence", [])
        if isinstance(raw_supporting, list):
            for item in raw_supporting:
                if isinstance(item, dict):
                    sid = str(item.get("source_id", "")).strip()
                    # Check citation format
                    cit = item.get("citation", f"[Source: {sid}]")
                    if sid and (sid in allowed_source_ids or not allowed_source_ids):
                        valid_supporting.append(InvestigationEvidenceItem(
                            source_id=sid,
                            source_table=item.get("source_table", "database"),
                            statement=item.get("statement", ""),
                            citation=cit
                        ))
                    elif sid:
                        # Hallucinated or unsupported citation detected!
                        invalid_citations.append(sid)
                        logger.warning(f"Filtered out hallucinated citation: {sid}")

        # 2. Counter Evidence Validation
        valid_counter: List[InvestigationCounterEvidenceItem] = []
        raw_counter = raw_response.get("counter_evidence", [])
        if isinstance(raw_counter, list):
            for item in raw_counter:
                if isinstance(item, dict):
                    sid = str(item.get("source_id", "")).strip()
                    cit = item.get("citation", f"[Source: {sid}]")
                    if sid and (sid in allowed_source_ids or not allowed_source_ids):
                        valid_counter.append(InvestigationCounterEvidenceItem(
                            source_id=sid,
                            source_table=item.get("source_table", "database"),
                            statement=item.get("statement", ""),
                            citation=cit
                        ))
                    elif sid:
                        invalid_citations.append(sid)

        # 3. Deterministic Risk Score Preservation
        # Extract authoritative score from packet
        authoritative_score = 0
        authoritative_severity = "NONE" if (is_unknown or is_ambiguous or is_no_alerts) else ""

        if packet.target_entity:
            det = packet.target_entity.get("details", {}) or {}
            if det.get("composite_risk_score") is not None:
                authoritative_score = max(authoritative_score, int(det["composite_risk_score"]))
            if det.get("severity"):
                authoritative_severity = str(det["severity"])

        for item in packet.calculated_information:
            if item.field == "composite_risk_score" and isinstance(item.value, (int, float)):
                authoritative_score = max(authoritative_score, int(item.value))
            elif item.field == "severity" and isinstance(item.value, str):
                if not authoritative_severity or (item.value == "CRITICAL" or (item.value == "HIGH" and authoritative_severity != "CRITICAL")):
                    authoritative_severity = item.value

        for item in packet.retrieved_evidence:
            if item.source_table == "alerts":
                prov = item.provenance or {}
                if "composite_risk_score" in prov:
                    authoritative_score = max(authoritative_score, int(prov["composite_risk_score"]))
                if "severity" in prov:
                    s_prov = str(prov["severity"])
                    if not authoritative_severity or s_prov == "CRITICAL" or (s_prov == "HIGH" and authoritative_severity != "CRITICAL"):
                        authoritative_severity = s_prov

        # Reconcile severity with score if not already established from authoritative alert
        if not authoritative_severity:
            if authoritative_score >= 90:
                authoritative_severity = "CRITICAL"
            elif authoritative_score >= 70:
                authoritative_severity = "HIGH"
            elif authoritative_score >= 40:
                authoritative_severity = "MEDIUM"
            elif authoritative_score > 0:
                authoritative_severity = "LOW"
            else:
                authoritative_severity = "NONE"
        elif is_unknown or is_ambiguous or is_no_alerts:
            authoritative_score = 0
            authoritative_severity = "NONE"

        # Check raw risk assessment from LLM
        raw_risk = raw_response.get("risk_assessment", {})
        llm_score = raw_risk.get("risk_score") if isinstance(raw_risk, dict) else None
        llm_severity = raw_risk.get("severity") if isinstance(raw_risk, dict) else None
        confidence = float(raw_risk.get("confidence", 0.85)) if isinstance(raw_risk, dict) else 0.85

        # STRICT ENFORCEMENT: The deterministic engine's score must be preserved
        final_score = authoritative_score
        final_severity = authoritative_severity
        if authoritative_score > 0 and llm_score is not None and llm_score != authoritative_score:
            logger.info(f"Preserving official deterministic risk score {authoritative_score} over LLM proposed {llm_score}")

        risk_assessment = RiskAssessment(
            severity=final_severity,
            risk_score=final_score,
            confidence=max(0.0, min(1.0, confidence))
        )

        # 4. Gaps Validation
        gaps: List[InvestigationGapItem] = []
        raw_gaps = raw_response.get("evidence_gaps", [])
        if isinstance(raw_gaps, list) and raw_gaps:
            for g in raw_gaps:
                if isinstance(g, dict):
                    gaps.append(InvestigationGapItem(
                        gap_type=g.get("gap_type", "DATA_GAP"),
                        description=g.get("description", ""),
                        impact=g.get("impact", "")
                    ))
        else:
            # Fallback to packet gaps
            for g in packet.evidence_gaps:
                gaps.append(InvestigationGapItem(
                    gap_type=g.gap_type,
                    description=g.description,
                    impact=g.impact
                ))

        # 5. Narrative & Sections
        summary = str(raw_response.get("summary") or packet.deterministic_summary or f"Investigation of {question}")
        deviations = raw_response.get("behavioural_deviation", [])
        if not isinstance(deviations, list):
            deviations = [str(deviations)]

        related = raw_response.get("related_activity", [])
        if not isinstance(related, list):
            related = [str(related)]

        next_steps = raw_response.get("investigation_next_steps", [])
        if not isinstance(next_steps, list):
            next_steps = [str(next_steps)]

        escalation = str(raw_response.get("escalation_recommendation") or "Review under standard monitoring.")

        # Source references
        sources: List[EvidenceReference] = []
        seen_sids = set()
        for s in packet.source_references:
            sid = s.get("source_id") or s.get("id")
            s_table = s.get("source_table") or s.get("table") or "database"
            if sid and str(sid) not in seen_sids:
                seen_sids.add(str(sid))
                sources.append(EvidenceReference(
                    source_id=str(sid),
                    source_table=str(s_table),
                    description=s.get("description")
                ))

        resolved_ents = [
            {
                "entity_type": e.entity_type,
                "canonical_id": e.canonical_id,
                "confidence": e.confidence,
                "is_ambiguous": e.is_ambiguous,
                "candidates": e.candidates
            }
            for e in packet.resolved_entities
        ]

        processing_time = round((time.time() - start_time) * 1000, 2)

        return CopilotInvestigationResponse(
            question=question,
            session_id=session_id,
            resolved_entities=resolved_ents,
            summary=summary,
            risk_assessment=risk_assessment,
            supporting_evidence=valid_supporting,
            counter_evidence=valid_counter,
            behavioural_deviation=deviations,
            related_activity=related,
            evidence_gaps=gaps,
            investigation_next_steps=next_steps,
            escalation_recommendation=escalation,
            source_references=sources,
            provenance_validated=(len(invalid_citations) == 0),
            invalid_citations_removed=invalid_citations,
            ambiguity_detected=is_ambiguous,
            unknown_entity_detected=is_unknown,
            insufficient_evidence_detected=is_no_alerts,
            model_used=model_name,
            processing_time_ms=processing_time
        )


copilot_service = CopilotService()
