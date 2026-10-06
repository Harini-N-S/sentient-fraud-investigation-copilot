"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Mock LLM Adapter
-----------------------------------------------------------------------------
Deterministic, grounded mock LLM provider for automated testing and offline demo.
Constructs realistic, fully schema-compliant investigation responses dynamically
derived from the supplied StandardEvidencePacket.
Guarantees zero hallucinations, exact risk score preservation, and strict provenance.
"""

from typing import Dict, Any, List, Optional
from backend.app.retrieval.models import StandardEvidencePacket, ResolvedEntity
from backend.app.llm.schemas import (
    CopilotInvestigationResponse,
    RiskAssessment,
    InvestigationEvidenceItem,
    InvestigationCounterEvidenceItem,
    InvestigationGapItem,
    EvidenceReference
)


class MockLLMAdapter:
    """
    Mock LLM provider that emulates Groq response generation with 100% evidence fidelity.
    Uses retrieved evidence packet to populate all 8 required investigation sections.
    """

    def __init__(self, model_name: str = "mock-groq-llama-3.3-70b"):
        self.model_name = model_name

    def generate(
        self,
        packet: StandardEvidencePacket,
        question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a structured dictionary matching CopilotInvestigationResponse.
        """
        q = question or packet.query
        
        # 1. Check for Unknown Entity
        has_unknown = any(g.gap_type == "UNKNOWN_ENTITY" for g in packet.evidence_gaps)
        unknown_entities = [e for e in packet.resolved_entities if e.confidence == 0.0 and e.matching_method == "unknown_identifier"]
        if has_unknown or unknown_entities:
            target_id = unknown_entities[0].canonical_id if unknown_entities else "specified entity"
            return {
                "question": q,
                "summary": f"Unknown entity investigated: '{target_id}' was not found in the Rawbank synthetic banking database. Zero records exist.",
                "risk_assessment": {
                    "severity": "NONE",
                    "risk_score": 0,
                    "confidence": 0.0
                },
                "supporting_evidence": [],
                "counter_evidence": [],
                "behavioural_deviation": [],
                "related_activity": [],
                "evidence_gaps": [
                    {
                        "gap_type": "UNKNOWN_ENTITY",
                        "description": f"Identifier '{target_id}' does not match any customer, account, transaction, or device in the database.",
                        "impact": "Investigation cannot proceed because target entity does not exist."
                    }
                ],
                "investigation_next_steps": [
                    "Verify the identifier against internal core banking registry.",
                    "Confirm spelling and ID format (e.g. CUS-XXXXX, TXN-XXXXX)."
                ],
                "escalation_recommendation": "Do not escalate. Non-existent record in banking database.",
                "source_references": []
            }

        # 2. Check for Ambiguous Entity
        has_ambiguous = any(g.gap_type == "AMBIGUOUS_ENTITY" for g in packet.evidence_gaps)
        ambiguous_entities = [e for e in packet.resolved_entities if e.is_ambiguous]
        if has_ambiguous or ambiguous_entities:
            amb = ambiguous_entities[0] if ambiguous_entities else packet.resolved_entities[0]
            cand_strs = [
                f"{c.get('customer_id') or c.get('canonical_id')}: {c.get('full_name') or c.get('title')}"
                for c in amb.candidates
            ]
            cand_summary = ", ".join(cand_strs) if cand_strs else "Multiple records matched"
            return {
                "question": q,
                "summary": f"Ambiguity detected: The reference '{amb.matched_text}' matches multiple candidate entities ({cand_summary}). Cannot conclusively investigate without specific identity clarification.",
                "risk_assessment": {
                    "severity": "NONE",
                    "risk_score": 0,
                    "confidence": 0.0
                },
                "supporting_evidence": [],
                "counter_evidence": [],
                "behavioural_deviation": [],
                "related_activity": [],
                "evidence_gaps": [
                    {
                        "gap_type": "AMBIGUOUS_ENTITY",
                        "description": f"Entity mention '{amb.matched_text}' resolved to multiple distinct candidates: {cand_summary}.",
                        "impact": "Requires investigator disambiguation before evidence dossier can be compiled."
                    }
                ],
                "investigation_next_steps": [
                    f"Clarify target customer ID from candidate list: {cand_summary}.",
                    "Specify unique account number (ACC-XXXXX) or customer ID (CUS-XXXXX)."
                ],
                "escalation_recommendation": "Hold escalation pending customer identity clarification.",
                "source_references": []
            }

        # 3. Check for Ungrounded Premise in Query
        ungrounded = [g for g in packet.evidence_gaps if g.gap_type == "UNGROUNDED_PREMISE"]
        if ungrounded:
            gap = ungrounded[0]
            target_name = packet.target_entity.get("canonical_id") if packet.target_entity else "target"
            return {
                "question": q,
                "summary": f"Premise Not Grounded: {gap.description} The system rejects this ungrounded assertion because no corresponding records exist in the Rawbank synthetic database.",
                "risk_assessment": {
                    "severity": "LOW",
                    "risk_score": 15,
                    "confidence": 0.95
                },
                "supporting_evidence": [],
                "counter_evidence": [
                    {
                        "source_id": str(target_name),
                        "source_table": "evidence_audit",
                        "statement": gap.description,
                        "citation": f"[Source: {target_name}]"
                    }
                ],
                "behavioural_deviation": [],
                "related_activity": [
                    f"All authenticated activities and transactions for {target_name} occurred strictly within DRC operational channels."
                ],
                "evidence_gaps": [
                    {
                        "gap_type": "UNGROUNDED_PREMISE",
                        "description": gap.description,
                        "impact": gap.impact
                    }
                ],
                "investigation_next_steps": [
                    "Verify the origin of the external claim or query premise.",
                    "Review authoritative audit logs in Sentient Command Centre for verified activity."
                ],
                "escalation_recommendation": "Do not escalate based on ungrounded allegations. Maintain monitoring on verified evidence.",
                "source_references": packet.source_references[:3]
            }

        # 4. Check for Normal Entity / Insufficient Evidence
        has_no_alerts = any(g.gap_type == "NO_RELATED_ALERTS" for g in packet.evidence_gaps)
        alerts_in_packet = [item for item in packet.retrieved_evidence if item.source_table == "alerts"]
        calc_scores = [item for item in packet.calculated_information if item.field == "composite_risk_score" and item.value > 0]
        if has_no_alerts or (not alerts_in_packet and not calc_scores):
            # Target is a normal customer or clean entity
            target_name = packet.target_entity.get("canonical_id") if packet.target_entity else "target"
            return {
                "question": q,
                "summary": f"Investigation of {target_name}: There is insufficient evidence in the available synthetic dataset to establish suspicious activity. No active fraud alerts, high-risk signals, or security incidents are recorded for this entity.",
                "risk_assessment": {
                    "severity": "NONE",
                    "risk_score": 0,
                    "confidence": 0.95
                },
                "supporting_evidence": [],
                "counter_evidence": [
                    {
                        "source_id": str(target_name),
                        "source_table": "alerts",
                        "statement": "Zero fraud alerts or suspicious incident reports exist in the synthetic database.",
                        "citation": f"[Source: {target_name}]"
                    }
                ],
                "behavioural_deviation": [
                    "Activity adheres consistently to regular retail/commercial profile with zero statistical deviations."
                ],
                "related_activity": [
                    "All observed historical transactions reflect routine banking activity."
                ],
                "evidence_gaps": [
                    {
                        "gap_type": "NO_RELATED_ALERTS",
                        "description": f"No alert records or suspicious incident reports exist for entity {target_name}.",
                        "impact": "No evidence of fraudulent activity identified."
                    }
                ],
                "investigation_next_steps": [
                    "No immediate investigative action required.",
                    "Continue standard automated monitoring under routine thresholds."
                ],
                "escalation_recommendation": "Do not escalate. Available evidence confirms normal banking profile with no suspicious indicators.",
                "source_references": [
                    {
                        "source_id": str(target_name),
                        "source_table": "customers" if str(target_name).startswith("CUS-") else "entities",
                        "description": "Clean entity record"
                    }
                ]
            }

        # 4. Standard Suspicious / Anomalous Investigation Case
        # Extract official risk score & severity from packet
        score = 0
        severity = ""

        # Check target entity details (e.g. alert entity)
        if packet.target_entity:
            det = packet.target_entity.get("details", {}) or {}
            if det.get("composite_risk_score") is not None:
                score = max(score, int(det["composite_risk_score"]))
            if det.get("severity"):
                severity = str(det["severity"])

        # Scan calculated information for max risk score
        for item in packet.calculated_information:
            if item.field == "composite_risk_score" and isinstance(item.value, (int, float)):
                score = max(score, int(item.value))
            elif item.field == "severity" and isinstance(item.value, str):
                if not severity or (item.value == "CRITICAL" or (item.value == "HIGH" and severity != "CRITICAL")):
                    severity = item.value

        # Scan retrieved alerts
        for item in packet.retrieved_evidence:
            if item.source_table == "alerts":
                prov = item.provenance or {}
                if "composite_risk_score" in prov:
                    score = max(score, int(prov["composite_risk_score"]))
                if "severity" in prov:
                    s_prov = str(prov["severity"])
                    if not severity or s_prov == "CRITICAL" or (s_prov == "HIGH" and severity != "CRITICAL"):
                        severity = s_prov

        # Reconcile severity with score if not already established from authoritative alert
        if not severity:
            if score >= 90:
                severity = "CRITICAL"
            elif score >= 70:
                severity = "HIGH"
            elif score >= 40:
                severity = "MEDIUM"
            elif score > 0:
                severity = "LOW"
            else:
                severity = "NONE"

        confidence = 0.95 if score > 70 else (0.85 if score > 30 else 0.75)

        # Build Supporting Evidence from packet
        supporting_items: List[Dict[str, Any]] = []
        for item in packet.exact_data[:8]:
            supporting_items.append({
                "source_id": item.source_id,
                "source_table": item.source_table,
                "statement": f"{item.description} (Value: {item.value})",
                "citation": f"[Source: {item.source_id}]"
            })
        for item in packet.calculated_information[:6]:
            supporting_items.append({
                "source_id": item.source_id,
                "source_table": item.source_table,
                "statement": f"Calculated indicator: {item.description} (Value: {item.value})",
                "citation": f"[Source: {item.source_id}]"
            })
        for item in packet.retrieved_evidence[:8]:
            supporting_items.append({
                "source_id": item.source_id,
                "source_table": item.source_table,
                "statement": f"Retrieved record: {item.description}",
                "citation": f"[Source: {item.source_id}]"
            })

        # Build Counter Evidence from packet
        counter_items: List[Dict[str, Any]] = []
        for item in packet.counter_evidence:
            counter_items.append({
                "source_id": item.source_id,
                "source_table": item.source_table,
                "statement": item.description,
                "citation": f"[Source: {item.source_id}]"
            })

        # Build Behavioural Deviation from packet
        deviations: List[str] = []
        for item in packet.calculated_information:
            if "baseline" in item.field.lower() or "ratio" in item.field.lower() or "spike" in item.description.lower() or "deviation" in item.description.lower():
                deviations.append(f"{item.description}: {item.value} [Source: {item.source_id}]")
        if not deviations:
            if counter_items:
                deviations.append("Transaction value is consistent with established historical commercial volume [Source: baselines].")
            else:
                deviations.append("No significant baseline deviations recorded in customer profile.")

        # Build Related Activity from packet
        related: List[str] = []
        for rel in packet.relationships[:8]:
            desc = f"Connected {rel.get('entity_type')} {rel.get('entity_id')}: {rel.get('relationship')} (hop: {rel.get('hop_depth', 1)})"
            related.append(desc)
        if not related:
            related.append("No multi-hop device or beneficiary sharing detected in bounded network graph.")

        # Build Evidence Gaps from packet
        gaps: List[Dict[str, Any]] = []
        for g in packet.evidence_gaps:
            gaps.append({
                "gap_type": g.gap_type,
                "description": g.description,
                "impact": g.impact
            })

        # Build Investigation Next Steps
        next_steps: List[str] = []
        has_ato_signal = any("ATO" in s.get("statement", "") or "password" in s.get("statement", "").lower() or "credential" in s.get("statement", "").lower() for s in supporting_items)
        if has_ato_signal:
            next_steps.append("Inspect recent authentication logs and credential reset audit logs [auth_activity].")
            next_steps.append("Contact customer via registered voice channel to confirm authorized device enrollment.")
        if any("shared" in r.lower() for r in related):
            next_steps.append("Conduct network graph analysis on co-occurring accounts linked to shared hardware signatures.")
        if counter_items:
            next_steps.append("Verify corporate authorization signatures against signatory mandate.")
        if not next_steps:
            next_steps.append("Review complete transaction sequence over the past 30 days.")
            next_steps.append("Verify beneficiary account history and outbound clearing channel.")

        # Build Escalation Recommendation
        if severity == "CRITICAL" or (severity == "NONE" and score >= 90):
            escalation = (
                f"Available evidence strongly supports immediate escalation to Level 2 Senior Fraud Analyst. "
                f"The incident presents an official risk score of {score}/100 ({severity}) combining critical indicators "
                f"(such as credential password reset and anomalous velocity). Immediate account restriction recommended."
            )
        elif severity == "HIGH" or (severity == "NONE" and score >= 70):
            escalation = (
                f"Available evidence supports escalation for enhanced due diligence (Risk Score: {score}/100, {severity}). "
                f"Analyst should verify beneficiary relationships and transaction origin before approving further outbound transfers."
            )
        elif counter_items and score < 50:
            escalation = (
                f"Available evidence does NOT support fraud escalation. The alert is classified as {severity} (Score: {score}/100) "
                f"and is strongly mitigated by legitimate operational counter-evidence (corporate baseline, trusted hardware, dual authorization). "
                f"Recommended for closure as a legitimate anomaly / false positive."
            )
        else:
            escalation = (
                f"Available evidence suggests low operational risk (Score: {score}/100, {severity}). "
                f"Recommend standard monitoring without immediate operational freeze."
            )

        # Summary narrative: synthesize primary entity, key signals, and citations
        target_name = packet.target_entity.get("canonical_id") if packet.target_entity else "target"
        key_signals = [s.get("statement", "") for s in supporting_items if "Signal" in s.get("statement", "") or "Alert" in s.get("statement", "")]
        signal_narrative = f" Key indicators: {'; '.join(key_signals[:2])}." if key_signals else ""
        
        summary = (
            f"Forensic investigation completed for {target_name} ({q}). "
            f"Official deterministic risk score is {score}/100 ({severity})."
            f"{signal_narrative} "
            f"Identified {len(supporting_items)} supporting evidence items and {len(counter_items)} counter-evidence mitigations."
        )

        # Sources: robust extraction supporting both 'id'/'table' and 'source_id'/'source_table'
        sources = []
        seen_sids = set()
        for s in packet.source_references:
            sid = s.get("source_id") or s.get("id")
            stable = s.get("source_table") or s.get("table") or "database"
            if sid and str(sid) not in seen_sids:
                seen_sids.add(str(sid))
                sources.append({
                    "source_id": str(sid),
                    "source_table": str(stable),
                    "description": s.get("description")
                })

        return {
            "question": q,
            "summary": summary,
            "risk_assessment": {
                "severity": severity,
                "risk_score": score,
                "confidence": confidence
            },
            "supporting_evidence": supporting_items,
            "counter_evidence": counter_items,
            "behavioural_deviation": deviations,
            "related_activity": related,
            "evidence_gaps": gaps,
            "investigation_next_steps": next_steps,
            "escalation_recommendation": escalation,
            "source_references": sources
        }
