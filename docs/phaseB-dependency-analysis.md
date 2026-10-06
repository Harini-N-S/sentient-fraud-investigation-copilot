# Phase B Dependency Analysis & Separation Matrix
## Rawbank Sentient Fraud Intelligence Platform

**Document Reference:** `docs/phaseB-dependency-analysis.md`  
**Phase:** Phase B — Separate Integrated Platform into Two Distinct Systems  
**Master Repository:** `c:\Users\Balaji\OneDrive\Desktop\bank` (Safe Master Backup)  
**Destination Systems:**
1. `sentient-command-centre` (`../sentient-command-centre/`)
2. `sentient-fraud-investigation-copilot` (`../sentient-fraud-investigation-copilot/`)

---

### Executive Objective

The master repository currently houses a complete, integrated enterprise platform serving two distinct operational fraud use cases:
1. **Sentient Command Centre:** Operational triage, real-time KPI surveillance, alert prioritization, multi-currency transaction ledger auditing, and customer risk profiling.
2. **Sentient Fraud Investigation Copilot:** Conversational, evidence-grounded AI forensic workspace, entity resolution, multi-hop evidence packet assembly, deterministic pre-checks, counter-evidence analysis, and escalation recommendations.

This document classifies every file, route, component, rule, database table, and test across the codebase to ensure a clean, decoupled separation without breaking working functionality, losing data provenance, or mutating the master repository.

---

### Classification Scheme

* `COMMAND_CENTRE_ONLY`: Exclusively utilized for monitoring, triage, ledger auditing, and operational surveillance.
* `COPILOT_ONLY`: Exclusively utilized for conversational investigation, query parsing, LLM prompt engineering, and forensic synthesis.
* `SHARED`: Required by both independent repositories (e.g., synthetic database, entity models, evidence extraction, graph relationships, Rawbank design tokens).
* `UNCERTAIN`: Under evaluation (resolved via import and runtime trace).

---

### A. Frontend Pages & Components

| Component / Page | File Path | Classification | Runtime Justification & Decision |
| :--- | :--- | :---: | :--- |
| **Command Centre Page** | `frontend/src/pages/CommandCentrePage.tsx` | `COMMAND_CENTRE_ONLY` | Primary operations dashboard: 4+3 KPI metric cards, immediate operational triage table, alert scenarios distribution, mule funnel watchlist. Removed from Copilot. |
| **Alerts Triage Page** | `frontend/src/pages/AlertsPage.tsx` | `COMMAND_CENTRE_ONLY` | Dedicated forensic queue with severity filtering, scenario filters, sorting, and pagination. Removed from Copilot. |
| **Transactions Page** | `frontend/src/pages/TransactionsPage.tsx` | `COMMAND_CENTRE_ONLY` | Synthetic multi-currency ledger (CDF/USD), channel mapping (`IllicoCash`, `RawbankOnline`, `Express POS`, `ATM`), and location filtering. Removed from Copilot. |
| **Customers Page** | `frontend/src/pages/CustomersPage.tsx` | `COMMAND_CENTRE_ONLY` | Surveillance directory with KYC tiers (`Tier 1 Basic`, `Tier 2 Standard`, `Tier 3 Full`), segment profiles, and risk tiers. Removed from Copilot. |
| **Copilot Page** | `frontend/src/pages/CopilotPage.tsx` | `COPILOT_ONLY` | Core forensic conversational workspace: suggested inquiry prompts, session management, structured dossier display (executive summary, risk assessment, supporting/counter evidence, gaps, checklist). Removed from Command Centre. |
| **App Shell (`App.tsx`)** | `frontend/src/App.tsx` | `SHARED` (Adapted) | Command Centre App shell mounts: Command Centre, Alerts, Transactions, Customers. Copilot App shell mounts: Copilot Workspace with session state and entity inspector. |
| **Top Navigation (`Navbar.tsx`)** | `frontend/src/components/Navbar.tsx` | `SHARED` | Retained in both: Rawbank logo lockup, dual DRC clocks (Kinshasa/Lubumbashi), synthetic disclaimer pill, quick search trigger. |
| **Sidebar Navigation (`Sidebar.tsx`)** | `frontend/src/components/Sidebar.tsx` | `SHARED` (Adapted) | Command Centre: 4 operational items (`Command Centre`, `Alerts`, `Transactions`, `Customers`). Copilot: Dedicated workspace navigation (`Investigation Copilot`, `New Investigation`, `Audit Trail`). |
| **Metric Card (`MetricCard.tsx`)** | `frontend/src/components/MetricCard.tsx` | `COMMAND_CENTRE_ONLY` | Reusable KPI metric card used exclusively on `CommandCentrePage.tsx`. |
| **Entity Drawer (`EntityDrawer.tsx`)** | `frontend/src/components/EntityDrawer.tsx` | `SHARED` | Slide-over inspector displaying entity details, 4-tier evidence dossiers, and relationship graphs upon row selection or citation click. |
| **Evidence Dossier (`EvidenceDossier.tsx`)** | `frontend/src/components/EvidenceDossier.tsx` | `SHARED` | Renders structured evidence items, counter-evidence pills, and data gaps inside `EntityDrawer.tsx`. |
| **Relationship Tree (`RelationshipTree.tsx`)** | `frontend/src/components/RelationshipTree.tsx` | `SHARED` | Visualizes 2-hop entity network connections; used in Command Centre for fraud pattern analysis and in Copilot for network correlation. |
| **Global Search Modal (`GlobalSearchModal.tsx`)**| `frontend/src/components/GlobalSearchModal.tsx` | `SHARED` | `Ctrl+K` omni-search for Customers, Transactions, Alerts, Devices, and Beneficiaries. |
| **Rawbank Logo (`RawbankLogo.tsx`)** | `frontend/src/components/RawbankLogo.tsx` | `SHARED` | Vector Congolese Leopard emblem and corporate typography lockup. |
| **Design System (`index.css`)** | `frontend/src/styles/index.css` | `SHARED` | Centralized `--rawbank-...` tokens, typography, dark obsidian theme, utility classes. |
| **Frontend API Service (`api.ts`)** | `frontend/src/services/api.ts` | `SHARED` (Adapted) | Filtered to include only endpoints needed by each independent application. |

