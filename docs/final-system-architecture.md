# Final System Architecture Specification
**Rawbank Sentient Fraud Intelligence Platform**
**End-to-End System Pipeline & Architectural Layers**

---

## 1. End-to-End Architectural Pipeline

```
                SYNTHETIC BANKING DATA
                         ↓
                SQLITE DATA LAYER
                         ↓
             DETERMINISTIC FRAUD RULES
                         ↓
              ENTITY RESOLUTION
                         ↓
                RETRIEVAL LAYER
                         ↓
                EVIDENCE BUILDER
                         ↓
                   GROQ / LLM
                         ↓
              COPILOT INVESTIGATION
                         ↓
                FASTAPI BACKEND
                         ↓
                REACT FRONTEND
                         ↓
          SENTIENT COMMAND CENTRE
                     +
          INVESTIGATION COPILOT
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Synthetic Banking Data Layer (Source of Truth)
- **Role:** Immutable single source of truth for all operational records, ledger balances, and audit trails.
- **Technology:** Embedded SQLite database (`database/synthetic_bank.db`).
- **Characteristics:**
  - Strict foreign key constraints and transactional integrity.
  - Exactly 120 customers, 240 dual-currency accounts (CDF/USD), 900 transactions ($2.31M USD total volume), 150 hardware devices, 180 beneficiaries, 450 authentication logs, and 120 behavioral baselines.
  - Tailored to DRC retail and commercial banking: mobile money rails (IllicoCash, M-Pesa, Orange, Airtel), regional mining corridors (Katanga/Kolwezi), and local telecom channels.
  - 100% synthetic; zero real customer PII.

---

### Layer 2: Deterministic Fraud Intelligence Layer
- **Role:** Authoritative, explainable risk assessment and incident generation without LLM dependencies.
- **Technology:** Python deterministic rule modules (`rules/`) & `CorrelationEngine`.
- **Characteristics:**
  - **9 Granular Fraud Engines:**
    1. `R-VEL-01`: Rapid consecutive transaction velocity bursts.
    2. `R-DEV-02` / `R-DEV-SHR-01`: Unenrolled devices and multi-customer hardware syndicate sharing.
    3. `R-GEO-03`: Impossible physical travel velocity across DRC geographies.
    4. `R-MULE-04`: Multi-sender fan-in aggregation to centralized mobile wallets.
    5. `R-ATO-05`: Credential administrative resets followed immediately by maximum account liquidation.
    6. `R-SMURF-06`: Smurfing patterns designed to evade regulatory reporting thresholds.
    7. `R-VAL-07`: Extreme value spikes relative to 30-day customer median baselines.
    8. `R-AUTH-08`: Multiple failed authentication events preceding transfers.
    9. `R-BEH-09`: Statistical deviations from established customer operating hours.
  - **Explainable Scoring:** Transparent composite scoring (0–100) and deterministic severity mapping (`CRITICAL >= 90`, `HIGH >= 70`, `MEDIUM >= 40`, `LOW < 40`).
  - **Mitigation Discounting:** Evaluates counter-evidence (e.g. trusted corporate hardware, recurring payroll baseline) to deduct false-positive points before final score crystallization.

---

### Layer 3: Deterministic Entity Resolution Layer
- **Role:** Normalizes ambiguous search queries, customer names, device IDs, and account references into canonical database primary keys.
- **Technology:** Deterministic resolver engine (`backend/app/retrieval/entity_resolver.py`).
- **Characteristics:**
  - Multi-strategy entity matching: exact ID, normalized ID, case-insensitive name matching, and alias expansion.
  - **Ambiguity Detection:** Identifies queries matching multiple distinct records (e.g. *"Jean Mutombo"* matching `CUS-00035` and `CUS-00041`) and surfaces candidate profiles rather than making arbitrary guesses.
  - **Unknown Entity Interception:** Detects non-existent identifiers (e.g. `CUS-99999`) and immediately halts downstream speculative fabrication.

---

### Layer 4: Semantic & Structured Retrieval Layer
- **Role:** Indexes structured banking records and executes hybrid multi-hop topological queries.
- **Technology:** In-memory inverted indexer & relational traversal (`backend/app/retrieval/indexer.py`, `retrieval_service.py`).
- **Characteristics:**
  - Indexes 2,618 documents (1:1 with core records + 107 topological relationships + 11 rule intelligence items).
  - Hybrid scoring formula: combines BM25 lexical keyword relevance, structured metadata filtering (severity, scenario, date), and graph adjacency weighting.
  - Fast sub-20ms retrieval execution with zero external vector database infrastructure requirements.

---

### Layer 5: Standardized Forensic Evidence Packet Builder
- **Role:** Assembles tamper-evident, audit-ready evidence dossiers strictly anchored in verified database rows.
- **Technology:** `ForensicEvidenceBuilder` (`backend/app/retrieval/evidence_builder.py`).
- **Characteristics:**
  - **Strict 4-Tier Evidence Hierarchy:**
    1. **Tier 1 (Exact Data):** Unaltered database ledger fields with table/column provenance.
    2. **Tier 2 (Calculated Information):** Deterministic mathematical indicators (e.g. velocity ratios, distinct sender counts, composite risk scores).
    3. **Tier 3 (Retrieved Evidence):** Corroborating historical alerts and granular fraud signals.
    4. **Tier 4 (Counter-Evidence):** Explicit mitigating factors supporting legitimate operational activity.
  - **Explicit Evidence Gaps:** Documents absent records (e.g. `UNKNOWN_ENTITY`, `AMBIGUOUS_ENTITY`, `UNGROUNDED_PREMISE`) to prevent speculation.
  - **Query Premise Auditing:** Detects assertions of non-existent foreign locations (e.g. *"Paris"*), unsupported dates, or fabricated amounts and flags them as ungrounded.

---

### Layer 6: Groq LLM & AI Reasoning Layer
- **Role:** Conversational reasoning, forensic narrative synthesis, hypothesis correlation, and investigative recommendations.
- **Technology:** Groq Cloud Llama 3.3 70B Versatile (`backend/app/llm/client.py`) with zero-config deterministic offline mock adapter (`mock_adapter.py`).
- **Characteristics:**
  - **Evidence-Before-Intelligence Protocol:** The LLM prompt is injected *only* with data pre-assembled in the Evidence Packet. The LLM has zero direct SQL write access.
  - **Score Preservation Guard:** Post-generation validation inspects the LLM response and strictly enforces the Phase 3 deterministic score, preventing LLM score drift or hallucinations.
  - **Citation Enforcement:** Every factual assertion must be backed by a verified bracketed citation (e.g. `[Source: TXN-00801]`). Hallucinated citation IDs are automatically stripped during validation.
  - **8 Required Investigation Sections:**
    1. Narrative Summary
    2. Authoritative Risk Assessment
    3. Supporting Evidence
    4. Counter-Evidence / Mitigating Factors
    5. Behavioral Baseline Deviation
    6. Related Syndicate Activity
    7. Evidence Gaps & Missing Information
    8. Actionable Next Steps & Escalation Recommendation

---

### Layer 7: FastAPI Backend Service Layer
- **Role:** RESTful API orchestration, session management, request validation, and database connection pooling.
- **Technology:** FastAPI, Uvicorn ASGI server, Pydantic v2 schemas (`backend/app/`).
- **Characteristics:**
  - High-throughput asynchronous endpoints with sub-25ms average latency.
  - Sanitized error handling: zero stack trace or internal path leakage on 404, 400, or 422 errors.
  - CORS middleware configured for enterprise local environments.

---

### Layer 8: React Frontend Application Layer
- **Role:** High-performance, responsive single-page enterprise web application.
- **Technology:** React 19, TypeScript, Vite, Vanilla CSS design tokens (`frontend/`).
- **Characteristics:**
  - **Sentient Command Centre:** Operational triage dashboard with live KPIs, severity distributions, scenario breakdowns, and interactive incident queues.
  - **Sentient Fraud Investigation Copilot:** Conversational chat interface with streaming message rendering, quick prompt suggestions, and interactive citation navigation.
  - **Interactive Entity Graph:** SVG topological network visualizer showing 1-hop and 2-hop links across customers, accounts, devices, and beneficiaries.
  - **Accessibility & UX:** Full keyboard navigation (`Alt+K` search omnibox, `Esc` drawer closing), dual Kinshasa/Lubumbashi clocks, and zero placeholder/mock numbers.

---

## 3. Explicit System Boundaries & Guardrails

| Subsystem | Authority & Responsibility | What It CANNOT Do |
|---|---|---|
| **SQLite Database** | Definitive ledger ground truth and historical activity records. | Cannot compute dynamic LLM narratives. |
| **Deterministic Rules** | Authoritative risk scoring (0–100), severity assignment, scenario classification. | Cannot hallucinate or invent new entities. |
| **Retrieval Layer** | Exact data assembly, graph link discovery, evidence gap identification. | Cannot guess or interpolate missing data. |
| **Groq / LLM Copilot** | Evidence explanation, hypothesis testing, analyst recommendation. | **CANNOT override deterministic risk scores.** Cannot invent ungrounded transactions or entities. |
| **React Frontend** | Human-in-the-loop visualization, triage, and investigative interaction. | Contains zero mock data; displays only verified API telemetry. |
