# Rawbank Sentient Fraud Intelligence Platform
## Phase 4: REST API Reference Manual

**API Version:** 1.0.0  
**Base URL:** `http://127.0.0.1:8000`  
**OpenAPI Interactive UI:** `http://127.0.0.1:8000/docs`  
**OpenAPI JSON Schema:** `http://127.0.0.1:8000/openapi.json`  

---

## 1. Global Conventions

### Pagination Parameters
All collection endpoints support pagination via standard query parameters:
* `page` (integer, default `1`, min `1`): The 1-indexed page number.
* `page_size` (integer, default `25`, min `1`, max `100`): Maximum items per page.

### Pagination Response Wrapper
```json
{
  "items": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total": 140,
    "total_pages": 6,
    "has_next": true,
    "has_prev": false
  }
}
```

### Error Response Format
```json
{
  "detail": "Alert with ID 'ALT-99999' was not found in the database.",
  "error_code": "HTTP_404",
  "timestamp": "2026-09-28T11:01:58.566282+00:00"
}
```

---

## 2. API Endpoints Summary

| Method | Endpoint Path | Tags | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Health | Verifies service liveness and active database connectivity. |
| `GET` | `/api/overview` | Overview | Computes live KPI metrics for Command Centre dashboards. |
| `GET` | `/api/alerts` | Alerts | Paginated and filtered alert queue. |
| `GET` | `/api/alerts/{alert_id}` | Alerts | Full forensic alert dossier with transaction, customer, and signals. |
| `GET` | `/api/transactions` | Transactions | Paginated and filtered financial transaction log. |
| `GET` | `/api/transactions/{transaction_id}` | Transactions | Transaction dossier with attached evaluation and evidence packet. |
| `GET` | `/api/transactions/{transaction_id}/evidence` | Transactions | 3-tier forensic evidence packet (alias). |
| `GET` | `/api/customers` | Customers | Paginated customer list with multi-attribute search and balances. |
| `GET` | `/api/customers/{customer_id}` | Customers | 360-degree customer dossier (accounts, activity, baseline, devices, risk). |
| `GET` | `/api/devices` | Devices | Hardware inventory with trust status and security compromise flags. |
| `GET` | `/api/devices/{device_id}` | Devices | Device profile, associated customers, transaction volumes, auth logs. |
| `GET` | `/api/beneficiaries` | Beneficiaries | Destination accounts with mule flags and transaction aggregations. |
| `GET` | `/api/beneficiaries/{beneficiary_id}` | Beneficiaries | Beneficiary dossier with interacting customer senders and mule metrics. |
| `GET` | `/api/entities/{entity_type}/{entity_id}/relationships` | Entities | 1-hop and 2-hop graph topological exploration. |
| `GET` | `/api/signals` | Signals | Granular deterministic fraud signals with confidence scores. |
| `GET` | `/api/signals/{signal_id}` | Signals | Full signal forensic breakdown with rule metadata. |
| `POST` | `/api/evaluate/transaction/{transaction_id}` | Evaluation | Runs Phase 3 deterministic rule engine on a transaction. |
| `POST` | `/api/evaluate/customer/{customer_id}` | Evaluation | Runs Phase 3 deterministic rule engine on customer's recent activity. |
| `GET` | `/api/evidence/{transaction_id}` | Evidence | Dedicated 3-tier grounded forensic evidence packet endpoint. |
| `GET` | `/api/search` | Search | Fast, deterministic cross-entity multi-table search. |

---

## 3. Detailed Endpoint Specifications

### 3.1 Health Check
* **`GET /api/health`**
* **Response (200 OK):**
```json
{
  "status": "ok",
  "database": "connected",
  "environment": "development",
  "version": "1.0.0",
  "table_count": 9,
  "timestamp": "2026-09-28T11:01:58.566282+00:00"
}
```

---