---

### B. Backend API Endpoints

| Router / Endpoint | Method & Route | Classification | Consumer & Action |
| :--- | :--- | :---: | :--- |
| **Health** | `GET /api/health` | `SHARED` | Liveness check; needed by both systems. |
| **Overview** | `GET /api/overview` | `COMMAND_CENTRE_ONLY` | Primary dashboard metrics, alert counts, and mule summaries. |
| **Alerts** | `GET /api/alerts`<br>`GET /api/alerts/{id}` | `COMMAND_CENTRE_ONLY` | Triage table query with pagination and filters. |
| **Alert Evidence** | `GET /api/alerts/{id}/evidence` | `SHARED` | Used by Command Centre drawer and Copilot investigation. |
| **Transactions** | `GET /api/transactions`<br>`GET /api/transactions/{id}` | `COMMAND_CENTRE_ONLY` | Transaction ledger stream with channel and currency filters. |
| **Transaction Evidence** | `GET /api/transactions/{id}/evidence` | `SHARED` | Transaction-level evidence assembly. |
| **Customers** | `GET /api/customers`<br>`GET /api/customers/{id}` | `COMMAND_CENTRE_ONLY` | Customer risk surveillance directory. |
| **Customer Evidence** | `GET /api/customers/{id}/evidence` | `SHARED` | Behavioral baseline and KYC evidence lookup. |
| **Devices** | `GET /api/devices/{id}` | `SHARED` | Hardware fingerprint detail for drawer and Copilot. |
| **Beneficiaries** | `GET /api/beneficiaries/{id}` | `SHARED` | Mule account destination profile. |
| **Entities** | `GET /api/entities/{type}/{id}/evidence`<br>`GET /api/entities/{type}/{id}/related` | `SHARED` | Multi-hop relationship graph exploration. |
| **Signals** | `GET /api/signals`<br>`GET /api/signals/{id}` | `COMMAND_CENTRE_ONLY` | Raw deterministic fraud signal audit. |
| **Evaluate** | `POST /api/evaluate` | `COMMAND_CENTRE_ONLY` | Ad-hoc transaction rule evaluation endpoint. |
| **Search** | `GET /api/search` | `SHARED` | Fuzzy & exact entity resolution for search modal and Copilot query routing. |
| **Retrieval Query** | `POST /api/retrieval/query` | `COPILOT_ONLY` | Natural language evidence retrieval engine. |
| **Copilot Investigate**| `POST /api/copilot/investigate` | `COPILOT_ONLY` | Primary multi-turn conversational investigation endpoint. |
| **Copilot Explain Alert** | `POST /api/copilot/explain/alert/{id}` | `COPILOT_ONLY` | Deep forensic explanation of specific alert. |
| **Copilot Explain Transaction** | `POST /api/copilot/explain/transaction/{id}` | `COPILOT_ONLY` | Deep forensic explanation of specific transaction. |
| **Copilot Explain Customer** | `POST /api/copilot/explain/customer/{id}` | `COPILOT_ONLY` | Deep forensic explanation of specific customer baseline. |

