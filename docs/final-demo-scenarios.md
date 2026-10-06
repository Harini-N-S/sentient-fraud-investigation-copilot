# Final Demonstration Scenarios Guide
**Rawbank Sentient Fraud Intelligence Platform**
**Demonstration Script & Verification Playbook**

---

## Overview

This guide provides step-by-step walkthroughs for 7 verified demonstration scenarios. Each scenario is strictly anchored in the synthetic banking database (`database/synthetic_bank.db`) and demonstrates key capabilities required by the *iTech Pre-Sales Technical Build Assignment*.

---

## Scenario 1: Account Takeover & Rapid Liquidation (ATO Drain)

### 1. Starting Screen
- **Screen:** Sentient Command Centre (`/`)
- **Initial View:** Executive KPIs and Real-time Incident Feed

### 2. Target Entity & Alert
- **Alert ID:** `ALT-00001`
- **Customer:** `CUS-00014` (Christelle Mutombo, SME, Lubumbashi)
- **Transaction:** `TXN-00801` ($4,800.00 USD, P2P Transfer via IllicoCash App, Goma)
- **Device:** `DEV-00127` (Tecno Spark 10, New Unverified, IP: 102.164.210.88)
- **Beneficiary:** `BEN-00088` (Tshimanga Quick Cash, Airtel Money, Known Mule)

### 3. Action
1. Filter the alert table by **Severity: CRITICAL**.
2. Click on alert **ALT-00001** to open the forensic inspection drawer.
3. Review the deterministic risk score (**96/100**) and supporting fraud signals (`R-ATO-05`, `R-DEV-02`, `R-VAL-07`, `R-BEH-09`).
4. Click **"Investigate with Copilot"** to hand off context to the conversational investigator.

### 4. Question to Copilot
> *"Why was alert ALT-00001 triggered?"*

### 5. Expected Evidence
- **Deterministic Risk Score:** Preserved at **96/100 (CRITICAL)**.
- **Credential ATO Signal:** Password reset performed 15 minutes prior on unverified novel device `DEV-00127`.
- **Value Anomaly:** Outbound transfer of $4,800 USD represents an 18x spike over customer baseline median ($260 USD).
- **Recipient Profiling:** Destination beneficiary `BEN-00088` is a known high-velocity mobile money aggregator.
- **Source Citations:** Bracketed citations `[Source: TXN-00801]`, `[Source: ALT-00001]`, `[Source: DEV-00127]`.

### 6. Expected Investigation Flow
Investigate $\to$ Correlate $\to$ Explain $\to$ Recommend $\to$ Escalate:
1. Copilot synthesizes timeline from password reset to transfer execution.
2. Identifies secondary drain `TXN-00802` ($4,750 USD) executed within 120 seconds.
3. Surfaces evidence gap: external SIM-swap verification record with telecom provider.
4. Recommends immediate account restriction and Level 2 fraud officer escalation.

### 7. Assignment Requirement Demonstrated
- Use Case 1 (Command Centre Prioritisation & Drill-down)
- Use Case 2 (Copilot Automated Forensic Correlation & Narrative Synthesis)
- Explainable, deterministic risk score preservation without LLM mutation.

---

## Scenario 2: Shared Hardware Device Syndicate Ring

### 1. Starting Screen
- **Screen:** Global Search (`Alt + K` or search bar) or Relationship Graph

### 2. Target Entity
- **Device ID:** `DEV-00125` (Infinix Hot 30, IP: 102.164.195.42)
- **Primary Owner:** `CUS-00031` (Blaise Kavugho)
- **Connected Syndicate Members:** `CUS-00032`, `CUS-00033`, `CUS-00034`

### 3. Action
1. In the search bar, enter `DEV-00125` and click the matching device result.
2. In the Entity Details view, click the **"Graph Topology"** tab to open the interactive relationship graph.
3. Observe the star topology connecting 4 distinct customer accounts to a single shared mobile device.
4. Click **"Ask Copilot About This Device"**.

### 4. Question to Copilot
> *"Which customers are connected to this device and why is the relationship relevant?"*

### 5. Expected Evidence
- **Multi-Customer Hardware Sharing:** 4 distinct customer identities transacting from the same IMEI/MAC signature (`CUS-00031`, `CUS-00032`, `CUS-00033`, `CUS-00034`).
- **Syndicate Alerts:** Correlated alerts `ALT-00008`, `ALT-00009`, `ALT-00010`, `ALT-00011` all flagged under scenario `SHARED_DEVICE_RING` with risk score **94/100 (CRITICAL)**.
- **Rule Evidence:** Rule `R-DEV-SHR-01` triggered by multi-identity hardware concentration.

