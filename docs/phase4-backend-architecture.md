# Rawbank Sentient Fraud Intelligence Platform
## Phase 4: Backend & Data Access API Architecture

**Status:** Completed (Phase 4 Verified)  
**Governance:** Strict Ground Truth — Zero LLM Dependencies — 100% Deterministic Relational Access  
**Framework:** FastAPI 0.135.3 / Uvicorn 0.44.0 / Python 3.14.3 / SQLite 3 / Pydantic v2  

---

## 1. Executive Summary & Objective

Phase 4 establishes the robust, low-latency Backend & Data Access API layer for the **Rawbank Sentient Fraud Intelligence Platform**. This layer bridges the underlying Phase 2 synthetic banking database (2,500 records across 9 relational tables) and Phase 3 deterministic fraud intelligence engine to future user interfaces:
1. **Sentient Command Centre** (Surveillance, Prioritization, Triage, Drill-down)
2. **Sentient Fraud Investigation Copilot** (Deep forensic analysis, evidence synthesis, counter-evidence evaluation)

### Core Architectural Principle:
```
           SQLite Database (2,500 Synthetic Records)
                              │
                              ▼
                Data Access Layer (Repositories)
                              │
                              ▼
            Deterministic Rules Engine (11 Forensic Rules)
                              │
                              ▼
               Evidence Packet Builder (3 Tiers)
                              │
                              ▼
               Backend API Layer (FastAPI Routers)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          Future Command Centre    Future Copilot
           (Phase 5 & 6)            (Phase 8 & 9)
```

> [!IMPORTANT]
> **"The LLM is NOT the database."**
> All entity metrics, account balances, transaction timelines, risk scores, and graph connections derive strictly from verified database records via parameterized SQL. Zero artificial intelligence or hallucinated state is present in this layer.

---

## 2. Technology & Framework Decisions

| Component | Selected Technology | Technical Rationale |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | High-performance asynchronous and threaded REST framework with automatic OpenAPI 3.1 documentation, strict typing via Pydantic v2, and dependency injection. |
| **ASGI Server** | **Uvicorn** | Fast, lightweight ASGI server enabling concurrent connection handling. |
| **Data Validation** | **Pydantic v2** | Strong typing for all request parameters, URL paths, and JSON response bodies. Enforces data integrity before business logic execution. |
| **Database** | **SQLite 3** | Zero-configuration, zero-network-latency embedded relational engine enforcing foreign keys (`PRAGMA foreign_keys = ON`). |
| **Testing** | **unittest + httpx (TestClient)** | Comprehensive automated test suite exercising real HTTP requests against the actual synthetic bank database without mocking away queries. |

---

## 3. Directory & Module Structure

```
backend/
├── app/
│   ├── __init__.py               # Package marker and version (1.0.0)
│   ├── config.py                 # Pydantic BaseSettings, path resolution, CORS config
│   ├── database.py               # SQLite connection factory & connectivity health checks
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── deps.py               # Reusable FastAPI dependencies (db session, pagination)
│   ├── models/
│   │   └── __init__.py           # Relational domain markers
│   ├── repositories/             # Pure Data Access Layer (parameterized SQL only)
│   │   ├── __init__.py
│   │   ├── base.py               # Row-to-dict converters, safe sorting, pagination math
│   │   ├── overview_repo.py      # System KPIs and alert aggregate calculations
│   │   ├── alert_repo.py         # Multi-filter alert queue and alert dossier queries
│   │   ├── transaction_repo.py   # Transaction queries with account/customer/device joins
│   │   ├── customer_repo.py      # Customer 360-degree forensic dossiers & baseline links
│   │   ├── device_repo.py        # Device fingerprints, trust status, and shared users
│   │   ├── beneficiary_repo.py   # Beneficiary accounts and mule network aggregations
│   │   ├── signal_repo.py        # Deterministic fraud signals and rule audit records
│   │   ├── entity_repo.py        # 1-hop and 2-hop topological graph link explorer
│   │   └── search_repo.py        # Fast deterministic cross-entity search engine
│   ├── schemas/                  # Typed Pydantic request and response contracts
│   │   ├── __init__.py
│   │   ├── common.py             # PaginationMetadata, PaginatedResponse[T], ErrorResponse
│   │   ├── health.py             # HealthResponse
│   │   ├── overview.py           # OverviewResponse
│   │   ├── alert.py              # AlertSummary, AlertDetail
│   │   ├── transaction.py        # TransactionSummary, TransactionDetail
│   │   ├── customer.py           # CustomerSummary, CustomerDossier
│   │   ├── device.py             # DeviceSummary, DeviceDetail
│   │   ├── beneficiary.py        # BeneficiarySummary, BeneficiaryDetail
│   │   ├── signal.py             # SignalSummary, SignalDetail
│   │   ├── entity.py             # EntityRelationshipsResponse, EntityEdge
│   │   ├── evaluate.py           # TransactionEvaluationResponse, CustomerEvaluationResponse
│   │   ├── evidence.py           # EvidenceResponse (Strict 3-Tier Taxonomy)
│   │   └── search.py             # SearchResponse, SearchResultItem
│   ├── services/                 # Business logic and Phase 3 engine orchestration
│   │   ├── __init__.py
│   │   ├── evaluation_service.py # Bridges API to Phase 3 FraudIntelligenceEngine
│   │   └── evidence_service.py   # Assembles 3-tier forensic evidence packets
│   ├── routers/                  # Modular FastAPI route controllers
│   │   ├── __init__.py
│   │   ├── health.py             # GET /api/health
│   │   ├── overview.py           # GET /api/overview
│   │   ├── alerts.py             # GET /api/alerts, GET /api/alerts/{id}
│   │   ├── transactions.py       # GET /api/transactions, GET /api/transactions/{id}
│   │   ├── customers.py          # GET /api/customers, GET /api/customers/{id}
│   │   ├── devices.py            # GET /api/devices, GET /api/devices/{id}
│   │   ├── beneficiaries.py      # GET /api/beneficiaries, GET /api/beneficiaries/{id}
│   │   ├── entities.py           # GET /api/entities/{type}/{id}/relationships
│   │   ├── signals.py            # GET /api/signals, GET /api/signals/{id}
│   │   ├── evaluate.py           # POST /api/evaluate/transaction/{id}, customer/{id}
│   │   ├── evidence.py           # GET /api/evidence/{id}
│   │   └── search.py             # GET /api/search?q=...
│   └── main.py                   # FastAPI app instance, CORS middleware, error handlers
├── tests/
│   └── test_api.py               # 24 automated endpoint tests against synthetic bank DB
└── .env.example                  # Environment configuration template (zero secrets)
```