---

### C. Database Tables (`database/synthetic_bank.db`)

All 9 synthetic database tables represent the unified synthetic financial reality of Rawbank DRC:

| Table Name | Established Row Count | Classification | Retention Rationale |
| :--- | :---: | :---: | :--- |
| `customers` | 120 | `SHARED` | Command Centre displays surveillance profiles; Copilot evaluates customer identity, KYC, and city risk. |
| `accounts` | 240 | `SHARED` | Dual-currency CDF/USD ledger balances required by both systems. |
| `devices` | 150 | `SHARED` | Device sharing and emulator detection required by both systems. |
| `beneficiaries` | 180 | `SHARED` | Mule funnel targets and destination entities required by both systems. |
| `transactions` | 900 | `SHARED` | Transaction ledger records, velocity spikes, and structured smurfing events. |
| `authentication_activities` | 450 | `SHARED` | Credential stuffing, impossible travel, and ATO detection. |
| `behavioural_baselines` | 120 | `SHARED` | Velocity and ticket size thresholds for baseline deviation calculations. |
| `alerts` | 140 | `SHARED` | High-risk events requiring triage in Command Centre and explanation in Copilot. |
| `fraud_signals` | 200 | `SHARED` | Deterministic signal indicators backing composite risk scores. |

**Database Decision:** Both repositories will retain an identical, standalone copy of `database/synthetic_bank.db` and `database/schema/init_schema.sql` to ensure 100% data fidelity and identical record counts (2,400 entities / events).

---

### D. Fraud Rules (`rules/`)

| Module | Rules Covered | Classification | Rationale |
| :--- | :--- | :---: | :--- |
| `rules/engine.py` | Composite Risk Scorer & Engine | `SHARED` | Evaluates deterministic signals into 0–100 risk scores; required by Command Centre for alert prioritization and by Copilot as the immutable risk anchor. |
| `rules/base.py` | `BaseRule` class & interfaces | `SHARED` | Core rule definitions. |
| `rules/authentication.py` | R01 (Credential Stuffing), R02 (Impossible Travel) | `SHARED` | Used in Command Centre evaluation and Copilot deterministic checks. |
| `rules/device.py` | R03 (New Device High Amount), R04 (Device Sharing ATO) | `SHARED` | Identifies hardware compromises. |
| `rules/velocity.py` | R05 (Velocity Burst Spike) | `SHARED` | Identifies burst transaction frequencies. |
| `rules/value_spike.py` | R06 (Baseline Value Spike) | `SHARED` | Identifies severe volume deviations. |
| `rules/structuring.py` | R07 (Smurfing / Structuring under AML threshold) | `SHARED` | Identifies cash structuring below BCC declaration limits ($10,000). |
| `rules/beneficiary.py` | R08 (Mule Funnel Fan-In Aggregation) | `SHARED` | Detects multi-sender aggregation to single beneficiary. |
| `rules/geographic.py` | R09 (High-Risk Mining Corridor Anomaly) | `SHARED` | Detects provincial routing anomalies (e.g. Kolwezi vs Kinshasa). |
| `rules/behavioural.py` | R10 (Dormant Account Awakening), R11 (Off-Hours Bulk Dispersal) | `SHARED` | Detects behavioral divergence from historical baselines. |
| `rules/evidence.py` | Evidence formatting utilities | `SHARED` | Formats deterministic findings for UI presentation. |