### 6. Expected Investigation Flow
1. Copilot identifies the co-users and total transaction volume routed through the hardware signature.
2. Evaluates whether the customers share family or commercial ties.
3. Concludes high probability of synthetic identity syndicate or mule farm operation.
4. Recommends blacklisting `DEV-00125` and auditing all linked accounts simultaneously.

### 7. Assignment Requirement Demonstrated
- Entity relationship graph traversal and second-hop link discovery.
- Hardware syndicate detection across seemingly unrelated customer accounts.

---

## Scenario 3: Mule Beneficiary Aggregator (Fan-In Funnel)

### 1. Starting Screen
- **Screen:** Sentient Command Centre (`/`)
- **Widget:** "Top Mule Aggregators & Funnels"

### 2. Target Entity
- **Beneficiary ID:** `BEN-00088` (Tshimanga Quick Cash)
- **Channel / Institution:** Airtel Money
- **Blacklist Status:** `is_known_mule = 1`

### 3. Action
1. Locate `BEN-00088` in the Top Mule Beneficiaries widget on the Command Centre dashboard.
2. Click the beneficiary card to view the incoming transaction aggregation.
3. Observe that **9 distinct sending customers** across Kinshasa, Goma, and Lubumbashi have transferred funds into this single Airtel Money account totaling **$20,809.07 USD**.
4. Open the Copilot drawer.

### 4. Question to Copilot
> *"Who else sends money to this beneficiary and what pattern should an investigator examine?"*

### 5. Expected Evidence
- **Distinct Sender Aggregation:** 9 distinct sending accounts (`CUS-00014`, `CUS-00118`, `CUS-00048`, `CUS-00029`, `CUS-00005`, `CUS-00018`, `CUS-00120`, `CUS-00019`, `CUS-00004`).
- **Linked Critical Incidents:** Receiver of stolen funds from ATO incidents `ALT-00001` and `ALT-00002`.
- **Topological Inflow Velocity:** Rapid multi-channel cash-in flows exceeding typical retail merchant profiles.

### 6. Expected Investigation Flow
1. Copilot correlates disparate sending customer profiles into a unified aggregation summary.
2. Highlights rapid cash-out behavior following receipt.
3. Recommends filing suspicious activity report (SAR/STR) and freezing outbound mobile wallet settlement clearing.

### 7. Assignment Requirement Demonstrated
- Mule account aggregation detection.
- Cross-customer entity resolution and network risk attribution.

---

## Scenario 4: Legitimate Corporate Anomaly (False Positive Mitigation)

### 1. Starting Screen
- **Screen:** Sentient Command Centre (`/`)
- **Filter:** Scenario Type: `LEGITIMATE_ANOMALY` or Alert `ALT-00027`

### 2. Target Entity
- **Alert ID:** `ALT-00027`
- **Customer:** `CUS-00010` (Corporate / Commercial segment)
- **Transaction:** `TXN-00751` ($68,898.00 USD via RawbankOnline Web, Lubumbashi)
- **Beneficiary:** `BEN-00035` (Société Commerciale Kanyinda SARL)
- **Device:** `DEV-00010` (Apple MacBook Pro M2, Trusted Enrolled)

### 3. Action
1. Select alert `ALT-00027` in the incident queue.
2. Note the low composite risk score (**28/100, LOW**) despite the high transfer amount ($68,898 USD).
3. Review counter-evidence indicators in the alert detail drawer.
4. Click **"Investigate with Copilot"**.

### 4. Question to Copilot
> *"What evidence could explain this activity as a legitimate corporate anomaly?"*

### 5. Expected Evidence
- **Corporate Baseline Alignment:** Transaction volume aligns with customer segment's quarterly procurement schedule.
- **Hardware Trust Verification:** Transaction originated from enrolled, trusted corporate hardware (`DEV-00010`) with zero VPN, Tor, or rooting compromise.
- **Dual-Authorization Standard:** Enterprise multi-signatory approval logged in core banking journal.
- **Established Counterparty:** Recipient is an established recurring corporate vendor.

