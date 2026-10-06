# Phase 2 Synthetic Data Quality & Validation Report
## Sentient Fraud Intelligence Platform (Rawbank DRC)

**Document Reference:** `docs/phase2-data-quality-report.md`  
**Execution Phase:** Phase 2 — Synthetic Banking Environment  
**Validation Engine:** `scripts/validate_data.py`  
**Database File:** `database/synthetic_bank.db` (SQLite 3)  
**Generation Engine:** `scripts/generate_data.py` (Fixed Seed `42`)  
**Execution Timestamp:** 2026-09-28T15:31:00 UTC  

> [!IMPORTANT]
> **SYNTHETIC DATA COMPLIANCE NOTICE**  
> **All data in this environment is synthetic and created solely for this technical demonstration.**  
> Zero real Rawbank customer records, live account numbers, actual banking transactions, real personal identifying information (PII), or confidential corporate financial details are present in this database.

---

### 1. Executive Summary

Phase 2 has successfully constructed a fully interconnected, relational synthetic banking environment tailored to Rawbank's Congolese operating context. The synthetic dataset achieves the exact target of **2,500 records** distributed across 9 relational tables, with **100% referential integrity** and **15 out of 15 automated validation checks passed** with zero errors or warnings.

---

### 2. Comprehensive Record Counts & Entity Census

| Entity / Table Name | Record Count | Target Budget | Primary Key Prefix | Relational Role & Description |
| :--- | :---: | :---: | :---: | :--- |
| **`customers`** | **120** | 120 | `CUS-XXXXX` | Retail (65%), SME (15%), HNWI (8%), Corporate (4%), Agency Operators (8%) across 6 DRC cities. |
| **`accounts`** | **240** | 240 | `ACC-XXXXX` | Exactly 2 accounts per customer (1 CDF checking/wallet, 1 USD savings/checking). |
| **`devices`** | **150** | 150 | `DEV-XXXXX` | Mobile (Android/iOS) and desktop clients, including 120 primary devices and 30 secondary/fraud devices. |
| **`beneficiaries`** | **180** | 180 | `BEN-XXXXX` | Merchants (30), corporate vendors (20), P2P individuals (127), and designated mule accounts (3). |
| **`behavioural_baselines`** | **120** | 120 | `BASE-XXXXX` | Statistical 60-day moving spending profiles, usual active hours, common channels, and typical volumes. |
| **`auth_activities`** | **450** | 450 | `AUTH-XXXXX` | Session logs: logins (success/fail), OTP requests/verifications, biometric checks, password resets. |
| **`transactions`** | **900** | 900 | `TXN-XXXXX` | Financial movements spanning 30-day temporal window (P2P, merchant QR, ATM cardless, agent POS). |
| **`alerts`** | **140** | 140 | `ALT-XXXXX` | Composite operational triage cases (CRITICAL: 18, HIGH: 32, MEDIUM: 45, LOW: 45). |
| **`fraud_signals`** | **200** | 200 | `SIG-XXXXX` | Deterministic mathematical indicators (Velocity, Device, Impossible Travel, Mule, Structuring, ATO). |
| **TOTAL RECORDS** | **2,500** | **2,500** | — | **Balanced, 100% relational synthetic banking universe.** |

---

### 3. Relational Topology & Graph Linkages

The database strictly implements the domain linkages established in `docs/domain-model.md`:

```
   [120 Customers] ──────┬────── [120 Baselines]
                         │
                         ├────── [240 Accounts] ──────┐
                         │                            │
                         ├────── [150 Devices] ───┐   │
                         │                        │   │
                         └────── [450 Auth Logs]  │   │
                                                  ▼   ▼
        [180 Beneficiaries] ◄────────────── [900 Transactions]
                                                  │
                                                  ▼
                                            [140 Alerts]
                                                  │
                                                  ▼
                                         [200 Fraud Signals]
```

* **Customer-to-Account:** 100% of accounts link to verified customers. Exactly 2 accounts per customer ensure realistic dual-currency operations (CDF and USD).
* **Transaction-to-Entity:** 100% of transactions resolve to an existing account, customer, registered device, and beneficiary.
* **Alert-to-Evidence:** 100% of alerts resolve to a real transaction, customer, account, and one or more deterministic fraud signals.
* **Referential Integrity Audit:** SQLite `PRAGMA foreign_key_check` reported **0 violations**.

