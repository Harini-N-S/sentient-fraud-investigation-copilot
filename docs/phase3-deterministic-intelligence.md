# Phase 3 Deterministic Intelligence Architecture
## Sentient Fraud Intelligence Platform (Rawbank DRC)

**Document Reference:** `docs/phase3-deterministic-intelligence.md`  
**Execution Phase:** Phase 3 — Deterministic Fraud Intelligence  
**Component:** `rules/` Engine Subsystem  
**Source Database:** `database/synthetic_bank.db` (SQLite 3)  
**Governance:** Strict Deterministic Calculations (Zero Machine Learning, Zero LLM)

---

### 1. Architectural Philosophy: The Deterministic Foundation

```
┌────────────────────────────────────────────────────────┐
│               Structured Banking Data                  │
│       (SQLite Database: Transactions, Accounts, Logs)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│            Deterministic Rule Evaluators               │
│      (Velocity, Value Spikes, Devices, Travel, etc.)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 Discrete Fraud Signals                 │
│        (Rule Code, Weights, Unaltered Evidence)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Deterministic Correlation Layer            │
│         (Mitigation Discounts, Risk Score 0–100)       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│           Grounded 3-Tier Evidence Packet              │
│      (Exact Data + Calculated Metrics + Retrieved Logs)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        Alerts & Forensic Operational Workstation       │
│      (Feeds Command Centre & Future Copilot Layer)     │
└────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **WHY DETERMINISTIC INTELLIGENCE PRECEDES AI REASONING**  
> In banking risk operations, explainability is a legal mandate. An anti-fraud system must be able to state mathematically why an account was frozen or flagged.  
> Large Language Models (LLMs) cannot reliably count 5 rapid transactions within 240 seconds, calculate geodesic travel velocities, or compute variance against standard deviation baselines without hallucinating.  
> Therefore, Phase 3 establishes the **deterministic intelligence engine** that produces zero-hallucination mathematical signals, which the Groq LLM layer will later consume as grounded evidence tokens.

---

### 2. Execution Flow & Processing Pipeline

The runtime pipeline operates through five sequential stages:

#### Stage 1: Atomic Ingestion & Context Resolution
When a transaction is evaluated via `FraudIntelligenceEngine.evaluate_transaction(transaction_id)`:
* The transaction record is loaded alongside customer metadata, device parameters, counterparty beneficiary details, and account ledger balances.
* The 60-day `behavioural_baselines` statistical record is joined to provide normative boundaries.

#### Stage 2: Individual Rule Evaluation
The transaction is evaluated against 11 specialized rule classes:
1. `VelocityRule` (`R-VEL-01`): Rolling time-window transaction count and volume.
2. `ValueSpikeRule` (`R-VAL-07`): Percentage deviation and multiplier against historical max.
3. `NewDeviceRule` (`R-DEV-02`): Trust status, age of device binding, novel hardware fingerprints.
4. `SharedDeviceRule` (`R-DEV-SHR-01`): Distinct customer count operating on the same physical hardware.
5. `NewBeneficiaryRule` (`R-BEN-03`): Prior transaction relationship history with counterparty.
6. `SharedBeneficiaryRule` (`R-MULE-04`): Multi-customer inbound concentration / aggregator topology.
7. `GeographicVelocityRule` (`R-GEO-03`): Physical distance (DRC pairwise table) divided by elapsed hours.
8. `StructuringRule` (`R-SMURF-06`): Clustering of amounts in the near-threshold band ($8,500–$9,999 USD).
9. `AuthenticationAnomalyRule` (`R-AUTH-08`): Consecutive failed PIN attempts within 30 minutes.
10. `ATOPatternRule` (`R-ATO-05`): Administrative password reset or new device enrolled within 60 minutes.
11. `BehaviouralDeviationRule` (`R-BEH-09`): Off-hours activity or unfamiliar transaction channel.

Each rule returns an array of `SignalResult` objects containing exact evidence parameters.

#### Stage 3: Multi-Signal Correlation & Mitigation Assessment
The `CorrelationEngine` aggregates all triggered signals and performs counter-evidence analysis:
* **Mitigation Evaluation:** Checks for verified corporate multi-authorization, Tier-3 KYC status, matching vendor registries, trusted primary device enrollment, and preceding biometric authentications.
* **Mitigation Discounts:** Verified legitimate counter-evidence applies a transparent mathematical deduction to the raw risk score.

#### Stage 4: Transparent Risk Scoring Formula
The final composite risk score is strictly deterministic:

$$\text{RawScore} = \sum_{i=1}^{N} \Big(\text{RuleWeight}_i \times \text{ConfidenceScore}_i\Big)$$

$$\text{CompositeRiskScore} = \max\Big(0, \min\big(100, \text{round}(\text{RawScore} - \text{MitigationDiscount})\big)\Big)$$

Severity is mapped transparently:
* **Score $\ge 90$:** `CRITICAL`
* **Score $70\text{--}89$:** `HIGH`
* **Score $40\text{--}69$:** `MEDIUM`
* **Score $< 40$:** `LOW`

#### Stage 5: Grounded Evidence Packet Assembly
The `EvidencePacketBuilder` packages the findings into a structured 3-tier dossier:
* **Tier 1 (Exact Data):** Unaltered raw records (ledger balances, transaction IDs, UTC timestamps, device models, beneficiary names).
* **Tier 2 (Calculated Metrics):** Deterministic mathematical indicators (24h velocity, deviation %, implied travel speed, distinct account counts, composite risk score).
* **Tier 3 (Retrieved Evidence):** Historical baselines, preceding 5 transactions, preceding 5 authentication logs, connected device accounts, triggered signals.
* **Tier 4 (AI Reasoning):** **STRICTLY NULL IN PHASE 3.** (Reserved for Phase 7 Groq integration).

---

### 3. False-Positive Mitigation & Counter-Evidence Handling

The engine rejects the simplistic assumption that *"Rule Breach = Fraud"*:
* A large transaction of $68,898 USD triggers `R-VAL-07` (Value Spike).
* However, because the customer is a verified Tier-3 Corporate entity, the beneficiary is an established commercial vendor, and the device is a trusted enrolled corporate laptop, the `CorrelationEngine` applies a 25-point mitigation discount.
* The composite score drops to **28/100 (LOW)**, and the scenario is classified as `LEGITIMATE_ANOMALY`.
* The analyst is presented with all underlying numbers and the explicit mitigating rationale.

---

### 4. System Limitations

1. **Rule Set Scope:** Current rules represent project assumptions developed in the absence of `SentientData_RuleSet.md`.
2. **Offline Local SQLite:** The engine runs synchronously against `database/synthetic_bank.db`.
3. **No Streaming Message Broker:** Evaluates on-demand via Python function calls rather than a distributed Kafka/RabbitMQ pipeline.
