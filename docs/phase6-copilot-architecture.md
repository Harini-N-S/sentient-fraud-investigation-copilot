# Rawbank Sentient Fraud Intelligence Platform
## Phase 6: Sentient Fraud Investigation Copilot Architecture

**Status:** Completed (Phase 6 Verified)  
**Governance:** "Evidence Before Intelligence" — Strict Ground Truth — Zero LLM Hallucination  
**Provider:** Groq Cloud (`llama-3.3-70b-versatile`) / Offline Mock Adapter  
**Framework:** FastAPI 0.135.3 / Pydantic v2 / HTTPX / SQLite 3  

---

## 1. Executive Summary & Objective

Phase 6 delivers the **Sentient Fraud Investigation Copilot** for the Rawbank Sentient Fraud Intelligence Platform. Building directly upon the Phase 2 synthetic banking database (2,500 records), Phase 3 deterministic fraud intelligence engine (11 forensic rules), and Phase 5 semantic retrieval & evidence layer, the Copilot serves as an AI-assisted fraud investigation co-pilot for fraud analysts at Rawbank (Democratic Republic of the Congo).

The Copilot is explicitly **NOT a generic chatbot**. It cannot browse the internet, cannot directly query SQLite, cannot calculate its own fraud scores, and cannot invent banking facts. Instead, it reasons strictly over deterministic forensic evidence packets retrieved prior to LLM invocation.

### Platform Architecture Pipeline
```
[1] Structured Data (SQLite Synthetic Banking Database — 2,500 records)
         │
         ▼
[2] Deterministic Processing (Phase 3 Rules Engine — 11 Forensic Rules)
         │
         ▼
[3] Entity Resolution (Phase 5 Deterministic Entity Resolver)
         │
         ▼
[4] Semantic Retrieval & Evidence Layer (Phase 5 StandardEvidencePacket)
         │
         ▼
[5] LLM Intelligence (Phase 6 Sentient Fraud Investigation Copilot)  <-- THIS PHASE
         │
         ▼
[6] Backend API (FastAPI Data Access & Copilot Endpoints)
         │
         ▼
[7] Application Experience (Future Phase 7 Workstation)
```

---

## 2. Core Architectural Principle: "Evidence Before Intelligence"

The foundational design constraint of Phase 6 is that **Retrieval Precedes Reasoning**.

```
ANALYST QUESTION
       │
       ▼
CONTEXT RESOLUTION (Lightweight Session Anaphora)
       │
       ▼
ENTITY RESOLUTION (Exact IDs, Normalized IDs, Names)
       │
       ▼
RETRIEVAL & GRAPH EXPANSION (EvidenceBuilder)
       │
       ▼
EVIDENCE PACKET (StandardEvidencePacket: 4-Tier Forensic Taxonomy)
       │
       ▼
DETERMINISTIC VALIDATION (Check Unknown / Ambiguous / Insufficient Evidence)
       │
       ▼
PROMPT CONSTRUCTION (Grounded System & User Dossier)
       │
       ▼
GROQ LLM / MOCK ADAPTER (Strict JSON Mode)
       │
       ▼
CITATION & PROVENANCE VALIDATION (Filter Ungrounded Citations, Preserve Risk Score)
       │
       ▼
GROUNDED INVESTIGATION RESPONSE (Structured 8-Section JSON)
```

### Why the LLM is NOT the Database
1. **Zero Database Access:** The LLM client never connects to SQLite or executes SQL queries.
2. **Zero Invented Records:** Every customer, transaction, amount, date, device, and beneficiary must exist in the retrieved evidence packet.
3. **Official Risk Score Preservation:** The official fraud risk score and severity level are deterministically produced by Phase 3 rules. The LLM explains contributing factors but is strictly forbidden from recalculating or overriding official scores.
4. **Traceable Citations:** All factual assertions must carry bracket citations (`[Source: TXN-00801]`, `[Source: ALT-00001]`, `[Source: DEV-00127]`).

---

## 3. Directory & Module Structure

The Copilot engine is modularized under `backend/app/llm/` and routed via `backend/app/routers/copilot.py`:

```
backend/app/llm/
├── __init__.py               # Public package exports
├── schemas.py                # Pydantic request/response contracts enforcing 8 sections
├── prompts.py                # Strict grounded system prompt & user prompt builder
├── client.py                 # Server-side Groq API client with timeouts and error mapping
├── mock_adapter.py           # High-fidelity deterministic mock adapter for testing/offline
├── context_manager.py        # Lightweight multi-turn conversation session manager
└── service.py                # 12-Step CopilotService orchestrating retrieval and validation

backend/app/routers/
└── copilot.py                # REST API endpoints (/api/copilot/*)
```

---

## 4. Groq Integration & Model Configuration

### Server-Side Only
All communication with Groq is executed server-side via `GroqClient` using `httpx`. The `GROQ_API_KEY` is **never** sent to the client, never embedded in HTML/JS, and never committed to version control.

### Configuration via Environment Variables
```env
# Phase 6: Copilot / Groq LLM Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_TIMEOUT_SECONDS=30.0
COPILOT_USE_MOCK=false
```

- **Configurable Model:** Model identifier is read dynamically from `settings.groq_model` (e.g. `llama-3.3-70b-versatile` or `llama-3.1-8b-instant`).
- **Fail-Fast Error Handling:** If `GROQ_API_KEY` is missing when a live call is requested, `GroqConfigurationError` is raised immediately. The backend **never silently falls back** to a fake LLM when live LLM is requested.
- **Offline / CI Mock Adapter:** Automated tests and offline environments use `MockLLMAdapter`, allowing complete test suite execution without requiring a live Groq API key or internet access.

---

## 5. The 12-Step Copilot Pipeline

Every investigation executed by `CopilotService.investigate()` follows 12 strict steps:

1. **Receive Question:** Accepts analyst query and optional `session_id`.
2. **Resolve Conversational Context:** Maps contextual references ("What happened before that?", "Who else uses this device?") to the previous turn's target entities via `ConversationContextManager`.
3. **Resolve Entities:** Invokes `EntityResolver` to identify canonical customer, account, transaction, device, beneficiary, or alert IDs.
4. **Deterministic Pre-Checks:**
   - **Unknown Identifier:** If target ID does not exist (e.g. `CUS-99999`), generates a zero-hallucination unknown entity response immediately.
   - **Ambiguous Match:** If name matches multiple entities (e.g. `Jean Mutombo` -> `CUS-00035` and `CUS-00041`), returns candidate list and requests clarification without arbitrary selection.
5. **Retrieve Evidence:** Calls Phase 5 `EvidenceBuilder` to assemble Tier 1 exact records, Tier 2 calculations, Tier 3 alerts/signals, counter-evidence, and 2-hop network graph linkages.
6. **Validate Evidence Completeness:** Checks for clean entities (e.g. `CUS-00003` normal customer with 0 alerts) and documents evidence gaps.
7. **Construct Grounded Prompt:** Formats the complete evidence dossier into JSON and applies strict anti-hallucination rules.
8. **Dispatch to LLM / Mock:** Sends prompt to Groq API (or `MockLLMAdapter` in test/mock mode) requesting strict JSON output.
9. **Receive Response:** Parses structured JSON payload.
10. **Validate Response Structure:** Validates against `CopilotInvestigationResponse` schema.
11. **Citation & Score Validation:**
    - Checks every cited `[Source: ID]` against the allowed source IDs in the evidence packet.
    - Hallucinated or unsupported IDs are filtered out and recorded in `invalid_citations_removed`.
    - Preserves authoritative Phase 3 deterministic risk score and severity.
12. **Record Context & Return:** Updates session history with turn summary and returns the validated investigation response.

---

## 6. The 8 Required Investigation Sections

Every complete investigation response structure (`CopilotInvestigationResponse`) contains:

