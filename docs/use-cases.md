# Two Connected Experiences Specification: Use Cases 01 & 02
## Sentient Fraud Intelligence Platform (aXtrLabs)

**Target Bank:** Rawbank (DRC)  
**Phase:** Phase 1 — Project Foundation & Functional Use Case Specification  
**Architecture Context:** Unified Banking Environment & Shared State

---

### Executive Architecture Overview: The Symbiotic Pair

The Sentient Fraud Intelligence Platform delivers its analytical power through two interconnected, synchronized operational experiences:
1. **Use Case 01: Sentient Command Centre** — The macro operational radar screen: *Monitor → Prioritise → Analyse → Drill Down*.
2. **Use Case 02: Sentient Fraud Investigation Copilot** — The micro forensic analyst workstation: *Investigate → Correlate → Explain → Recommend → Escalate*.

```
   ┌─────────────────────────────────────────────────────────────┐
   │             USE CASE 01: SENTIENT COMMAND CENTRE            │
   │   [ Fleet Monitor ] ➔ [ Prioritise ] ➔ [ Rapid Analyse ]    │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                       Drill-Down / Pivot Context
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │        USE CASE 02: SENTIENT FRAUD INVESTIGATION COPILOT    │
   │  [ Investigate ] ➔ [ Correlate ] ➔ [ Explain & Recommend ]   │
   └─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                     SHARED SYNTHETIC ENVIRONMENT
        (Customers, Accounts, Transactions, Deterministic Rules)
```

---

### USE CASE 01: Sentient Command Centre

#### 1. Purpose & User Persona
* **Primary Persona:** Tier-1 Fraud Operations Triage Analyst / Risk Operations Supervisor at Rawbank.
* **Objective:** Provide a real-time, bird’s-eye surveillance cockpit over all incoming synthetic transactions, immediate rule triggers, and fleet-wide risk anomalies across Rawbank channels (IllicoCash, ATMs, Agency Express, SWIFT).
* **Operational Goal:** Enable an analyst to identify, prioritize, and initiate triage on critical threats in less than 30 seconds.

#### 2. The Operational Flow

##### Step 1: Monitor (Fleet-Wide Situational Awareness)
* **What the Analyst Sees:**
  * Real-time stream of synthetic transactions and generated alerts.
  * Live KPI status bar:
    * Total Transactions Evaluated (e.g. 2,500 baseline)
    * Active High/Critical Alerts requiring immediate action
    * Currency Breakdown (CDF vs. USD volume)
    * High-Risk Channel Distribution (IllicoCash mobile vs. Cardless ATM vs. Agency POS)
* **Operational Value:** Instant comprehension of systemic health without digging through raw logs.

##### Step 2: Prioritise (Intelligent Risk Triage)
* **What the Analyst Does:**
  * Uses the Priority Ribbon to filter the stream into actionable severity queues:
    * `Tier 1: Critical (Immediate Drain / ATO in progress)`
    * `Tier 2: High (Suspicious Mule Fan-Out / Velocity Breach)`
    * `Tier 3: Medium (Unusual Currency Exchange / Foreign IP)`
    * `Tier 4: Low / Informational (First-time device with normal biometric check)`
  * Sorts by Composite Risk Score (0–100) or Time-to-SLA breach.
* **Operational Value:** Eliminates cognitive fatigue by ensuring that severe account drains are triaged before lower-severity anomalies.

##### Step 3: Analyse (Rapid Entity & Anomaly Inspection)
* **What the Analyst Does:**
  * Selects an alert from the prioritised queue.
  * The central view displays an aggregated summary card:
    * Customer Summary (KYC Tier, Tenure, Primary City)
    * Transaction Details (CDF/USD amount, Channel, Counterparty)
    * Triggered Deterministic Rules (e.g., `Rule R-VEL-01: Rapid succession of 4 transfers > $1,000`)
    * 24-Hour Velocity Delta (e.g., 850% above historical 30-day baseline)
* **Operational Value:** Delivers complete situational context in a single visual pane without modal hopping.

##### Step 4: Drill Down (Seamless Handoff to Investigation)
* **What the Analyst Does:**
  * Clicks the **"Initiate Deep Investigation"** action or presses hotkey `I`.
  * The Command Centre seamlessly loads the full forensic dossier into the contextual panel:
    * Full 30-Day Customer Transaction Timeline.
    * Linked Device & Authentication History.
    * Beneficiary Graph Connections (detecting shared mule accounts).
  * Automatically seeds the **Sentient Fraud Investigation Copilot** with the active case dossier.

---

### USE CASE 02: Sentient Fraud Investigation Copilot