---

### E. Retrieval / Evidence Layer (`backend/app/retrieval/`)

| Module | Purpose | Classification | System Assignment |
| :--- | :--- | :---: | :--- |
| `indexer.py` | SQLite FTS and in-memory entity inverted index | `SHARED` | Powers both `/api/search` (Command Centre) and forensic retrieval (Copilot). |
| `entity_resolver.py` | Resolves entity IDs from strings / names / codes | `SHARED` | Used by Command Centre search modal and Copilot inquiry resolution. |
| `evidence_builder.py` | Builds 4-tier structured evidence packets | `SHARED` | Generates evidence for `EntityDrawer` (Command Centre) and the Copilot prompt/response. |
| `models.py` | Pydantic evidence schemas | `SHARED` | Core data models. |
| `query_parser.py` | Parses natural language questions into search intents | `COPILOT_ONLY` | Exclusively utilized by Copilot investigative router. |
| `ranking.py` | Re-ranks evidence snippets by relevance | `COPILOT_ONLY` | Exclusively utilized by Copilot retrieval pipeline. |
| `retriever.py` | Multi-hop evidence graph traversal | `COPILOT_ONLY` | Orchestrates evidence gathering for Copilot prompts. |

---

### F. Copilot / LLM Components (`backend/app/llm/`)

| Module | Purpose | Classification | System Assignment |
| :--- | :--- | :---: | :--- |
| `client.py` | Groq API async client with retry logic | `COPILOT_ONLY` | Removed from Command Centre backend. |
| `context_manager.py` | Multi-turn conversation and entity memory | `COPILOT_ONLY` | Removed from Command Centre backend. |
| `mock_adapter.py` | Deterministic evidence synthesis engine (fallback) | `COPILOT_ONLY` | Removed from Command Centre backend. |
| `prompts.py` | System prompt, few-shot prompts, banking persona | `COPILOT_ONLY` | Removed from Command Centre backend. |
| `schemas.py` | Structured Copilot response Pydantic models | `COPILOT_ONLY` | Removed from Command Centre backend. |
| `service.py` | Copilot investigation service orchestration | `COPILOT_ONLY` | Removed from Command Centre backend. |

---

### G. Repositories (`backend/app/repositories/`)

| Repository | Purpose | Classification |
| :--- | :--- | :---: |
| `base.py` | Database connection context and base queries | `SHARED` |
| `overview_repo.py` | Aggregates dashboard metrics and mule accounts | `COMMAND_CENTRE_ONLY` |
| `alert_repo.py` | Alert queries, severity filters, sorting | `SHARED` (Used for both alert list and alert detail) |
| `transaction_repo.py`| Transaction queries, channel & currency filters | `SHARED` (Used for ledger list and evidence lookup) |
| `customer_repo.py` | Customer queries, KYC & segment filters | `SHARED` (Used for surveillance list and profile lookup) |
| `device_repo.py` | Device queries and hardware details | `SHARED` |
| `beneficiary_repo.py`| Beneficiary queries and routing details | `SHARED` |
| `entity_repo.py` | Multi-hop graph relationship traversal | `SHARED` |
| `search_repo.py` | Unified entity text search | `SHARED` |
| `signal_repo.py` | Signal log queries | `COMMAND_CENTRE_ONLY` |

---

### H. Tests

#### 1. Backend Tests (`tests/`)

| Test File | Total Tests | Target System | Classification |
| :--- | :---: | :---: | :---: |
| `tests/test_rules_engine.py` | 24 | Both Systems | `SHARED` (Verifies deterministic rules in both) |
| `tests/test_api.py` | 24 | Command Centre | `COMMAND_CENTRE_ONLY` (Tests overview, alerts, transactions, customers, devices, etc.) |
| `tests/test_customer_filters.py`| 7 | Command Centre | `COMMAND_CENTRE_ONLY` (Tests customer segment, KYC, and risk query filters) |
| `tests/test_retrieval.py` | 37 | Copilot | `COPILOT_ONLY` (Tests entity resolution, query parsing, ranking, evidence builder) |
| `tests/test_copilot.py` | 27 | Copilot | `COPILOT_ONLY` (Tests Copilot investigation, mock synthesis fallback, sessions) |