---

### 4. Normal vs. Suspicious Activity Breakdown

| Activity Category | Transaction Count | Percentage | Operational Role |
| :--- | :---: | :---: | :--- |
| **Routine Normal Activity** | **750** | **83.3%** | Establishes statistical baseline stability, realistic channel usage, and clean counter-evidence. |
| **Legitimate Anomalies** | **50** | **5.6%** | Tests false positive mitigation (large corporate vendor wires, verified travel, late-night hospital payments). |
| **Suspicious Injected Scenarios** | **100** | **11.1%** | Provides rich forensic evidence for the Command Centre and Copilot. |
| **Total Transactions** | **900** | **100.0%** | Full 30-day operational synthetic environment. |

---

### 5. Suspicious Forensic Scenarios Injected

The dataset incorporates eight distinct, realistic BFSI fraud typologies:

1. **Scenario A (Account Takeover & Drain):**  
   *Target:* Customer `CUS-00014` (SME, Lubumbashi). Unrecognized device `DEV-00127` logs in from Goma; password reset triggered; beneficiary `BEN-00088` added; two consecutive $4,800 USD transfers immediately drain the account.  
   *Signals Triggered:* `R-ATO-05`, `R-DEV-02`, `R-VAL-07`, `R-VEL-01`. Alert `ALT-00001` (CRITICAL, Score: 96).
2. **Scenario B (High Transaction Velocity Burst):**  
   *Target:* Customer `CUS-00022` (SME, Lubumbashi). 5 rapid transfers of 15,000,000 CDF (~$5,454 USD each) to 5 different mobile money wallets within 240 seconds.  
   *Signals Triggered:* `R-VEL-01`, `R-VAL-07`. Alert `ALT-00003` to `ALT-00007` (HIGH, Score: 88).
3. **Scenario C (Shared Device Syndicate Ring):**  
   *Target:* Rooted Android device `DEV-00125` executing outbound transfers across 4 distinct customer accounts (`CUS-00031`, `CUS-00032`, `CUS-00033`, `CUS-00034`) within 48 hours. Totaling $12,800 USD.  
   *Signals Triggered:* `R-DEV-02`, `R-MULE-04`. Alert `ALT-00008` to `ALT-00011` (CRITICAL, Score: 94).
4. **Scenario D (Mule Account Fan-In Aggregator):**  
   *Target:* Beneficiary `BEN-00050` (registered in Goma) receives rapid funnel transfers from 6 different senders across Kinshasa and Lubumbashi, followed by an immediate $18,000 USD agent cash-out.  
   *Signals Triggered:* `R-MULE-04`, `R-VEL-01`. Alert `ALT-00012` to `ALT-00018` (HIGH, Score: 85).
5. **Scenario E (Impossible Geographic Velocity):**  
   *Target:* Customer `CUS-00045`. Point-of-Sale merchant payment in Kinshasa at 14:10 UTC, followed 30 minutes later (14:40 UTC) by a Cardless ATM cash-out in Lubumbashi (1,560 km away). Required travel time is > 180 minutes.  
   *Signals Triggered:* `R-GEO-03`, `R-DEV-02`. Alert `ALT-00020` (CRITICAL, Score: 99).
6. **Scenario F (Brute Force Anomaly to Cardless ATM Cash-Out):**  
   *Target:* Customer `CUS-00055`. 4 consecutive failed PIN attempts followed by sudden web login and instant $4,500 USD cardless ATM withdrawal code generation.  
   *Signals Triggered:* `R-AUTH-08`, `R-ATO-05`. Alert `ALT-00021` (HIGH, Score: 87).
7. **Scenario G (Structuring / Smurfing):**  
   *Target:* Customer `CUS-00062`. 4 sequential transfers of $9,500, $9,650, $9,400, and $9,800 executed 12 minutes apart, designed to evade the BCC $10,000 AML threshold.  
   *Signals Triggered:* `R-SMURF-06`, `R-VEL-01`. Alert `ALT-00022` to `ALT-00025` (HIGH, Score: 84).
8. **Scenario H (Multi-Signal Critical Convergence):**  
   *Target:* Customer `CUS-00078`. Foreign anonymizing VPN IP (`185.220.101.44`) + new unverified device (`DEV-00126`) + off-hours (03:45 AM UTC) + balance drain of $12,500 USD.  
   *Signals Triggered:* `R-DEV-02`, `R-GEO-03`, `R-VAL-07`. Alert `ALT-00026` (CRITICAL, Score: 97).