#### 1. Purpose & User Persona
* **Primary Persona:** Senior Fraud Forensic Investigator / AML Compliance Officer.
* **Objective:** Assist the investigator in reasoning through complex, multi-hop synthetic fraud scenarios by synthesizing evidence, identifying counter-evidence, detecting behavioral deviations, highlighting data gaps, and recommending regulatory escalations.
* **Anti-Chatbot Mandate:** The Copilot is **NOT** a generic chatbot answering general knowledge questions. It is a specialized, contextually bound forensic copilot operating directly on the active entity selected in the Command Centre.

#### 2. Core Capabilities & Reasoning Requirements

##### A. Reasoning About Why Activity is Suspicious
* Synthesizes multiple disparate signals into an intelligible fraud hypothesis (e.g., *"This activity exhibits classic Account Takeover (ATO) behavior: a password reset occurred from an unrecognized device in Goma, followed 4 minutes later by two maximum-limit transfers to newly added mobile wallets."*).

##### B. Supporting Evidence Synthesis
* Cites exact verifiable records from the synthetic database:
  * Transaction IDs (`TX-90412`, `TX-90415`)
  * Device Hardware Hashes & IP Geolocation mismatches (`DEV-A9842` in Goma vs. customer’s historical device `DEV-0012` in Kinshasa)
  * Rule engine execution outputs (`Rule R-VEL-01: Breached`, `Rule R-GEO-02: Impossible Travel`).

##### C. Counter-Evidence & Mitigating Factors
* Crucially, the Copilot must never suffer from confirmation bias. It must actively search for and present evidence that **contradicts** fraud:
  * *Counter-Evidence Example:* *"The customer successfully verified a biometric facial scan on their enrolled iPhone 6 minutes prior to the transaction."*
  * *Counter-Evidence Example:* *"While the transfer amount ($4,500) is large, it matches an identical quarterly vendor disbursement made to the same beneficiary over the past 18 months."*

##### D. Behavioural Deviation Analysis
* Contrasts the incident against the customer’s `BehaviouralBaseline`:
  * Typical transaction size vs. current spike (e.g. 14x normal median).
  * Unusual hour of execution (e.g., 03:22 AM UTC vs. normal active window of 07:00–18:00 UTC).
  * Novelty of channel (first time using web portal instead of IllicoCash mobile app).

##### E. Related Activity & Entity Graph Correlation
* Traverses the relational graph to uncover broader coordinated attacks:
  * Identifies if the recipient beneficiary account has received funds from 5 other Rawbank accounts in the past 2 hours (mule ring).
  * Identifies if the initiating device ID has been logged across any other customer profiles.

##### F. Evidence Gaps Identification
* Highlights what data is missing from the case file before a definitive conclusion can be reached:
  * *"Evidence Gap: Carrier SIM-swap telemetry is currently unconfirmed for phone number +243-81-XXX-XXXX."*
  * *"Evidence Gap: IP address geolocation is masked by a known commercial VPN node."*

##### G. Potential False Positive Evaluation
* Evaluates the operational risk of taking adverse action against a genuine customer:
  * Computes the probability of legitimate customer behavior (e.g., travel during holiday season, emergency medical payment).
  * Helps the analyst avoid unnecessary account freezes that disrupt loyal clients.

##### H. Prescriptive Analyst Recommendations
* Generates tiered, actionable next steps:
  1. **Immediate Defensive Action:** *"Temporarily place a debit hold on Account ACC-RAW-0092144."*
  2. **Customer Outreach Action:** *"Contact the customer via secondary verified phone channel to confirm recent login."*
  3. **Regulatory Action:** *"Flag beneficiary wallet Vodacom-MPESA-9912 for AML Suspicious Activity Report (SAR) filing under BCC circular 004."*

---

### Symbiotic Interaction Contract: Command Centre ↔ Copilot

| Interaction Event | Command Centre Action | Copilot Response |
| :--- | :--- | :--- |
| **Row Select in Triage Queue** | Central viewport highlights alert; loads quick metadata. | Copilot silently receives entity context, runs background pre-retrieval, and prepares executive summary. |
| **"Investigate with Copilot" Click** | Command Centre splits viewport to expose Copilot panel; pins entity header. | Copilot opens with pre-populated case summary, key evidence cards, and recommended prompt pills. |
| **Analyst Prompt in Copilot** | Remains in view; highlights relevant UI elements (e.g. highlighting a timeline node if cited). | Groq LLM streams response with evidence citations; generates interactive action buttons. |
| **Analyst Executes Action in Copilot** | Command Centre immediately updates alert status badge (`ESCALATED_AML`), removing item from active queue. | Copilot records action into the immutable audit trail log. |
