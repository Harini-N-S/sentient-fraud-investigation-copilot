# Intelligence Architecture Plan
## Sentient Fraud Intelligence Platform (aXtrLabs)

**Target Bank:** Rawbank (DRC)  
**Phase:** Phase 1 — Project Foundation & Architecture Planning  
**Execution Rule:** Foundation Plan Only (No AI or Backend Code Implemented in Phase 1)

---

### 1. Architectural Philosophy & Core Tenet

> [!IMPORTANT]
> **THE LLM IS NOT THE DATABASE**  
> Large Language Models (LLMs) are reasoning engines, not factual data stores. LLMs suffer from hallucinations, lack direct access to volatile ledgers, and cannot perform precise deterministic calculations at banking scale.  
> In the Sentient Fraud Intelligence Platform, **the database is the single source of truth**. The Groq LLM Intelligence layer functions strictly as a forensic synthesizer, hypothesis generator, and investigative co-pilot operating on verified, retrieved evidence tokens.

---

### 2. End-to-End Pipeline Architecture

The platform architecture strictly implements the assignment's specified 8-stage intelligence dataflow:

```
┌────────────────────────────────────────────────────────┐
│                   Structured Data                      │
│        (Customers, Accounts, Transactions, Logs)       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               Deterministic Processing                 │
│         (Velocity, Thresholds, Impossible Travel)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Entity Resolution                     │
│         (Mule Rings, Shared Devices, Phone Clones)     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Semantic Retrieval                    │
│      (Baseline Profiles, Evidence Tokens, Typologies)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             LLM Intelligence (via Groq)                │
│    (Forensic Reasoning, Explanations, Recommendations) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Backend Services                     │
│         (FastAPI / Node, Caching, Event Orchestration) │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Frontend Presentation                  │
│       (High-Density Operations Console, UI State)      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Application Experience                 │
│    Sentient Command Centre  ↔  Fraud Copilot Workstation│
└────────────────────────────────────────────────────────┘
```

---

### 3. Detailed Technical Responsibilities by Layer

#### Layer 1: Structured Data (Storage & Schema)
* **What it does:** Serves as the immutable factual foundation. Contains the synthetic entities defined in `docs/domain-model.md` (Customers, Accounts, Transactions, Beneficiaries, Devices, AuthActivity, Alerts).
* **Storage Strategy:** Relational persistence (e.g. SQLite for zero-configuration local execution or PostgreSQL) guaranteeing ACID transactions, foreign-key integrity, and millisecond query access for tabular financial ledgers.
* **Invariant:** Every financial movement is permanently stamped with an immutable UTC timestamp, transaction ID, and currency denominator (CDF/USD).

#### Layer 2: Deterministic Processing (Rules Engine)
* **What it does:** Executes high-speed, mathematical, zero-hallucination validation rules across incoming transactions and historical time windows.
* **Examples of Deterministic Rules:**
  * *Velocity Check:* 5 transfers within 3 minutes exceeding $2,000 equivalent.
  * *Threshold Breach:* Single transaction > $10,000 without Tier-3 KYC verification.
  * *Impossible Travel:* Device session in Kinshasa followed 20 minutes later by an ATM withdrawal in Lubumbashi (1,500 km away).
  * *ATO Pattern:* Password reset + New Device Enrolled + Max Limit Transfer within 10 minutes.
* **Output:** Generates discrete `FraudSignal` records with quantitative severity scores and rule IDs (to be synced with `SentientData_RuleSet.md`).

#### Layer 3: Entity Resolution (Graph & Correlation Engine)
* **What it does:** Resolves non-obvious relationships across disparate records to uncover organized fraud syndicates.
* **Core Functions:**
  * Matches shared device fingerprints across multiple accounts with different customer names.
  * Detects mule account clusters routing money to identical external phone numbers or beneficiary wallets.
  * Constructs an in-memory graph of vertices (Customers, Devices, Accounts, Counterparties) and edges (Transacted_To, Logged_In_From, Shared_With).
* **Output:** Produces connected subgraph clusters with linked risk multipliers.

#### Layer 4: Semantic Retrieval (Context & Evidence Assembler)
* **What it does:** Packages raw structured facts into structured, token-bounded **Evidence Packets** ready for AI consumption.
* **Mechanism:**
  * Retrieves the customer's 60-day `BehaviouralBaseline` (normal spend, usual hours, common recipients).
  * Gathers all deterministic `FraudSignal` items and entity resolution links.
  * Selects relevant anti-fraud typologies or regulatory policy guidelines (e.g., Banque Centrale du Congo circulars).