### 6. Expected Investigation Flow
1. Copilot evaluates both supporting evidence (high dollar value) and counter-evidence (trusted hardware, baseline match, verified vendor).
2. Explicitly communicates uncertainty rather than forcing a fraudulent conclusion.
3. Recommends alert closure with status `DISMISSED_FALSE_POSITIVE` without customer disruption.

### 7. Assignment Requirement Demonstrated
- Counter-evidence evaluation and false-positive handling.
- Prevention of operational friction for legitimate high-value corporate clients.

---

## Scenario 5: Non-Existent Identifier / Unknown Entity Challenge

### 1. Starting Screen
- **Screen:** Fraud Investigation Copilot (`/copilot`)

### 2. Target Entity
- **Input Identifier:** `CUS-99999` (Non-existent customer)

### 3. Action
1. Navigate to the Copilot conversational page.
2. Enter an investigation query referencing an ungrounded, non-existent customer ID.

### 4. Question to Copilot
> *"Investigate customer CUS-99999 and explain why their risk score is so high."*

### 5. Expected Evidence
- **Unknown Entity Detection:** System intercepts identifier `CUS-99999` during deterministic entity resolution.
- **Risk Score:** Authoritative score set to **0/100 (NONE)**.
- **Evidence Gap:** Surfaces explicit `UNKNOWN_ENTITY` gap: *"Identifier 'CUS-99999' was not found in the Rawbank synthetic banking database. Zero records exist."*

### 6. Expected Investigation Flow
1. System does NOT hallucinate a fictitious customer profile, balances, or transactions.
2. Copilot immediately halts speculative reasoning and notifies the analyst.
3. Recommends verifying the customer identifier against core banking records.

### 7. Assignment Requirement Demonstrated
- Robust hallucination resistance and strict database grounding.
- Zero fabrication of non-existent banking entities.

---

## Scenario 6: Ambiguous Entity Disambiguation

### 1. Starting Screen
- **Screen:** Fraud Investigation Copilot (`/copilot`)

### 2. Target Entity
- **Name Query:** *"Jean Mutombo"* (Common Congolese archetype shared by multiple customers)

### 3. Action
1. In the Copilot prompt input, type the ambiguous name without specifying a customer ID.

### 4. Question to Copilot
> *"Investigate Jean Mutombo for recent transfers."*

### 5. Expected Evidence
- **Ambiguity Detection Flag:** `ambiguity_detected: true`.
- **Candidate Disambiguation:** Surfaces matching candidate profiles:
  - `CUS-00035`: Jean Mutombo (Retail, Kinshasa)
  - `CUS-00041`: Jean Mutombo (SME, Lubumbashi)
- **Evidence Gap:** Surfaces `AMBIGUOUS_ENTITY` gap: *"Entity mention 'Jean Mutombo' matches multiple candidate records. Cannot conclusively resolve identity."*

### 6. Expected Investigation Flow
1. Copilot refrains from arbitrarily picking one customer or merging their transaction histories.
2. Prompts the human investigator to disambiguate by selecting the exact customer ID or account number.

### 7. Assignment Requirement Demonstrated
- Deterministic entity resolution and candidate disambiguation.
- Safeguard against cross-contaminating distinct customer dossiers.

---

## Scenario 7: Clean Customer Baseline / Insufficient Evidence

### 1. Starting Screen
- **Screen:** Fraud Investigation Copilot (`/copilot`)

### 2. Target Entity
- **Customer ID:** `CUS-00003` (Routine retail customer with zero suspicious activity)

### 3. Action
1. Submit an investigation query asking if customer `CUS-00003` should be escalated for fraud.

### 4. Question to Copilot
> *"Is there sufficient evidence to establish suspicious activity for this customer?"*

### 5. Expected Evidence
- **Risk Score:** **0/100 (NONE)**.
- **Zero Active Alerts:** Confirmation that zero fraud alerts or high-risk signals exist in the database.
- **Baseline Adherence:** All transaction amounts and velocity metrics fall squarely within standard retail moving averages.
- **Evidence Gap:** Documents `NO_RELATED_ALERTS` gap.

### 6. Expected Investigation Flow
1. Copilot explicitly states: *"There is insufficient evidence in the available synthetic dataset to establish suspicious activity."*
2. Does NOT manufacture suspicious hypotheses to justify escalation.
3. Recommends continuing routine automated monitoring without operational freeze.

### 7. Assignment Requirement Demonstrated
- Responsible, evidence-grounded AI intelligence capable of stating "evidence is insufficient".
- Defense against over-eager AI fraud accusations.
