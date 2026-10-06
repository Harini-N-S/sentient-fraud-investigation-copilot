# Assignment Resources Status & Audit Log
## Rawbank – Sentient Fraud Intelligence Platform (aXtrLabs)

**Status Date:** 2026-09-28  
**Phase:** Phase 1 (Foundation & Context)

---

### 1. Overview of Assignment Resources

The assignment guidelines reference a set of authoritative assets designed to guide the architecture, synthetic data schema, fraud rule engine, and use-case experience. In accordance with strict Phase 1 governance:
* **Rule 1:** If resources are present, they are authoritative and must be strictly followed.
* **Rule 2:** If resources are missing, their absence must be clearly logged without fabricating their contents.
* **Rule 3:** No arbitrary technology or schema choices may be locked in that would conflict with missing resources.

---

### 2. Comprehensive Resource Audit Table

| Resource Identifier | Description / Expected Role | Local Status | Fallback / Governance Protocol |
| :--- | :--- | :--- | :--- |
| **`BuildStack.png`** | Architectural stack diagram specifying tiers, protocols, Groq integration pattern, and frontend/backend components. | **Missing** | Architecture is designed around the assignment's explicit dataflow: `Structured Data → Deterministic Processing → Entity Resolution → Semantic Retrieval → LLM Intelligence (Groq) → Backend → Frontend → Experience`. No incompatible frameworks are introduced. |
| **`SentientData_RuleSet.md`** | Authoritative specifications of deterministic fraud rules, rule IDs, scoring formulas, threshold values, and trigger conditions. | **Missing** | The framework reserves rule categorization slots (Velocity, Value Spikes, ATO / Credential Anomalies, Mule Structuring, Impossible Travel, Agent Anomalies). All specific thresholds and rule codes are marked `[To be confirmed from SentientData_RuleSet.md]`. |
| **`SyntheticData_Fuel`** | Seed data profiles, probability distributions, customer demographics, transaction volumes, and fraud injection scenarios. | **Missing** | Generation of the 2,500 synthetic records is strictly deferred to Phase 2. Core entity schemas are defined abstractly in `domain-model.md`. |
| **`UsecaseONE_stuff.txt`** | Detailed specifications, wireframes, or test cases for the Sentient Command Centre (Monitor → Prioritise → Analyse → Drill Down). | **Missing** | The Command Centre workflow is architected using core enterprise risk management principles and explicit prompt requirements. Specific fields are marked `[To be confirmed from UsecaseONE_stuff.txt]`. |
| **`UsecaseTWO_stuff.txt`** | Detailed specifications for the Sentient Fraud Investigation Copilot (Investigate → Correlate → Explain → Recommend → Escalate). | **Missing** | The Copilot workflow is architected using evidence-grounded AI reasoning patterns. Specific prompt templates or test cases are marked `[To be confirmed from UsecaseTWO_stuff.txt]`. |
| **`Working Sheet`** | Analyst notes, rubrics, evaluation criteria, or grading checklist. | **Missing** | Monitored as an external dependency; requirements are mapped into `requirements-checklist.md`. |
| **`Clue Deck`** | Investigation scenarios, hidden synthetic fraud clues, or storyline walkthroughs. | **Missing** | Flagged as pending user provision. No speculative narratives are hardcoded. |
| **`Reference Documents` / Walkthrough** | Supporting implementation guides or architectural walkthroughs. | **Missing** | Documented as missing. Standard enterprise banking architectures are applied. |

---

### 3. Procedure for Incorporating Resources When Provided

When the user or client provides any of the missing files:
1. Place the files into the workspace directory (e.g., in a dedicated `resources/` or `assignment_data/` folder).
2. Phase 1 documentation (`docs/domain-model.md`, `docs/architecture-plan.md`, `docs/use-cases.md`) will be reviewed and updated to incorporate exact field names, rule IDs, and prompt templates.
3. No code from Phase 2 onwards will proceed without cross-checking against these authoritative files.
