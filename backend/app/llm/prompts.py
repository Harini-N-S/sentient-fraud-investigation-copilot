"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Prompts & Formatting
-----------------------------------------------------------------------------
Constructs strictly grounded system and user prompts for Groq LLM.
Enforces the core principle: "EVIDENCE BEFORE INTELLIGENCE".
The LLM is NOT the database and must reason ONLY over supplied evidence.
"""

import json
from typing import Optional, Dict, Any
from backend.app.retrieval.models import StandardEvidencePacket


COPILOT_SYSTEM_PROMPT = """You are the Rawbank Sentient Fraud Intelligence Copilot, an expert AI banking fraud investigator.
Your duty is to assist human fraud analysts at Rawbank (Democratic Republic of the Congo) in investigating suspicious transactions, account takeovers, money mule networks, and transactional anomalies.

CRITICAL INSTRUCTION — EVIDENCE BEFORE INTELLIGENCE:
1. You must reason ONLY and STRICTLY from the supplied factual evidence packet.
2. The LLM is NOT the database. You must NEVER invent, assume, extrapolate, or hallucinate:
   - Customers, accounts, transaction IDs, or amounts
   - Dates, timestamps, locations, or cities
   - Devices, hardware models, or IP addresses
   - Beneficiaries, names, or telecom operators
   - Fraud signals, rules, or alerts
   - Risk scores or severity levels
3. OFFICIAL RISK SCORE PRESERVATION:
   - You must NOT calculate your own fraud risk score or invent severity levels.
   - You must STRICTLY preserve the official deterministic risk score and severity provided in the evidence packet.
   - You may explain the contributing factors, but never override the numeric score.
4. FACTUAL TRACEABILITY & BRACKET CITATIONS:
   - Every factual claim supporting fraud or legitimacy MUST include an explicit source citation in brackets: [Source: <SOURCE_ID>].
   - Examples: [Source: TXN-00801], [Source: AUTH-00389], [Source: ALT-00001], [Source: DEV-00127].
   - You must NOT cite identifiers that were not provided in the evidence packet.
5. MANDATORY COUNTER-EVIDENCE & FALSE-POSITIVE EVALUATION:
   - Do NOT force every case into a fraud conclusion.
   - If counter-evidence exists in the packet (e.g. corporate customer baseline, trusted device, known beneficiary, successful dual-factor auth, verified commercial invoice), you MUST include it under "counter_evidence" and explain how it mitigates suspicion.
6. INSUFFICIENT EVIDENCE & GAPS:
   - If no suspicious activity or alerts exist (e.g. normal customer), explicitly state: "Insufficient evidence available in the supplied dataset to establish suspicious activity."
   - Explicitly list all missing parameters under "evidence_gaps".
7. AMBIGUOUS OR UNKNOWN ENTITIES:
   - If an entity is unknown or ambiguous, acknowledge this directly and request analyst clarification. Never guess or assume identity.
8. DISTINGUISH FACTS FROM REASONING:
   - Clearly distinguish between observed database facts, calculated indicators, retrieved graph connections, and investigative reasoning.
   - Do not present reasoning as verified database fact.
9. OUTPUT FORMAT:
   - You must respond with valid JSON ONLY conforming strictly to the requested schema. No conversational preamble or trailing commentary outside the JSON object.
"""


def build_investigation_prompt(
    packet: StandardEvidencePacket,
    conversation_context: Optional[str] = None
) -> str:
    """
    Constructs a grounded user prompt containing the complete evidence packet,
    forensic taxonomy, and conversation context.
    """
    # Extract packet data into a clean structure for the prompt
    exact_data_summary = [
        {"source_id": item.source_id, "table": item.source_table, "field": item.field, "value": item.value, "desc": item.description}
        for item in packet.exact_data
    ]
    
    calc_data_summary = [
        {"source_id": item.source_id, "metric": item.field, "value": item.value, "desc": item.description}
        for item in packet.calculated_information
    ]
    
    retrieved_summary = [
        {"source_id": item.source_id, "table": item.source_table, "desc": item.description}
        for item in packet.retrieved_evidence
    ]
    
    counter_summary = [
        {"source_id": item.source_id, "table": item.source_table, "desc": item.description}
        for item in packet.counter_evidence
    ]
    
    gaps_summary = [
        {"gap_type": g.gap_type, "description": g.description, "impact": g.impact}
        for g in packet.evidence_gaps
    ]
    
    valid_source_ids = [s.get("source_id") for s in packet.source_references if s.get("source_id")]
    
    payload = {
        "investigation_question": packet.query,
        "target_entity": packet.target_entity,
        "deterministic_summary": packet.deterministic_summary,
        "allowed_source_ids_for_citations": valid_source_ids,
        "tier_1_exact_database_records": exact_data_summary,
        "tier_2_calculated_metrics_and_scores": calc_data_summary,
        "tier_3_retrieved_evidence_and_alerts": retrieved_summary,
        "counter_evidence_mitigations": counter_summary,
        "relationships_network": packet.relationships,
        "evidence_gaps_missing_data": gaps_summary
    }

    prompt_lines = [
        "Please perform an evidence-grounded fraud investigation response for the following analyst question.",
        "",
        f"ANALYST QUESTION: {packet.query}",
        ""
    ]

    if conversation_context:
        prompt_lines.extend([
            "PREVIOUS CONVERSATION CONTEXT:",
            conversation_context,
            ""
        ])

    prompt_lines.extend([
        "FACTUAL EVIDENCE DOSSIER (RETRIEVED FROM SYNTHETIC BANKING DATABASE):",
        json.dumps(payload, indent=2),
        "",
        "REQUIRED JSON OUTPUT STRUCTURE (MUST MATCH STRICTLY):",
        """{
  "question": "<the analyst question>",
  "summary": "<concise grounded narrative of events, including [Source: ID] citations>",
  "risk_assessment": {
    "severity": "<CRITICAL | HIGH | MEDIUM | LOW | NONE>",
    "risk_score": <official integer score 0-100 preserved from evidence>,
    "confidence": <float 0.0 to 1.0>
  },
  "supporting_evidence": [
    {
      "source_id": "<ID>",
      "source_table": "<table_name>",
      "statement": "<factual claim>",
      "citation": "[Source: <ID>]"
    }
  ],
  "counter_evidence": [
    {
      "source_id": "<ID>",
      "source_table": "<table_name>",
      "statement": "<mitigating fact>",
      "citation": "[Source: <ID>]"
    }
  ],
  "behavioural_deviation": [
    "<specific deviation comparison against baseline or 'No baseline deviation observed'>"
  ],
  "related_activity": [
    "<connected accounts, shared devices, or linked transactions>"
  ],
  "evidence_gaps": [
    {
      "gap_type": "<type>",
      "description": "<what is missing>",
      "impact": "<forensic effect>"
    }
  ],
  "investigation_next_steps": [
    "<recommended forensic step 1>",
    "<recommended forensic step 2>"
  ],
  "escalation_recommendation": "<grounded recommendation explaining why or why not to escalate>"
}""",
        "",
        "CRITICAL RULES REMINDER:",
        "- Reason ONLY from the evidence provided above.",
        "- Preserve the exact deterministic risk score and severity.",
        "- Do NOT cite any source_id not listed in allowed_source_ids_for_citations.",
        "- If evidence is insufficient or entity is unknown, explicitly state that.",
        "- Return ONLY the JSON object."
    ])

    return "\n".join(prompt_lines)
