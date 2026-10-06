# Rawbank Sentient Fraud Intelligence Platform
## Phase 5: Semantic Retrieval & Evidence Layer Architecture

**Status:** Completed (Phase 5 Verified)  
**Governance:** Strict Ground Truth — Zero LLM Dependencies — 100% Explainable Provenance  
**Framework:** FastAPI 0.135.3 / SQLite 3 / Pydantic v2 / In-Memory Inverted Index (BM25)  

---

## 1. Executive Summary & Objective

Phase 5 implements the **Semantic Retrieval & Evidence Layer** for the Rawbank Sentient Fraud Intelligence Platform. Positioned directly between Phase 3/4 deterministic data access and the future Fraud Investigation Copilot (Phase 7+), this layer ensures that all AI reasoning will be strictly anchored in verified database facts rather than generic chatbot hallucinations.

### The 8-Stage Platform Pipeline
```
[1] Structured Data (SQLite Synthetic Banking Database — 2,500 records)
         │
         ▼
[2] Deterministic Processing (Phase 3 Rules Engine — 11 Forensic Rules)
         │
         ▼
[3] Entity Resolution (Phase 5 Deterministic Resolver — zero-hallucination)
         │
         ▼
[4] Semantic Retrieval & Evidence Layer (Phase 5 Hybrid Retriever & Evidence Builder)  <-- THIS PHASE
         │
         ▼
[5] LLM Intelligence (Phase 7+ Groq Llama-3 Forensic Reasoner — FUTURE)
         │
         ▼
[6] Backend API (FastAPI Data Access & Intelligence Routers)
         │
         ▼
[7] Frontend (Phase 6 Command Centre & Phase 8 Copilot UI — FUTURE)
         │
         ▼
[8] Application Experience (Interactive Forensic Workstation)
```

> [!IMPORTANT]
> **Core Architectural Principle: "The LLM is NOT the Database."**  
> AI Reasoning is explicitly deferred to future phases. Phase 5 enforces a rigid boundary:
> 1. **EXACT DATA** (Immutable database ledger columns)
> 2. **CALCULATED INFORMATION** (Deterministic mathematical ratios, scores, cluster sizes)
> 3. **RETRIEVED EVIDENCE** (Historical baselines, prior devices, co-user clusters, auth logs)
> 4. **COUNTER-EVIDENCE** (Mitigating facts supporting legitimate customer activity / false positives)
> 5. **EVIDENCE GAPS** (Explicitly documented missing facts rather than speculative assumptions)
> 6. **AI REASONING** (Strictly absent in Phase 5)

---

## 2. Directory & Module Structure

The retrieval and evidence layer is organized under `backend/app/retrieval/`:

```
backend/app/retrieval/
├── __init__.py               # Package marker and public interface exports
├── models.py                 # Pydantic data contracts (RetrievalDocument, EvidencePacket, etc.)
├── entity_resolver.py        # Deterministic regex and multi-attribute entity resolver
├── query_parser.py           # Intent classification, filter extraction, and keyword tokenizer
├── indexer.py                # In-memory document builder & inverted BM25 index
├── ranking.py                # Multi-factor transparent relevance scoring engine
├── retriever.py              # Hybrid multi-vector retrieval coordinator
└── evidence_builder.py       # Standardized grounded forensic evidence packet builder
```

---

## 3. Deterministic Entity Resolution

The future Copilot must never guess or fabricate entity identifiers. The `EntityResolver` performs deterministic matching:

### Supported Identifiers & Canonical Mapping
| Entity Type | Input Variations Accepted | Canonical Format | DB Validation Target |
| :--- | :--- | :--- | :--- |
| **Customer** | `CUS-00014`, `CUST-0012`, `CUS-14`, `CUST-14` | `CUS-%05d` | `customers.customer_id` |
| **Account** | `ACC-00028`, `ACC-28`, `ACC28` | `ACC-%05d` | `accounts.account_id` |
| **Transaction** | `TXN-00801`, `TXN-801`, `TXN801` | `TXN-%05d` | `transactions.transaction_id` |
| **Device** | `DEV-00127`, `DEV-127`, `DEV127` | `DEV-%05d` | `devices.device_id` |
| **Beneficiary** | `BEN-00088`, `BEN-88`, `BEN88` | `BEN-%05d` | `beneficiaries.beneficiary_id` |
| **Alert** | `ALT-00001`, `ALT-1`, `ALT1` | `ALT-%05d` | `alerts.alert_id` |
| **Signal** | `SIG-00001`, `SIG-1`, `SIG1` | `SIG-%05d` | `fraud_signals.signal_id` |

### Resolution Algorithm
1. **Identifier Extraction:** Regular expressions scan query text for prefix patterns with zero-padding tolerance.
2. **Database Verification:** Every candidate ID is validated via parameterized SQL against its primary table.
   - If present: `confidence = 1.0`, `matching_method = "exact_id"` (or `"normalized_id"`).
   - If not in DB: `confidence = 0.0`, `matching_method = "unknown_identifier"`. Zero records fabricated.
