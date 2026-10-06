# Phase 2 Synthetic Data Assumptions & Modelling Specification
## Sentient Fraud Intelligence Platform (Rawbank DRC)

**Document Reference:** `docs/phase2-data-assumptions.md`  
**Phase:** Phase 2 — Synthetic Banking Environment  
**Execution Context:** Greenfield Synthetic Generation  
**Resource Pack Availability:** Authoritative assignment resource pack (`BuildStack.png`, `SentientData_RuleSet.md`, `SyntheticData_Fuel`, `UsecaseONE_stuff.txt`, `UsecaseTWO_stuff.txt`, `Working Sheet`, `Clue Deck`) is **NOT AVAILABLE**.

> [!CAUTION]
> **SYNTHETIC DATA & MODELLING DISCLAIMER**  
> All banking structures, customer names, accounts, transactions, device signatures, and fraud patterns defined in this document are **100% synthetic** and constructed solely for technical evaluation and system demonstration. Under no circumstances should any record, distribution, or pattern be construed as actual internal data, customers, or vulnerabilities of Rawbank SA.

---

### 1. Master Classification of Assumptions

Because the official resource pack is missing locally, all design choices, schemas, and rule thresholds are explicitly designated as:

`[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`

If the authoritative resource pack is supplied at a later stage, these assumptions will be reconciled against the official parameters.

---

### 2. Entity & Relational Assumptions

#### 2.1 Entity Set & Scope [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
The synthetic environment is modelled around nine relational entities:
1. `customers` (Demographic, KYC segment, geographic home)
2. `accounts` (CDF and USD ledgers linked to customers)
3. `devices` (Hardware fingerprints, OS, IP geolocation)
4. `beneficiaries` (Internal and external recipient counterparties)
5. `behavioural_baselines` (Statistical spending profiles per customer)
6. `auth_activities` (Logins, failed attempts, OTP validations, device enrollments)
7. `transactions` (Atomic payment and transfer events)
8. `fraud_signals` (Discrete deterministic rule breach markers)
9. `alerts` (Composite operational risk cases linking transactions to signals)

#### 2.2 Relational Integrity Model [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]
* Every `account` belongs to an existing `customer`.
* Every `transaction` originates from an existing `account`, references an existing `customer`, and links to a valid `beneficiary` and `device`.
* Every `device` is associated with at least one `customer` (or shared among syndicate customers).
* Every `auth_activity` references a valid `customer` and `device`.
* Every `alert` references an existing `transaction`, `customer`, and `account`.
* Every `fraud_signal` is tied to an `alert` and `transaction`.
* Every `customer` has a corresponding `behavioural_baseline`.
* **Zero dangling foreign keys:** Referential integrity is strictly enforced at database level with foreign key constraints.

---

### 3. Identifier Format Standards [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

Stable, zero-collision synthetic IDs with deterministic prefixes are standardized as follows:

| Entity | Identifier Format | Example Value | Description |
| :--- | :--- | :--- | :--- |
| Customer | `CUS-XXXXX` | `CUS-00104` | 5-digit zero-padded synthetic customer code |
| Account | `ACC-XXXXX` | `ACC-00215` | 5-digit zero-padded synthetic account ledger code |
| Transaction | `TXN-XXXXX` | `TXN-00892` | 5-digit zero-padded synthetic transaction reference |
| Beneficiary | `BEN-XXXXX` | `BEN-00045` | 5-digit zero-padded counterparty code |
| Device | `DEV-XXXXX` | `DEV-00078` | 5-digit zero-padded hardware client profile code |
| Auth Activity | `AUTH-XXXXX` | `AUTH-00312` | 5-digit zero-padded security event log code |
| Alert | `ALT-XXXXX` | `ALT-00067` | 5-digit zero-padded operational case file code |
| Fraud Signal | `SIG-XXXXX` | `SIG-00142` | 5-digit zero-padded deterministic rule signal code |
| Baseline | `BASE-XXXXX` | `BASE-00104` | 5-digit zero-padded baseline linked to `CUS-XXXXX` |

No IDs are reused across entities.

---

### 4. Synthetic Record Budget (~2,500 Records Target) [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

To satisfy the assignment's mandate of approximately 2,400–2,600 total records (target: ~2,500) while maximizing relational depth, the dataset is distributed across the nine connected entities as follows:

| Entity Table | Target Count | Relational Role |
| :--- | :---: | :--- |
| `customers` | 120 | Seed customer directory across retail, SME, corporate, and agent segments. |
| `accounts` | 240 | Exactly 2 accounts per customer (1 CDF current, 1 USD savings/wallet). |
| `devices` | 150 | Client hardware fleet (includes normal 1:1, multi-device, and shared fraud devices). |
| `beneficiaries` | 180 | Recipient directory (trusted payees, merchants, telco wallets, and shared mules). |
| `behavioural_baselines` | 120 | Pre-calculated 60-day baseline profiles (1 per customer). |
| `auth_activities` | 450 | Session security audit trail (logins, OTPs, password changes, failed logins). |
| `transactions` | 900 | Financial movement events over a 30-day temporal window. |
| `fraud_signals` | 200 | Deterministic rule breaches generated by suspicious/anomalous transactions. |
| `alerts` | 140 | Composite operational triage cases synthesized from fraud signals. |
| **Total Database Records** | **2,500** | **Balanced, fully interconnected synthetic banking universe.** |

---

### 5. Geographic Assumptions [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