| Section | Field | Purpose |
|---|---|---|
| **1. Summary** | `summary` | Objective narrative of what occurred based strictly on retrieved facts with bracket citations. |
| **Risk Assessment** | `risk_assessment` | Deterministic severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE`) and score (`0-100`) preserved from Phase 3. |
| **2. Supporting Evidence** | `supporting_evidence` | Factual claims supporting fraud hypothesis with `source_id`, `source_table`, and `citation`. |
| **3. Counter-Evidence** | `counter_evidence` | Mitigating facts indicating legitimate activity or reducing suspicion (mandatory for balanced investigations). |
| **4. Behavioural Deviation** | `behavioural_deviation` | Quantitative comparison against customer 30-day baseline (velocity spike, amount vs median, new city). |
| **5. Related Activity** | `related_activity` | Network connections (shared hardware signatures, shared mule beneficiaries, linked accounts). |
| **6. Evidence Gaps** | `evidence_gaps` | Explicitly documented missing information (e.g. lack of prior baseline, unverified device, ambiguous entity). |
| **7. Next Steps** | `investigation_next_steps` | Actionable recommendations for the analyst (e.g. inspect auth logs, contact customer via out-of-band voice). |
| **8. Escalation** | `escalation_recommendation` | Objective recommendation on whether evidence supports escalation to Level 2 fraud team. |

---

## 7. Evidence Citations & Hallucination Defense

### Bracket Citation Standard
All claims in the narrative and structured evidence items are cited using:
```
[Source: <SOURCE_ID>]
```
Examples:
- `[Source: TXN-00801]` — Transaction ledger record
- `[Source: ALT-00001]` — Official fraud alert
- `[Source: AUTH-00403]` — Preceding authentication event
- `[Source: DEV-00127]` — Hardware device fingerprint
- `[Source: BEN-00088]` — Beneficiary mobile money account

### Post-Generation Verification
The Copilot service compiles an `allowed_source_ids` set directly from the retrieved `StandardEvidencePacket`. Any citation referencing an identifier outside this set is rejected, removed from `supporting_evidence`, and flagged in `invalid_citations_removed` with `provenance_validated = False`.

---

## 8. Edge Cases & Special Scenarios

### 1. Counter-Evidence & False Positives
For legitimate anomalies (e.g. corporate high-value payment `ALT-00027` / `CUS-00010` / `TXN-00751`), the Copilot actively highlights mitigating evidence:
- Corporate customer classification
- Known recurring beneficiary
- Trusted enrolled MacBook hardware
- Verified dual-factor authorization
The Copilot explicitly recommends **closing as a legitimate anomaly / false positive** rather than forcing a fraud accusation.

### 2. Ambiguous Entities
When an analyst asks: *"Why was Jean Mutombo flagged?"*, the entity resolver identifies two matching customers (`CUS-00035` and `CUS-00041`).
- The Copilot **refuses to guess arbitrarily**.
- Flags `ambiguity_detected = True`.
- Returns candidate list with customer IDs and account titles.
- Recommends clarifying target customer ID before proceeding.

### 3. Unknown Entities
When an analyst queries a non-existent identifier (*"Why was customer CUS-99999 flagged?"*):
- Flags `unknown_entity_detected = True`.
- Risk score: `0`, Severity: `NONE`.
- Confirms zero records exist in the synthetic banking database.
- Does not call the LLM with fabricated data.

### 4. Clean Normal Customers (Insufficient Evidence)
When an analyst queries a clean customer with zero alerts (*"Why was customer CUS-00003 flagged?"*):
- Flags `insufficient_evidence_detected = True`.
- Explicitly states: *"There is insufficient evidence in the available synthetic dataset to establish suspicious activity."*
- Documents `NO_RELATED_ALERTS` evidence gap.

### 5. Multi-Turn Conversational Memory
The `ConversationContextManager` tracks session turns in memory:
- Turn 1: *"Why was customer CUS-00014 flagged?"* (Copilot details ATO alert `ALT-00001` and transaction `TXN-00801`).
- Turn 2: *"What happened before that?"* (Copilot resolves "that" to `TXN-00801` and retrieves preceding authentication events and password resets).

---

## 9. Security & Data Governance

1. **Zero Real Banking Data:** All investigations operate strictly over the Phase 2 synthetic banking database (2,500 records).
2. **Zero PII Exposure:** Customer names, phone numbers, and addresses are synthetically generated.
3. **Server-Side API Key Protection:** `GROQ_API_KEY` is loaded via backend environment variables and is never exposed in API responses or frontend bundles.
4. **Git Protection:** `.env` is registered in `.gitignore`; `.env.example` contains placeholders only.
5. **No Stack Trace Leakage:** Unhandled exceptions and API errors return clean, standardized error objects without disclosing server file paths or internal variables.