### 3.2 System Overview
* **`GET /api/overview`**
* **Response (200 OK):**
```json
{
  "total_customers": 120,
  "total_accounts": 240,
  "total_transactions": 900,
  "total_alerts": 140,
  "total_fraud_signals": 200,
  "critical_alerts": 8,
  "high_alerts": 17,
  "medium_alerts": 49,
  "low_alerts": 66,
  "alerts_by_status": {
    "NEW_UNASSIGNED": 57,
    "UNDER_INVESTIGATION": 38,
    "DISMISSED_FALSE_POSITIVE": 45
  },
  "total_volume_usd": 2311183.57,
  "total_flagged_volume_usd": 946562.18,
  "known_mules_count": 5,
  "suspicious_devices_count": 3,
  "generated_at": "2026-09-28T11:01:58.584000+00:00"
}
```

---

### 3.3 List Alerts
* **`GET /api/alerts`**
* **Query Parameters:**
  * `severity` (string): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  * `status` (string): Investigation status.
  * `customer_id` (string): Filter by customer ID.
  * `transaction_id` (string): Filter by transaction ID.
  * `rule_code` (string): e.g. `R-ATO-05`.
  * `rule_category` (string): e.g. `Credential_ATO`.
  * `date_from`, `date_to` (string, ISO 8601).
  * `sort_by` (string): `created_at`, `risk_score`, `severity`, `customer_id`.
  * `sort_order` (string): `ASC` or `DESC`.
  * `page`, `page_size` (pagination).
* **Response (200 OK):** Returns `PaginatedResponse[AlertSummary]`.

---

### 3.4 Get Alert Detail
* **`GET /api/alerts/{alert_id}`**
* **Path Parameters:** `alert_id` (string, e.g. `ALT-00001`).
* **Response (200 OK):** Returns `AlertDetail` including `alert`, `customer`, `account`, `transaction`, `signals`, and `related_entities`.
* **Errors:** `404 Not Found` if `alert_id` is missing.

---

### 3.5 List Transactions
* **`GET /api/transactions`**
* **Query Parameters:**
  * `customer_id`, `account_id`, `beneficiary_id`, `device_id`.
  * `channel`: `IllicoCash_App`, `RawbankOnline_Web`, `ATM_Cardless`, `Agency_Express_POS`, `SWIFT_Wire`.
  * `transaction_type`: `P2P_Transfer`, `Merchant_Payment`, `Cardless_CashOut`, etc.
  * `currency`: `CDF` or `USD`.
  * `status`: `Completed`, `Pending_Review`, `Blocked_Declined`.
  * `min_amount_usd`, `max_amount_usd` (float).
  * `date_from`, `date_to` (string, ISO 8601).
  * `sort_by`: `timestamp`, `amount_usd`, `amount`.
  * `sort_order`: `ASC` or `DESC`.
* **Response (200 OK):** Returns `PaginatedResponse[TransactionSummary]`.

---

### 3.6 Get Transaction Detail
* **`GET /api/transactions/{transaction_id}`**
* **Path Parameters:** `transaction_id` (string, e.g. `TXN-00801`).
* **Response (200 OK):** Returns `TransactionDetail` with customer profile, debited account, receiving beneficiary, hardware device, recent authentication activities, recorded fraud signals, alerts, fresh deterministic evaluation, and 3-tier evidence packet.

---

### 3.7 Customer 360 Dossier
* **`GET /api/customers/{customer_id}`**
* **Path Parameters:** `customer_id` (string, e.g. `CUS-00014`).
* **Response (200 OK):** Returns `CustomerDossier`:
  * `customer`: Full profile and KYC level.
  * `accounts`: Linked checking, savings, or float accounts with balances.
  * `activity_summary`: Lifetime volume, average, and peak metrics.
  * `recent_transactions`: 10 latest transactions.
  * `behavioural_baseline`: Profile from `behavioural_baselines`.
  * `devices`: Hardware enrolled or used.
  * `beneficiaries`: Top recipient entities.
  * `recent_auth_events`: 10 latest logins, OTPs, and challenges.
  * `risk`: Alert history, signals, peak risk score.
  * `relationships`: Shared device co-users and shared beneficiary links.