---

## 4. Database Access Layer & Repository Pattern

To prevent raw SQL from leaking into API route handlers, all database interactions are encapsulated in dedicated repositories under `backend/app/repositories/`.

### Key Repository Features:
1. **Parameterized SQL Queries:** 100% of user-supplied values are bound via `?` parameters, preventing SQL injection vulnerabilities.
2. **Column Whitelisting:** Dynamic sorting and filtering strictly validate column names against predefined dictionaries (`SORT_COLUMNS`), rejecting arbitrary SQL expressions.
3. **Foreign Key Integrity:** All connections instantiate with `PRAGMA foreign_keys = ON;`.
4. **Performance & Index Utilization:**
   - Table joins leverage indexes defined in Phase 2 (`idx_transactions_customer_id`, `idx_alerts_transaction_id`, etc.).
   - Multi-hop graph lookups execute in sub-millisecond execution times.

---

## 5. Phase 3 Deterministic Engine Integration

The backend directly invokes the Phase 3 `FraudIntelligenceEngine` from `rules/engine.py`:
* **Zero Duplication of Fraud Logic:** Rule thresholds, rolling time-window calculations, and risk-weight correlations remain isolated within the `rules/` package.
* **On-Demand Transaction Evaluation (`POST /api/evaluate/transaction/{id}`):**
  - Pulls transaction from SQLite.
  - Executes all 11 registered forensic rules (`VelocityRule`, `ValueSpikeRule`, `NewDeviceRule`, `SharedDeviceRule`, `NewBeneficiaryRule`, `SharedBeneficiaryRule`, `GeographicVelocityRule`, `StructuringRule`, `AuthenticationAnomalyRule`, `ATOPatternRule`, `BehaviouralDeviationRule`).
  - Correlates signals via `CorrelationEngine.evaluate()`, calculating composite risk score [0–100], scenario classification, and score contribution breakdown.
  - Attaches fresh 3-tier forensic evidence packet.
* **Customer Evaluation (`POST /api/evaluate/customer/{id}`):**
  - Gathers customer's latest transactions.
  - Evaluates each transaction through the rule engine.
  - Aggregates peak risk score, overall severity, and contributing signal catalog.
  - Emits a transparent forensic summary without arbitrary black-box scores.

---

## 6. Grounded Evidence Packet Flow

In strict compliance with the Phase 3 forensic taxonomy, evidence packets served through `GET /api/evidence/{transaction_id}` and `GET /api/transactions/{transaction_id}/evidence` maintain a rigid 4-tier structure:

```json
{
  "transaction_id": "TXN-00801",
  "customer_id": "CUS-00014",
  "generated_at": "2026-09-28T11:01:58.758170+00:00",
  "tier_1_exact_data": {
    "transaction": { "amount": 4800.0, "currency": "USD", "channel": "IllicoCash_App" },
    "source_account": { "account_id": "ACC-00028", "balance": 82264.0 },
    "customer": { "full_name": "Christelle Mutombo", "kyc_status": "Tier_2_Standard" },
    "device": { "device_id": "DEV-00127", "trust_status": "New_Unverified" },
    "beneficiary": { "beneficiary_name": "Tshimanga Quick Cash", "is_known_mule": 0 }
  },
  "tier_2_calculated": {
    "composite_risk_score": 100,
    "severity": "CRITICAL",
    "scenario_type": "ATO_DRAIN",
    "velocity_1h_count": 1,
    "amount_to_baseline_ratio": 18.46
  },
  "tier_3_retrieved_evidence": {
    "behavioural_baseline": { "avg_monthly_volume_usd": 1250.0, "avg_tx_amount_usd": 260.0 },
    "recent_auth_events": [ ... ],
    "prior_device_history": [ ... ],
    "shared_device_co_users": [ ... ]
  },
  "tier_4_ai_reasoning": null
}
```

> [!CAUTION]
> **Tier 4 AI Reasoning** is explicitly set to `None`. In Phase 4, AI has not yet been introduced. This field is reserved for the Groq inference integration in Phase 7.

---

## 7. Unified Graph & Relationship Exploration

The endpoint `GET /api/entities/{entity_type}/{entity_id}/relationships` powers visual graph link exploration for investigators:
* **Supported Entity Types:** `customer`, `account`, `transaction`, `device`, `beneficiary`, `alert`.
* **1-Hop Direct Links:**
  - Customer $\to$ Accounts (`OWNS_ACCOUNT`)
  - Customer $\to$ Devices (`USES_DEVICE`)
  - Customer $\to$ Beneficiaries (`TRANSFERS_TO`)
  - Customer $\to$ Alerts (`SUBJECT_OF_ALERT`)
* **2-Hop Shared Entities (Clustering):**
  - Device $\to$ Other Customers (`ALSO_USED_BY` / `SHARED_WITH_USER`)
  - Beneficiary $\to$ Other Customer Senders (`ALSO_RECEIVES_FROM` / `COMMON_BENEFICIARY_SENDER`)
* **Ground Truth Guarantee:** Every graph node and edge maps directly to verified foreign key relations in SQLite.

---

## 8. Deterministic Cross-Entity Search

The endpoint `GET /api/search?q={query}` provides unified search capabilities across:
* **Customers:** Matches `customer_id`, `full_name`, `email`, `primary_phone`.
* **Accounts:** Matches `account_id`.
* **Transactions:** Matches `transaction_id`, `location_city`.
* **Devices:** Matches `device_id`, `device_model`, `ip_address`, `ip_city`.
* **Beneficiaries:** Matches `beneficiary_id`, `beneficiary_name`, `institution_name`, `account_or_phone`.
* **Alerts:** Matches `alert_id`, `scenario_type`, `reason_summary`.

Matches are ranked deterministically:
1. Exact ID match (Rank 0)
2. ID prefix match (Rank 1)
3. Name/Title substring match (Rank 2)
4. Other attribute match (Rank 3)

---

## 9. Error Handling & Exception Architecture

All API responses follow consistent JSON error structures:
* **`400 Bad Request`:** Raised on invalid enum values (e.g. `severity=SUPER_CRITICAL`, `currency=EUR`, unsupported entity types).
* **`404 Not Found`:** Raised when an entity ID (`alert_id`, `transaction_id`, `customer_id`, etc.) does not exist in the database.
* **`422 Unprocessable Content`:** Raised on parameter validation failures (e.g. `page=0`, `page_size > 100`).
* **`500 Internal Server Error`:** Global catch-all handler logs the full traceback internally while returning a sanitized message to the client, preventing leakage of system paths or credentials.

---

## 10. Security Baseline & Compliance

* **Zero Secrets in Code:** Configuration is read from environment variables or `.env.example`.
* **Controlled CORS:** Configured via comma-separated origin whitelist (`CORS_ORIGINS`). Unrestricted wildcard (`*`) is disabled in production settings.
* **SQL Injection Prevention:** 100% parameterized SQL. Column names for sorting and filtering are strictly whitelisted against static dictionaries.
* **No Arbitrary System Access:** The API contains zero endpoints executing shell commands, operating system scripts, or arbitrary file access.
* **Synthetic Local Scope:** All data is synthetic; zero production PII or real banking credentials exist in the system.

---

## 11. Regression Testing & Verification

The Phase 4 test suite verified 100% compliance across all previous and current phases:

1. **Phase 2 Validation (`python scripts/validate_data.py`):**
   - **15 / 15 PASSED** (0 failed). Zero data corruption.
2. **Phase 3 Rules Engine Tests (`python tests/test_rules_engine.py`):**
   - **24 / 24 PASSED** (0 failed). Zero logic deviation.
3. **Phase 4 API Tests (`python tests/test_api.py`):**
   - **24 / 24 PASSED** in 0.49s against live database.
4. **Manual Verification (`python scripts/verify_api_manual.py`):**
   - Verified 12 representative endpoints returning HTTP 200 with live payloads.
5. **OpenAPI Schema (`GET /openapi.json`):**
   - Validated OpenAPI 3.1 specification exposing 21 endpoint paths.