---

### 6. Legitimate Anomaly Scenarios (False Positive Testing)

* **Legitimate High-Value Corporate Payment:** Large bulk payroll / supplier payment of $68,898 USD by a corporate executive to an established supplier (`BEN-00035`), backed by multi-authorization credentials and matching historical corporate baselines. Alert `ALT-00027` (LOW severity, Score: 28).
* **Legitimate Customer Travel:** Retail customer travelling from Kinshasa to Lubumbashi over a 3-day holiday, transacting small merchant payments on their enrolled personal smartphone.
* **Legitimate Off-Hours Emergency Payment:** $350 USD hospital payment at 02:30 AM to a registered healthcare facility (`Hôpital du Cinquantenaire`).
* **Legitimate Device Upgrade:** Customer enrolling a new phone with prior SMS OTP challenge verification followed by small routine transfer.

---

### 7. Automated Validation Suite Results (15/15 Passed)

The validation script `scripts/validate_data.py` executed 15 exhaustive relational, temporal, and financial integrity checks:

| Check # | Validation Check Name | Status | Observed Result / Verification Evidence |
| :---: | :--- | :---: | :--- |
| **01** | Zero Duplicate Primary Keys | **PASSED** | 100% uniqueness across all 9 tables. Zero primary key collisions. |
| **02** | Zero Missing Required (NULL) Fields | **PASSED** | Zero unexpected null values across all mandatory schema columns. |
| **03** | Strict Foreign Key Referential Integrity | **PASSED** | `PRAGMA foreign_key_check` reported 0 violations across all 2,500 rows. |
| **04** | ISO 8601 Timestamp Validity | **PASSED** | All dates parse cleanly into ISO 8601 UTC timestamps. |
| **05** | Strict Dual-Currency Conformance | **PASSED** | 100% of accounts and transactions denominated strictly in `CDF` or `USD`. |
| **06** | Non-Negative Balances & Positive Amounts | **PASSED** | All balances >= 0.0, all transaction amounts > 0.0. |
| **07** | Customer-Account Relational Linkage | **PASSED** | 100% of accounts resolve to valid existing customers. |
| **08** | Transaction-Beneficiary Relational Linkage | **PASSED** | 100% of transactions resolve to registered beneficiaries. |
| **09** | Transaction-Device Relational Linkage | **PASSED** | 100% of transactions resolve to registered device profiles. |
| **10** | Alerts Entity Cross-Referencing | **PASSED** | All 140 alerts resolve to existing transactions, customers, and accounts. |
| **11** | Fraud Signals Entity Cross-Referencing | **PASSED** | All 200 fraud signals resolve to valid alerts and transactions. |
| **12** | Zero Exact Duplicate Entity Records | **PASSED** | Zero duplicate entity rows detected across directory tables. |
| **13** | Zero Impossible Relationship States | **PASSED** | Account ownership verified; device `first_seen` <= `last_seen`. |
| **14** | Data Distribution Sanity & Budget | **PASSED** | Exactly 2,500 records generated (within target 2,400–2,600). |
| **15** | 100% Synthetic Compliance & Zero PII | **PASSED** | All IDs use synthetic prefixes (`CUS-`, `ACC-`, `TXN-`); zero live PII. |

---

### 8. Project Assumptions & Known Limitations

1. **[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]:** The rule codes (`R-VEL-01`, `R-ATO-05`, `R-GEO-03`, `R-MULE-04`, `R-SMURF-06`, `R-VAL-07`, `R-AUTH-08`, `R-BEH-09`) and threshold constants were formulated as project assumptions based on standard BFSI fraud typologies. If `SentientData_RuleSet.md` is provided in future phases, the rule names and codes will be synchronized.
2. **[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]:** A fixed exchange rate of `1 USD = 2,750 CDF` was adopted to standardize `amount_usd_equivalent` calculations across multi-currency transactions.
3. **Temporal Bounds:** Synthetic transactions are bounded within a 30-day temporal window (September 2026).
4. **Known Limitation:** The SQLite database is local (`database/synthetic_bank.db`). It does not require cloud infrastructure or network services, guaranteeing offline reproducibility and instant query execution.