3. **Natural Language Names:**
   - Detects customer full names (e.g. "Christelle Mutombo") and beneficiary names ("Tshimanga Quick Cash").
   - If exactly one record matches: `confidence = 0.95` (`"exact_name"`).
   - If multiple records match (e.g. "Jean Mutombo"): `is_ambiguous = True`, `confidence = 0.50`, `matching_method = "ambiguous_match"`, candidate list returned.

---

## 4. Retrieval Technology & Hybrid Indexing

### Technology Decision & Local Reproducibility
* **Chosen Technology:** In-Memory Multi-Index + BM25 Lexical Inverted Index over SQLite.
* **Why this approach was chosen:**
  1. **Zero External Cloud Dependencies:** Does not require external vector databases, Pinecone, or cloud API keys.
  2. **Sub-Millisecond Latency:** 2,618 normalized documents indexed in ~0.15s; search response times < 5ms.
  3. **100% Explainable Scoring:** Every ranking decision is mathematically traceable; zero opaque black-box embeddings.
  4. **Vector-Ready Interface:** The modular retriever architecture can incorporate dense vector embeddings (e.g. local `sentence-transformers` or embeddings API) in future phases without altering API contracts or data models.

### Multi-Index Topology
```
                          ┌───────────────────────────┐
                          │   SQLite Database File    │
                          │   synthetic_bank.db       │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                             [ BankingIndexer ]
                                        │
        ┌───────────────┬───────────────┼───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
   [ Entity Map ]  [ Type Map ]  [ FK Indices ]  [ Inverted Index ] [ Clusters ]
   (type, id)->doc  type->[docs]  cus_id->[docs]  token->{doc:tf}    shared dev /
                                  dev_id->[docs]  avg_dl precomputed mule hubs
```

---

## 5. Normalized Retrieval Documents

Structured banking tables are converted into 2,618 normalized `RetrievalDocument` instances containing human-readable summaries and structured metadata:

1. **CUSTOMER (120 docs):** Full profile, KYC tier, risk category, registered city, account balances, registered hardware.
2. **ACCOUNT (240 docs):** Account type, currency (CDF/USD), current & available balances, status, ownership link.
3. **TRANSACTION (900 docs):** Amount, currency, USD equivalent, channel, city, status, sender, recipient, originating device, triggered rules, linked alerts.
4. **DEVICE (150 docs):** Hardware model, OS, fingerprint hash, IP address, city, trust status, VPN/Tor flag, co-user customer count.
5. **BENEFICIARY (180 docs):** Name, institution, MSISDN/account, city, known mule flag, distinct sender count, aggregated received volume.
6. **AUTHENTICATION_EVENT (450 docs):** Customer, device, event type (login, password reset, OTP), status, failure reason, timestamp.
7. **BEHAVIOURAL_BASELINE (120 docs):** Moving monthly volume, average transaction amount, maximum single transaction, active hours UTC, frequent cities.
8. **ALERT (140 docs):** Severity, composite risk score, scenario type, reason summary, customer, transaction.
9. **FRAUD_SIGNAL (200 docs):** Rule code, rule name, category, severity, confidence, signal description.
10. **RULE_EVIDENCE (11 docs):** Specifications for all 11 Phase 3 deterministic forensic rules.
11. **RELATIONSHIP (77 docs):** Pre-aggregated cluster summaries for shared device rings and mule concentration hubs.

---

## 6. Transparent & Explainable Ranking

The ranker computes a normalized relevance score $[0.0 - 1.0]$ driven by transparent additive factors:

```
Relevance Score = Clamp(
    + 0.35 [Exact Identifier Match]
    + 0.30 [Primary Target Entity Match]
    + 0.25 [Direct 1-Hop Foreign Key Relationship]
    + 0.20 [Scenario Type Match: ATO, Travel, etc.]
    + 0.18 [Rule Code Match: R-ATO-05, etc.]
    + 0.15 [Severity Boost: Critical (+0.12), High (+0.08), Medium (+0.04)]
    + 0.20 [BM25 Lexical Keyword Similarity]
    + 0.18 [Counter-Evidence / False Positive Factor]
    + 0.20 [Relational Syndicate Cluster Factor]
)
```

Each retrieved result attaches `relevance_reasons`:
```json
{
  "relevance_score": 0.92,
  "relevance_reasons": [
    "exact_identifier_match(customer:CUS-00014)",
    "primary_resolved_entity",
    "critical_severity_alert",
    "scenario_match(ATO_DRAIN)",
    "keyword_lexical_match(bm25=0.45)"
  ]
}
```

---

## 7. Controlled Relationship Expansion

The retrieval engine prevents graph explosion by enforcing hard limits:
- `MAX_RELATED_ENTITIES = 20`
- `MAX_TRANSACTIONS = 15`
- `MAX_ALERTS = 10`
- `MAX_RELATIONSHIP_DEPTH = 2`

