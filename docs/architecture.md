# System Architecture — Sentient Fraud Investigation Copilot

## 1. High-Level Architecture

```
+-----------------------------------------------------------------------------------+
|                  SENTIENT FRAUD INVESTIGATION COPILOT FRONTEND                    |
|             (React 19 + TypeScript + Vite + Rawbank Design System)                |
|                                                                                   |
|  [Investigation Console]  [Case Templates]  [Entity Drawer]  [Evidence Dossier]   |
|  - Natural Language Chat  - Quick Scenarios - Slide-over     - 3-Tier Breakdown   |
|  - Structured Findings    - Persona Focus   - Link Citations - Counter-Evidence   |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP / JSON REST
                                          v
+-----------------------------------------------------------------------------------+
|                        INVESTIGATION COPILOT FASTAPI BACKEND                      |
|                                                                                   |
|  Routers:                                                                         |
|  - /api/copilot/investigate     - /api/copilot/explain-alert                      |
|  - /api/copilot/explain-transaction - /api/copilot/explain-customer               |
|  - /api/retrieval/query         - /api/evidence                                   |
|  - /api/entities                - /api/search                                     |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         EVIDENCE RETRIEVAL & INDEXING LAYER                       |
|                                                                                   |
|  - Entity Resolution (entity_resolver.py): Exact ID, Name, Keyword Matching       |
|  - Evidence Builder (evidence_builder.py): Assembles 3-Tier Grounded Dossier      |
|  - Field-Level Provenance & Explicit Gap Identification                           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         DETERMINISTIC INTELLIGENCE ENGINE                         |
|                                                                                   |
|  11 Registered Forensic Rules (rules/):                                           |
|  - Mathematical Composite Risk Scoring: [0 - 100]                                 |
|  - Authoritative Rule Severity & Scenario Classification                          |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           AI REASONING & VALIDATION LAYER                         |
|                                                                                   |
|  - Grounded System Prompt (prompts.py): Strictly anchors on retrieved evidence   |
|  - LLM Providers: Groq llama-3.3-70b-versatile (or Offline Mock Adapter)         |
|  - Citation Validator: Filters hallucinated IDs not present in retrieved evidence |
|  - Deterministic Score Override: Protects mathematical score from LLM drift       |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                           SYNTHETIC BANKING DATABASE                              |
|                       (Local SQLite: synthetic_bank.db)                           |
|                                                                                   |
|  - 120 Customers        - 240 Accounts          - 150 Devices                     |
|  - 180 Beneficiaries    - 900 Transactions      - 450 Auth Activities             |
|  - 120 Baselines        - 140 Alerts            - 200 Fraud Signals               |
+-----------------------------------------------------------------------------------+
```

---

## 2. End-to-End Investigation Lifecycle Pipeline

Every question submitted to the Copilot undergoes an explicit 8-stage verification pipeline:

```
  Question
     │
     ▼
[Stage 1: Entity Resolution]
  Matches entity mentions (CUS-, TXN-, ALT-, DEV-, BEN-) to verified canonical database entities.
     │
     ▼
[Stage 2: Deterministic Pre-Checks]
  Executes deterministic rules engine to calculate authoritative risk score, scenario, and metrics.
     │
     ▼
[Stage 3: Evidence Retrieval]
  Builds 3-Tier evidence dossier (Tier 1 Exact Data, Tier 2 Calculated Metrics, Tier 3 Graph Links).
     │
     ▼
[Stage 4: Evidence Validation]
  Verifies provenance against synthetic database; identifies explicit data blindspots / evidence gaps.
     │
     ▼
[Stage 5: Grounded Prompt Assembly]
  Injects verified database evidence and constraints into system prompt. The LLM is NEVER given direct SQL access.
     │
     ▼
[Stage 6: LLM Reasoning]
  Synthesizes executive summary, counter-evidence, behavioral deviation, and next steps via Groq / local mock adapter.
     │
     ▼
[Stage 7: Response Validation & Citation Guardrails]
  Validates every [Source: ID]. Strips any hallucinated citation. Enforces deterministic risk score.
     │
     ▼
[Stage 8: Investigation Result]
  Returns structured CopilotInvestigationResponse schema to frontend workspace.
```