#### 2. Frontend Tests (`frontend/src/test/`)

| Test Numbers | Focus Area | Target System | Classification |
| :--- | :--- | :---: | :---: |
| **Tests 1–9** | Command Centre, KPIs, Alerts Table, Entity Drawer, Search, Relationships | Command Centre | `COMMAND_CENTRE_ONLY` |
| **Tests 10–18** | Copilot console, prompt submit, structured sections, citations, evidence gaps, sessions | Copilot | `COPILOT_ONLY` |
| **Tests 19–21** | Transaction ledger channel filter, currency filter (CDF & USD), filter reset | Command Centre | `COMMAND_CENTRE_ONLY` |
| **Tests 22–28** | CustomersPage segment, KYC status, risk category, city filters, combined filters | Command Centre | `COMMAND_CENTRE_ONLY` |

---

### I. Architectural Separation Blueprint

```
Master Project (c:\Users\Balaji\OneDrive\Desktop\bank) [PRESERVED UNTOUCHED]
 │
 ├──▶ Clone 1: c:\Users\Balaji\OneDrive\Desktop\sentient-command-centre
 │     │
 │     ├── Frontend: CommandCentrePage, AlertsPage, TransactionsPage, CustomersPage, EntityDrawer, Search
 │     ├── Backend: Overview, Alerts, Transactions, Customers, Devices, Beneficiaries, Entities, Search, Signals, Evaluate
 │     ├── Rules: 11 Deterministic Fraud Rules + Composite Engine
 │     ├── Database: Complete Synthetic SQLite Database (2,400 entities/events)
 │     └── Tests: 19 Frontend Tests + 55 Backend Tests
 │
 └──▶ Clone 2: c:\Users\Balaji\OneDrive\Desktop\sentient-fraud-investigation-copilot
       │
       ├── Frontend: CopilotPage (Investigation Workspace), EntityDrawer (Citations), Search Modal
       ├── Backend: Copilot Investigate, Explain Alert/Tx/Cust, Retrieval Query, Entity Evidence, Search
       ├── Retrieval: Query Parser, Entity Resolver, Evidence Builder, Ranking, Retriever
       ├── LLM: Groq Client, System Prompts, Context Manager, Deterministic Synthesis Fallback
       ├── Rules: 11 Deterministic Fraud Rules (Grounded Anchors)
       ├── Database: Complete Synthetic SQLite Database (2,400 entities/events)
       └── Tests: 9 Frontend Tests + 88 Backend Tests
```

---

### J. Separation Action Plan

1. **Safety Guarantee:** The master repository `c:\Users\Balaji\OneDrive\Desktop\bank` remains completely untouched.
2. **Directory Creation:** Create `c:\Users\Balaji\OneDrive\Desktop\sentient-command-centre` and `c:\Users\Balaji\OneDrive\Desktop\sentient-fraud-investigation-copilot`.
3. **File Copying:** Copy files into both sibling directories.
4. **Command Centre Pruning:** Remove Copilot routes (`routers/copilot.py`, `routers/retrieval.py`, `app/llm/`, `CopilotPage.tsx`), update `App.tsx` and `Sidebar.tsx`, adapt tests.
5. **Copilot Pruning:** Remove Command Centre monitoring views (`CommandCentrePage.tsx`, `AlertsPage.tsx`, `TransactionsPage.tsx`, `CustomersPage.tsx`, `routers/overview.py`, `routers/alerts.py`, etc.), update `App.tsx` and `Sidebar.tsx`, adapt tests.
6. **Documentation:** Add dedicated `README.md`, `docs/system-scope.md`, and `docs/architecture.md` to each repository.
7. **Verification:** Run all tests, builds, and health checks on both independent repositories.