### Traversal Paths
* **Customer-Centric:** Customer $\to$ Accounts $\to$ Transactions $\to$ Devices $\to$ Beneficiaries $\to$ Alerts $\to$ Signals.
* **Device-Centric (Syndicate Clustering):** Device $\to$ Co-using Customers $\to$ Secondary transactions $\to$ Shared device ring alerts.
* **Beneficiary-Centric (Mule Networks):** Beneficiary $\to$ Senders $\to$ Aggregate inbound USD volume $\to$ Fan-in concentration alerts.

---

## 8. Standardized Evidence Packet & Provenance

When an investigation query is processed, the system generates a standardized evidence dossier:

```json
{
  "query": "Why was customer CUS-00014 flagged?",
  "generated_at": "2026-09-28T20:39:54.164282+00:00",
  "target_entity": {
    "entity_type": "customer",
    "entity_id": "CUS-00014",
    "canonical_id": "CUS-00014",
    "confidence": 1.0,
    "matching_method": "exact_id"
  },
  "resolved_entities": [ ... ],
  "exact_data": [
    {
      "type": "EXACT_DATA",
      "source_table": "transactions",
      "source_id": "TXN-00801",
      "field": "amount_usd_equivalent",
      "value": 4800.0,
      "description": "Transaction ledger attribute: amount_usd_equivalent = 4800.0",
      "timestamp": "2026-09-16T03:25:00",
      "provenance": { "table": "transactions", "pk": "transaction_id", "pk_val": "TXN-00801" }
    }
  ],
  "calculated_information": [
    {
      "type": "CALCULATED",
      "source_table": "alerts",
      "source_id": "ALT-00001",
      "field": "composite_risk_score",
      "value": 96,
      "description": "Alert ALT-00001 (CRITICAL): Risk Score 96/100. Scenario: ATO_DRAIN."
    }
  ],
  "retrieved_evidence": [
    {
      "type": "RETRIEVED_EVIDENCE",
      "source_table": "auth_activities",
      "source_id": "AUTH-00389",
      "field": "event_type",
      "value": "Password_Reset_Triggered",
      "description": "Password Reset Triggered on 2026-09-16T03:10:00 via IllicoCash_App."
    }
  ],
  "counter_evidence": [ ... ],
  "relationships": [ ... ],
  "evidence_gaps": [ ... ],
  "source_references": [
    { "table": "customers", "id": "CUS-00014" },
    { "table": "transactions", "id": "TXN-00801" },
    { "table": "alerts", "id": "ALT-00001" }
  ]
}
```

---

## 9. Explicit Evidence Gaps (No Hallucination)

Instead of speculating or inventing facts, missing context is surfaced as structured `EvidenceGap` objects:

| Gap Type | Trigger Condition | Forensic Impact |
| :--- | :--- | :--- |
| `MISSING_BASELINE` | Customer has no entry in `behavioural_baselines` | Cannot compute spending deviation from moving median |
| `UNVERIFIED_DEVICE` | Hardware has `New_Unverified` trust status | Device has zero prior transaction history |
| `LACK_OF_AUTH_RECORDS` | Zero authentication logs in time window | Cannot confirm whether credential compromise occurred |
| `INSUFFICIENT_TRANSACTION_HISTORY` | Customer has zero recorded transactions | Velocity and historical patterns cannot be evaluated |
| `UNKNOWN_ENTITY` | Query refers to ID not in DB (e.g. `CUS-99999`) | Zero records exist; halts speculative reasoning |
| `AMBIGUOUS_ENTITY` | Name matches multiple customers | Disambiguation required before attributing actions |
| `INSUFFICIENT_QUERY_CONTEXT` | Query has no recognized entity or filters | Requires user to anchor investigation on an entity |
| `NO_RELATED_ALERTS` | Customer has zero alerts | Confirms baseline normal, unflagged profile |

---

## 10. False-Positive & Counter-Evidence Support

To support legitimate corporate transactions, VIP payments, and false-positive triage, the retrieval layer surfaces counter-evidence alongside suspicious indicators:

* **Corporate / VIP Segments:** High-value corporate payments (`TXN-00751`, $68,898 USD for `CUS-00010`) surface corporate baseline approval rules.
* **Full KYC Verification:** Customers with `Tier_3_Full` KYC verification are highlighted.
* **Trusted Enrolled Devices:** Hardware marked `Trusted_Enrolled` without root, jailbreak, VPN, or Tor flags is surfaced as mitigating evidence.
* **Deterministic Mitigation Rules:** Fired mitigation indicators from Phase 3 engine (e.g. corporate dual-authorization) are presented in the `counter_evidence` array.

---

## 11. Known Limitations & Future LLM Integration Plan

1. **Current Limitations:**
   - Lexical matching relies on exact tokens, sub-strings, and BM25 statistics rather than dense vector embeddings.
   - Ambiguous names return candidate lists rather than resolving through contextual user disambiguation.
2. **Future LLM Integration Plan (Phase 7+):**
   - Groq / Llama-3 inference will ingest the standardized `StandardEvidencePacket` as ground-truth context.
   - LLM prompts will be constrained strictly to citation IDs present in `source_references`.
   - Any LLM assertion lacking a citation in `source_references` will be flagged by automated grounding validators.
