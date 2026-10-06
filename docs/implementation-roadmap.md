# Implementation Roadmap: Phases 1 Through 12
## Sentient Fraud Intelligence Platform (aXtrLabs)

**Target Bank:** Rawbank (DRC)  
**Document Purpose:** Phased Execution Master Plan  
**Current Phase:** Phase 1 (In Progress / Completing)  
**Governance Constraint:** Sequential Phase Execution — No Future Phase Implementation Permitted During Phase 1

---

### Phase Summary Matrix

| Phase | Phase Title | Status | Primary Output |
| :---: | :--- | :---: | :--- |
| **01** | Project Foundation + Enterprise Context | **Active (Finalizing)** | Complete architectural & context documentation suite under `docs/`. |
| **02** | Synthetic Banking Data + Data Model | Pending Phase 1 Sign-off | 2,500 validated synthetic records across all core banking entities. |
| **03** | Fraud Rules + Deterministic Intelligence | Queued | Executable deterministic rules engine & computed fraud signals. |
| **04** | Backend + Data Access APIs | Queued | REST / Fast API service providing data, graph, and triage endpoints. |
| **05** | Sentient Command Centre (Core Console) | Queued | Operational triage dashboard (Monitor → Prioritise → Analyse). |
| **06** | Command Centre Drill-Down + Relationships | Queued | Deep entity inspector, transaction timeline, and graph visualizer. |
| **07** | Groq Intelligence Layer | Queued | Groq client, model prompts, and retrieval evidence assembler. |
| **08** | Sentient Fraud Investigation Copilot | Queued | Forensic investigation assistant UI integrated into console. |
| **09** | Evidence-Grounded Reasoning & Entity Correlation | Queued | Anti-hallucination citation engine, counter-evidence evaluator. |
| **10** | End-to-End System Integration | Queued | Unified single-page experience linking Command Centre & Copilot. |
| **11** | Validation, Testing & Verification | Queued | Automated scenario tests, false-positive benchmarks, audit tests. |
| **12** | Refinement, Polish & Demo Readiness | Queued | High-fidelity UI polish, demo walkthrough script, packaging. |

---

### Detailed Phase Specifications

---

#### PHASE 1: Project Foundation + Enterprise Context
* **Objective:** Establish the foundational architecture, inspect existing workspace, document authoritative resource status, define the Rawbank enterprise & design context, specify domain entities, and plan the roadmap before writing any application code or generating data.
* **Major Components:** Project inventory audit, resource status tracker, Rawbank enterprise context report, design system specification, domain model schema plan, 8-layer intelligence architecture, use-case specifications, implementation roadmap, requirements checklist.
* **Dependency:** None (Initial Phase).
* **Expected Output:** Complete, validated documentation suite in `docs/` with zero premature code or synthetic data generation.

---

#### PHASE 2: Synthetic Banking Data + Data Model
* **Objective:** Generate a robust, realistic, self-consistent synthetic banking dataset representing Rawbank’s Congolese operating environment (CDF and USD dual currency, retail, corporate, and agency channels) totaling **2,500 records**.
* **Major Components:** Synthetic generator script, seed distributions reflecting Rawbank customer demographics, transactional event simulator, fraud typology scenario injectors (ATO, mule rings, structuring, cardless ATM cash-outs, agent collusion), database schema migration (SQLite/PostgreSQL).
* **Dependency on Previous Phases:** Phase 1 (`docs/domain-model.md`, `docs/rawbank-enterprise-context.md`).
* **Expected Output:** Populated, relational synthetic database with 2,500 records and zero PII, ready for deterministic querying.

---

#### PHASE 3: Fraud Rules + Deterministic Intelligence
* **Objective:** Implement the zero-hallucination deterministic rules engine executing high-speed mathematical and categorical evaluations on the synthetic dataset.
* **Major Components:** Rules execution pipeline, velocity calculators (time-window rolling sums), threshold validators, impossible travel detector (geographic velocity), credential anomaly detectors, composite risk scoring formula (0–100).
* **Dependency on Previous Phases:** Phase 2 (Synthetic dataset).
* **Expected Output:** Populated `Alert` and `FraudSignal` tables with deterministic scores, rule codes, and quantified indicators.

---

#### PHASE 4: Backend + Data Access APIs
* **Objective:** Construct the high-performance backend API service to expose structured data, computed alerts, and entity relationships to the user interface.
* **Major Components:** API server (FastAPI / Express), route handlers (`/api/alerts`, `/api/customers/:id`, `/api/transactions`, `/api/timeline`), query optimization, entity resolution graph service.
* **Dependency on Previous Phases:** Phase 2 (Database), Phase 3 (Rules Engine).
* **Expected Output:** Working, documented backend API service returning structured JSON responses with millisecond latency.