Reflecting the Democratic Republic of the Congo's economic geography as established in Phase 1:
* **Primary Urban Hubs & Distribution:**
  * `Kinshasa` (Capital & Financial Hub) — ~50% of volume
  * `Lubumbashi` (Mining Center of Haut-Katanga) — ~25% of volume
  * `Kolwezi` (Lualaba Mining Axis) — ~10% of volume
  * `Goma` (Eastern Trade Corridor) — ~8% of volume
  * `Matadi` (Maritime Port of Kongo Central) — ~5% of volume
  * `Bukavu` (South Kivu Commercial Hub) — ~2% of volume
* **Impossible Travel Heuristic:**
  * Distance between Kinshasa and Lubumbashi is ~1,560 km (minimum flight time: 2.5 hours).
  * Any consecutive transactions or logins between Kinshasa and Lubumbashi within < 90 minutes are classified as **Impossible Geographic Travel**.

---

### 6. Currency Assumptions [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

* **Dual-Currency Standard:** Every financial amount operates in either Congolese Francs (`CDF`) or United States Dollars (`USD`).
* **Synthetic Peg Rate:** A realistic fixed baseline exchange rate of `1 USD = 2,750 CDF` is adopted across all currency normalization fields to allow seamless cross-currency risk aggregation.
* **Denomination Rules:**
  * USD transactions range from $5.00 to $75,000.00 (with corporate limits up to $150,000.00).
  * CDF transactions range from 15,000 CDF (~$5.45) to 200,000,000 CDF (~$72,727).
* No account carries a negative balance unless explicitly flagged with a pre-approved overdraft facility.

---

### 7. Banking Channel & Product Assumptions [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

* **Supported Channels:**
  * `IllicoCash_App` (Mobile banking & digital wallet — ~55% of transactions)
  * `RawbankOnline_Web` (Corporate & SME portal — ~20% of transactions)
  * `ATM_Cardless` (Dynamic OTP cash withdrawal — ~10% of transactions)
  * `Agency_Express_POS` (Local branchless agent cash-in/cash-out — ~10% of transactions)
  * `SWIFT_Wire` (International cross-border transfer — ~5% of transactions)
* **Transaction Types:**
  * `P2P_Transfer` (Mobile/account transfer to individuals)
  * `Merchant_Payment` (QR code or POS purchase)
  * `Cardless_CashOut` (ATM withdrawal without card)
  * `Agent_CashOut` (Withdrawal via Rawbank Express agent)
  * `Agent_CashIn` (Deposit via Rawbank Express agent)
  * `Bulk_Payroll_Disbursement` (Corporate salary payment)
  * `FX_Conversion` (In-app CDF <-> USD exchange)
  * `Bill_Payment` (Utility / telecom airtime)

---

### 8. Fraud Pattern & Scenario Assumptions [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

Because `SentientData_RuleSet.md` is unavailable, the synthetic environment models eight distinct forensic scenarios:

1. **Scenario A (Account Takeover & Drain):** Unrecognized device logs in from a novel IP; password reset initiated; new beneficiary added; immediate maximum-limit transfer.
2. **Scenario B (High Transaction Velocity):** 5 to 7 transfers executed within a 4-minute window to different recipients, rapidly depleting an account balance.
3. **Scenario C (Shared Device Syndicate):** A single hardware device ID (`DEV-XXXXX`) is observed executing transactions across 4 completely distinct customer accounts.
4. **Scenario D (Mule Account Fan-In):** Multiple distinct customers across different cities send round-sum transfers to a single recipient (`BEN-XXXXX`), who immediately initiates cash-out.
5. **Scenario E (Impossible Travel / Geo Velocity):** A login session in Kinshasa followed 20 minutes later by an ATM cash-out in Goma (1,500+ km away).
6. **Scenario F (Brute Force / Credential Anomaly):** 4 consecutive failed login attempts on `IllicoCash_App`, followed by a sudden successful login and instant outbound transfer.
7. **Scenario G (Structuring / Smurfing):** 3 to 4 sequential transfers timed 15 minutes apart, each priced at $9,400–$9,800 to remain just below the $10,000 regulatory AML reporting ceiling.
8. **Scenario H (Multi-Signal Critical Convergence):** Foreign VPN IP + new unverified device + abnormal hour (03:30 AM) + velocity breach.

---

### 9. Legitimate Anomaly Assumptions [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

To rigorously test false positive mitigation and counter-evidence reasoning, the generator produces legitimate anomalies that trigger rule thresholds but are substantiated by authenticating counter-evidence:
* **Legitimate High-Value Corporate Payment:** Large $55,000 transfer by a verified corporate executive to a regular, long-standing supplier during normal business hours.
* **Legitimate Customer Travel:** An executive flying from Kinshasa to Lubumbashi with an elapsed time of 4 hours, verified by biometric face recognition on their enrolled primary device.
* **Legitimate Device Upgrade:** A retail customer enrolling a new Samsung smartphone, preceded by SMS OTP verification and followed by a small, routine P2P transfer to a known family beneficiary.
* **Emergency Medical / Off-Hours Payment:** A late-night transfer (02:15 AM) to a known hospital or family member, matching historic seasonal patterns.

---

### 10. Database Architecture Choice [PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]

* **Database Engine:** **SQLite 3** (`database/synthetic_bank.db`).
* **Technical Justification:**
  * Zero-configuration, serverless, self-contained local database.
  * Standard ANSI SQL support with native foreign key enforcement (`PRAGMA foreign_keys = ON`).
  * Instant sub-millisecond query execution over 2,500 records.
  * Fully reproducible schema via idempotent DDL migration script.
  * Seamless compatibility with Python, FastAPI, Node.js, and browser tools.
  * Avoids unnecessary docker/cloud dependencies during local development.
