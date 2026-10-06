# Phase 7 — Sentient Fraud Intelligence Platform: End-to-End Analyst Journey

## Overview
This document details the unified operational workflow for Rawbank fraud analysts operating the **Sentient Fraud Intelligence Platform**. The platform integrates two connected use cases required by the *iTech Pre-Sales Technical Build Assignment*:

1. **USE CASE 1: Sentient Command Centre** (Monitor → Prioritise → Analyse → Drill Down)
2. **USE CASE 2: Sentient Fraud Investigation Copilot** (Investigate → Correlate → Explain → Recommend → Escalate)

---

## The 9-Stage Analyst Investigation Journey

```
┌────────────────────────────────────────────────────────────────────────┐
│                      USE CASE 1: COMMAND CENTRE                        │
│                                                                        │
│   [ 1. MONITOR ] ──> [ 2. PRIORITISE ] ──> [ 3. ANALYSE ] ──> [ 4. DRILL DOWN ]
│   (KPI Top Bar)     (Triage Stream)      (Risk Breakdown)   (Entity Drawer)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ "Investigate with Copilot"
┌───────────────────────────────────▼────────────────────────────────────┐
│                  USE CASE 2: INVESTIGATION COPILOT                     │
│                                                                        │
│   [ 5. INVESTIGATE ] ──> [ 6. CORRELATE ] ──> [ 7. EXPLAIN ]            │
│   (Contextual Prompt)   (Graph & Evidence)  (Multi-Section Dossier)    │
│                                                       │                │
│                                                       ▼                │
│                        [ 9. ESCALATE ] <─── [ 8. RECOMMEND ]          │
│                       (Disposition Action)  (Actionable Checklist)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

### Stage 1: Monitor
**Analyst Goal:** Maintain continuous real-time situational awareness across Rawbank's synthetic DRC banking environment.
- **Console Screen:** Command Centre (`/`)
- **Key Indicators:**
  - Active Total Alerts (e.g., 142 total alerts in synthetic pipeline)
  - Critical Severity Count (e.g., 28 critical alerts requiring immediate triage)
  - Active Fraud Signals (e.g., 320 deterministic rule violations)
  - Dual-Timezone Operation: System clocks displaying Kinshasa (WAT, UTC+1) and Lubumbashi (CAT, UTC+2) to monitor local banking hours.
- **Analyst Action:** Observe critical alert count and scenario distribution bars to identify active fraud waves (e.g., a burst of ATO attacks in Lubumbashi).

---

### Stage 2: Prioritise
**Analyst Goal:** Isolate high-impact threats requiring immediate triage over routine false positives.
- **Console Screen:** Immediate Operational Triage Table / Alerts Workspace (`/alerts`)
- **Action Sequence:**
  1. The analyst reviews the top triage queue sorted by **Composite Risk Score** (descending).
  2. The analyst spots `ALT-00001`:
     - **Severity:** `CRITICAL` (bold red badge).
     - **Deterministic Risk Score:** `96 / 100`.
     - **Scenario:** `ATO_DRAIN` (Account Takeover followed by maximum liquidation).
     - **Customer:** `CUS-00014` (`Christelle Mutombo`).
     - **Transaction:** `TXN-00801` (`$4,800.00 USD`).
- **Decision:** Select `ALT-00001` for detailed forensic examination.

---

### Stage 3: Analyse
**Analyst Goal:** Understand the specific rule firings, indicators, and timeline triggering the alert.
- **Console Screen:** Alert Row in Triage Workspace
- **Evidence Review:**
  - Rule `R-ATO-05`: Credential password reset occurred 15 minutes prior to transfer.
  - Rule `R-DEV-02`: Transaction originated on unverified novel hardware `DEV-00127`.
  - Rule `R-VAL-07`: Transfer amount ($4,800 USD) is 18x customer's median baseline ($260 USD).
  - Rule `R-VEL-01`: Rapid consecutive transfer attempt following authorization.

---

### Stage 4: Drill Down
**Analyst Goal:** Seamlessly inspect connected entities without losing investigation context.
- **Console Screen:** Universal Slide-Over `EntityDrawer`
- **Action Sequence:**
  1. Clicking `ALT-00001` slides open the `EntityDrawer` from the right edge.
  2. **Core Attributes Tab:** Verifies account ID `ACC-00028`, execution timestamp `2026-09-16T03:25:00`, and transfer channel `IllicoCash_App`.
  3. **Evidence Packet Tab:** Displays the 4-tier structured evidence dossier:
     - *Exact Data:* Transaction $4,800 USD via IllicoCash.
     - *Calculated:* Velocity spike of 18x median daily turnover.
     - *Retrieved:* First login on device `DEV-00127` at 03:10 AM from Goma.
     - *Counter-Evidence:* Customer has KYC Tier 2 verification and 3 years clean tenure.
     - *Evidence Gaps:* Missing cell-tower geolocation coordinates.
  4. **Relationship Network Tab:** Expands 1-hop and 2-hop graph showing `CUS-00014` connected to `DEV-00127` and beneficiary `BEN-00088`.
  5. The analyst clicks the clickable `[Source: CUS-00014]` pill to inspect the customer's full profile without navigating away.

---

### Stage 5: Investigate
**Analyst Goal:** Formulate an evidence-grounded investigation inquiry in the Sentient Fraud Copilot.
- **Console Screen:** Sentient Fraud Investigation Copilot (`/copilot`)
- **Action Sequence:**
  1. The analyst clicks the gold `Investigate with Copilot` button on `ALT-00001`.
  2. The application pre-populates the prompt:
     > *"Why was alert ALT-00001 triggered?"*
  3. The analyst submits the query to `POST /api/copilot/investigate`.

---

### Stage 6: Correlate
**Analyst Goal:** Synthesize multi-source telemetry across transactions, authentication logs, and device fingerprints.
- **System Action:**
  - The Copilot retrieval engine queries the synthetic bank database for `ALT-00001`.
  - Resolves target entities: Customer `CUS-00014`, Transaction `TXN-00801`, Device `DEV-00127`, Beneficiary `BEN-00088`.
  - Correlates authentication events, discovering a password reset request immediately preceding the high-value transfer.
  - Links beneficiary `BEN-00088` (`Tshimanga Quick Cash`) to 9 other distinct senders, identifying a coordinated cash-out mule funnel.

---

### Stage 7: Explain
**Analyst Goal:** Review a structured, audit-ready narrative that clearly separates facts from speculation.
- **Console Screen:** Copilot Forensic Investigation Dossier
- **Rendered Sections:**
  - **Executive Summary:** Explains that `ALT-00001` represents an account takeover wherein credentials were reset from an unverified Android device in Goma, followed by a maximum-balance drain to an external mobile money wallet.
  - **Risk Assessment:** Confirms official deterministic risk score of `96/100` (`CRITICAL`) with `0.95` evidence confidence.
  - **Supporting Evidence:**
    - Transfer of $4,800 USD exceeds 90-day moving average `[Source: TXN-00801]`.
    - Password reset occurred 15 minutes prior on newly enrolled device `[Source: AUTH-00389]`.
    - Hardware signature `DEV-00127` has never been observed for customer `[Source: DEV-00127]`.
  - **Counter-Evidence (Mitigating Factors):** Customer `CUS-00014` holds valid Tier 2 KYC status and has zero prior fraud incidents on record.
  - **Evidence Gaps:** Cell tower coordinates unavailable; IP geolocation indicates Goma, while customer's registered branch is Lubumbashi.

---

### Stage 8: Recommend
**Analyst Goal:** Review actionable operational guidance grounded in Rawbank risk policy.
- **Console Screen:** Copilot Recommended Operational Disposition
- **Recommended Action Checklist:**
  1. Place an immediate debit hold on account `ACC-00028` to prevent secondary drain attempts.
  2. Suspend mobile banking session for device `DEV-00127`.
  3. Initiate out-of-band verification by calling customer `Christelle Mutombo` on registered phone `+243-85-880-3646`.
  4. Flag destination beneficiary `BEN-00088` (`Tshimanga Quick Cash`) as a high-risk aggregator mule across all channels.

---

### Stage 9: Escalate
**Analyst Goal:** Execute the final disposition and preserve complete provenance for compliance auditing.
- **Action Sequence:**
  1. The analyst conducts a follow-up inquiry in the same conversational session (`sess_1790611464802`):
     > *"What happened right before the transfer?"*
  2. The Copilot maintains session context and details the password reset request initiated at 03:10 AM from IP `197.157.210.45` in Goma.
  3. The analyst clicks the primary action button to confirm disposition:
     - **Status:** Escalated to Senior Fraud Operations & SAR Review.
     - **Audit Trail:** Complete 4-tier evidence packet and citation records stored with immutable provenance.

---

## Edge Case Handling in Daily Workflow

| Scenario | Tested Entity | Analyst Experience |
| :--- | :--- | :--- |
| **Ambiguous Customer Name** | Search: `"Jean Mutombo"` | The global search and Copilot detect multiple matches (`CUS-00035` in Lubumbashi vs. `CUS-00041` in Bukavu). Copilot renders an **Amber Ambiguity Banner** prompting the analyst to clarify which account is under review before proceeding. |
| **Unknown Entity Inquiry** | Search: `"CUS-99999"` | The platform returns a clean 404 alert and Copilot renders a **Red Unknown Entity Banner** explicitly confirming zero database records exist, preventing hallucinated customer histories. |
| **Clean Customer Baseline** | Search: `"CUS-00003"` | When investigating a non-fraudulent customer, Copilot accurately reports normal behavioral patterns, zero active alerts, and prominent **Counter-Evidence** highlighting why no escalation is warranted. |