---

#### PHASE 5: Sentient Command Centre (Core Console)
* **Objective:** Construct the macro operational surveillance console allowing fraud analysts to monitor, prioritize, and analyze fleet-wide activity.
* **Major Components:** Enterprise Single-Page Application (SPA), dark-mode design system implementation (`#0B0E14` palette), live KPI ribbon, prioritized triage queue table, search and multi-criteria filters (channel, risk tier, currency).
* **Dependency on Previous Phases:** Phase 1 (`docs/rawbank-design-context.md`), Phase 4 (Backend APIs).
* **Expected Output:** High-density, responsive operational Command Centre UI displaying prioritized alerts.

---

#### PHASE 6: Command Centre Drill-Down + Relationships
* **Objective:** Build the interactive drill-down capabilities within the Command Centre for deep entity inspection and relationship visualization.
* **Major Components:** Contextual inspector drawer/panel, interactive 30-day chronological transaction timeline, customer profile snapshot, linked entity graph visualizer (detecting shared devices and mule counterparties).
* **Dependency on Previous Phases:** Phase 5 (Command Centre UI), Phase 4 (Graph APIs).
* **Expected Output:** Interactive inspector view displaying full customer forensic context with one-click drill-down.

---

#### PHASE 7: Groq Intelligence Layer
* **Objective:** Integrate the ultra-low-latency Groq LLM API with structured evidence assembler pipelines to deliver grounded AI reasoning.
* **Major Components:** Groq client integration (e.g. Llama-3 / Mixtral models), Evidence Packet Assembler (retrieving customer baselines, triggered rules, and transaction history), structured system prompts, JSON output formatting.
* **Dependency on Previous Phases:** Phase 1 (`docs/architecture-plan.md`), Phase 4 (Data Access).
* **Expected Output:** Working Groq intelligence service that returns structured forensic evaluations grounded strictly in evidence packets.

---

#### PHASE 8: Sentient Fraud Investigation Copilot
* **Objective:** Develop the interactive forensic investigation workstation UI seamlessly docked with the Command Centre.
* **Major Components:** Copilot chat and reasoning panel, quick-action prompt pills ("Explain this Alert", "Evaluate Counter-Evidence", "Check for Mule Network"), streaming response renderer, evidence card citations.
* **Dependency on Previous Phases:** Phase 5 & 6 (Command Centre & Inspector), Phase 7 (Groq API).
* **Expected Output:** Fully interactive Copilot panel embedded in the console, responsive to analyst queries on the active entity.

---

#### PHASE 9: Evidence-Grounded Reasoning & Entity Correlation
* **Objective:** Implement strict anti-hallucination guardrails, mandatory evidence citation checks, and counter-evidence analysis in Copilot responses.
* **Major Components:** Citation verification engine (validating every claim against database IDs), counter-evidence extraction algorithm, behavioral deviation scoring module, missing evidence gap reporter.
* **Dependency on Previous Phases:** Phase 7 (Groq prompts), Phase 8 (Copilot UI).
* **Expected Output:** Verifiable, hallucination-free Copilot reasoning where every claim links directly to a database record or deterministic rule.

---

#### PHASE 10: End-to-End System Integration
* **Objective:** Unify the Sentient Command Centre and the Sentient Fraud Investigation Copilot into a seamless, single-window enterprise experience.
* **Major Components:** Shared state synchronization (row selection instantly seeds Copilot context), bi-directional actions (Copilot recommendations trigger alert status updates in Command Centre), audit logging service.
* **Dependency on Previous Phases:** Phases 5 through 9.
* **Expected Output:** Cohesive, end-to-end platform operating synchronously over the shared synthetic banking environment.

---

#### PHASE 11: Validation, Testing & Verification
* **Objective:** Validate the entire platform against predefined fraud scenarios, performance benchmarks, and regulatory requirements.
* **Major Components:** Automated end-to-end test suite, scenario validation (ATO scenario, mule network scenario, cardless ATM exploit scenario, legitimate VIP false positive scenario), API latency testing, evidence citation verification tests.
* **Dependency on Previous Phases:** Phase 10 (Integrated Platform).
* **Expected Output:** Verified platform passing all test scenarios with documented test reports and zero regressions.

---

#### PHASE 12: Refinement, Polish & Demo Readiness
* **Objective:** Polish the user experience, optimize aesthetics to enterprise executive presentation quality, and prepare complete demonstration materials.
* **Major Components:** Visual polish (micro-animations, typography, contrast tuning), demo walk-through script, comprehensive README and architecture guide, containerized run script / single-command startup.
* **Dependency on Previous Phases:** Phase 11 (Validated Platform).
* **Expected Output:** Turn-key, production-grade demonstration platform with executive documentation ready for stakeholder evaluation.