---

### 3.8 Entity Graph Relationships
* **`GET /api/entities/{entity_type}/{entity_id}/relationships`**
* **Path Parameters:**
  * `entity_type`: `customer`, `account`, `transaction`, `device`, `beneficiary`, `alert`.
  * `entity_id`: e.g. `CUS-00014`, `DEV-00127`, `BEN-00088`.
* **Response (200 OK):**
```json
{
  "entity_type": "customer",
  "entity_id": "CUS-00014",
  "root_entity": { "customer_id": "CUS-00014", "full_name": "Christelle Mutombo" },
  "total_relationships": 54,
  "relationships": [
    {
      "source_type": "customer",
      "source_id": "CUS-00014",
      "relationship": "OWNS_ACCOUNT",
      "target_type": "account",
      "target_id": "ACC-00028",
      "target_label": "Current_Checking (USD)",
      "direction": "outgoing",
      "details": { "balance": 82264.0 }
    }
  ],
  "second_hop_links": [
    {
      "source_type": "device",
      "source_id": "DEV-00127",
      "relationship": "ALSO_USED_BY",
      "target_type": "customer",
      "target_id": "CUS-00088",
      "target_label": "...",
      "direction": "outgoing",
      "details": { "pivot_device": "Tecno Spark 10" }
    }
  ]
}
```

---

### 3.9 Deterministic Evaluation
* **`POST /api/evaluate/transaction/{transaction_id}`**
* **Response (200 OK):**
```json
{
  "transaction_id": "TXN-00801",
  "customer_id": "CUS-00014",
  "is_flagged": true,
  "risk_score": 100,
  "severity": "CRITICAL",
  "scenario_type": "ATO_DRAIN",
  "reason_summary": "Account Takeover + Drain pattern: password reset followed by high-value transfer on novel unverified device.",
  "signals": [ ... ],
  "scoring_breakdown": [ ... ],
  "evidence_packet": { ... }
}
```

* **`POST /api/evaluate/customer/{customer_id}?limit=10`**
* **Response (200 OK):** Evaluates customer's recent transactions and aggregates peak risk score, overall severity, contributing signals, and deterministic summary.

---

### 3.10 3-Tier Forensic Evidence Packet
* **`GET /api/evidence/{transaction_id}`**
* **Response (200 OK):**
```json
{
  "transaction_id": "TXN-00801",
  "customer_id": "CUS-00014",
  "generated_at": "2026-09-28T11:01:58.758170+00:00",
  "tier_1_exact_data": {
    "transaction": { ... },
    "source_account": { ... },
    "customer": { ... },
    "device": { ... },
    "beneficiary": { ... }
  },
  "tier_2_calculated": {
    "composite_risk_score": 100,
    "severity": "CRITICAL",
    "scenario_type": "ATO_DRAIN"
  },
  "tier_3_retrieved_evidence": {
    "behavioural_baseline": { ... },
    "recent_auth_events": [ ... ],
    "prior_device_history": [ ... ]
  },
  "tier_4_ai_reasoning": null
}
```

---

### 3.11 Unified Cross-Entity Search
* **`GET /api/search?q={query}&limit=25`**
* **Query Parameters:** `q` (string, required, min 1 char), `limit` (int, default 25).
* **Response (200 OK):**
```json
{
  "query": "CUS-00014",
  "total_results": 1,
  "results": [
    {
      "entity_type": "customer",
      "entity_id": "CUS-00014",
      "title": "Christelle Mutombo",
      "subtitle": "SME • Lubumbashi",
      "match_field": "customer_id",
      "match_value": "CUS-00014",
      "details": {
        "segment": "SME",
        "city": "Lubumbashi",
        "phone": "+243818301725",
        "email": "christelle.mutombo83@rawbank-synthetic.cd"
      }
    }
  ]
}
```