* **Output:** A deterministic JSON payload representing the complete ground truth required to answer an investigator's query.

#### Layer 5: LLM Intelligence Layer (Groq Acceleration)
* **What it does:** Consumes the retrieved Evidence Packet and delivers fast, high-quality analytical reasoning via the Groq API (utilizing models such as Llama 3 / Mixtral for ultra-low inference latency).
* **What it is Allowed to do:**
  * Explain *why* an activity was flagged in plain, natural English/French.
  * Correlate disparate signals (e.g., connecting a dormant account sudden reactivation with a device change).
  * Highlight **counter-evidence** (e.g., noting that the customer confirmed biometric login on their primary phone).
  * Identify **evidence gaps** (e.g., noting that SIM swap status from the mobile carrier is unknown).
  * Propose investigator actions (e.g., "Place temporary freeze on Account ACC-901; request branch verification").
* **What it is Strictly Prohibited from doing:**
  * Guessing account balances or transaction amounts not present in the evidence packet.
  * Inventing customer IDs or dates.
  * Making irreversible autonomous decisions without human analyst sign-off.

#### Layer 6: Backend Services (Orchestration & Data Access APIs)
* **What it does:** Provides the secure API interface bridging the storage/reasoning pipeline with the user interface.
* **Core Endpoints Planned:**
  * `GET /api/alerts`: Triage queue with filtering, pagination, and sorting.
  * `GET /api/alerts/:id/drilldown`: Full forensic dossier (timeline, graph links, rule calculations).
  * `POST /api/copilot/chat`: Context-aware investigation endpoint querying Groq with strictly grounded evidence packets.
  * `POST /api/alerts/:id/action`: Analyst action dispatcher (freeze, dismiss, escalate to AML).

#### Layer 7: Frontend Presentation (Enterprise Risk Console)
* **What it does:** Single-Page Application (SPA) designed according to `docs/rawbank-design-context.md`.
* **Ergonomics:**
  * High-density tables with instant client-side filtering.
  * Visual timeline charts tracking customer events over time.
  * Visual entity relationship trees.
  * Tabular numeric alignment for CDF and USD currencies.

#### Layer 8: Application Experience (Two Connected Workspaces)
* **The Unified Experience:**
  * **Sentient Command Centre:** The operational radar screen for fleet-wide monitoring and triage.
  * **Sentient Fraud Investigation Copilot:** The deep-dive forensic investigator docked alongside or linked to the Command Centre.
  * Both operate simultaneously on the exact same underlying state and synthetic environment.

---

### 4. The 4-Tier Information Classification Model

To guarantee 100% transparency and prevent cognitive confusion, the platform enforces strict visual and structural segregation across four categories of information:

| Information Tier | Definition | Source of Truth | Visual Representation |
| :--- | :--- | :--- | :--- |
| **1. Exact Data** | Raw, immutable facts directly recorded in the system ledger. Timestamps, exact currency sums, account IDs, device hashes. | Core Database Tables | Monospace font, Slate grey tag, zero editorial alteration. |
| **2. Calculated Information** | Mathematical, deterministic computations derived from exact data. Velocity sums, time-deltas, rule scores. | Deterministic Rules Engine | Cyan tag, explicit formula tooltip (`5 txns in 120s = 2.5 tx/min`). |
| **3. Retrieved Evidence** | Contextual records assembled for a specific case. Historical baselines, matched entity links, policy excerpts. | Semantic Retrieval Service | Amber tag, clickable link to underlying raw record. |
| **4. AI Reasoning** | Natural language synthesis, hypothesis generation, correlation analysis, and operational recommendations. | Groq LLM Intelligence | Purple/Violet tag, mandatory citations back to Tiers 1–3 (`[Ref: TX-901]`). |

---

### 5. Evidence Grounding & Anti-Hallucination Guardrails

To ensure that the Groq LLM never produces ungrounded claims:
1. **Citation Engine:** Prompts will require the LLM to tag every assertion with a verified evidence token (e.g. `[Evidence: Rule R-VEL-01]` or `[Evidence: Device DEV-02]`). Uncited factual claims are rejected by the backend.
2. **Strict Schema Constraints:** Copilot outputs are structured via JSON or typed markdown schemas containing discrete sections:
   * `Summary Assessment`
   * `Key Evidence Indicators`
   * `Counter-Evidence & Mitigating Factors`
   * `Evidence Gaps (What is Missing)`
   * `Recommended Next Steps`
3. **Fallback Policy:** If evidence is insufficient, the LLM is instructed to state: *"Insufficient evidence to determine whether this pattern represents fraud; recommend manual customer contact via primary phone."*
