# Rawbank Sentient Fraud Intelligence Platform
## Phase 5: Semantic Retrieval & Evidence API Reference Manual

**API Version:** 1.0.0 (Phase 5 Enhanced)  
**Base URL:** `http://127.0.0.1:8000`  
**OpenAPI Interactive UI:** `http://127.0.0.1:8000/docs`  
**OpenAPI JSON Schema:** `http://127.0.0.1:8000/openapi.json`  

---

## 1. Overview & Protocol Conventions

The Phase 5 Retrieval & Evidence API provides grounded data access for the future Fraud Investigation Copilot and Command Centre.
* **Deterministic Ground Truth:** All evidence traces strictly to verified SQLite records via field-level provenance.
* **Zero Hallucination:** Nonexistent records return explicit `UNKNOWN_ENTITY` evidence gaps rather than speculative answers.
* **Explainable Ranking:** Every ranked search result includes its `relevance_score` $[0.0 - 1.0]$ and the specific deterministic reasons driving that score.

---

## 2. Endpoints Summary

| Method | Endpoint Path | Tags | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/retrieval/query` | Semantic Retrieval | Primary natural language / structured retrieval engine with standardized evidence packet generation. |
| `GET` | `/api/search` | Unified Search | Multi-entity hybrid search supporting exact lookups and keyword/filter matching. |
| `GET` | `/api/entities/{entity_type}/{entity_id}/evidence` | Entities | Standardized grounded evidence packet for any banking entity. |
| `GET` | `/api/entities/{entity_type}/{entity_id}/related` | Entities | Controlled 1-hop and 2-hop relationship graph expansion. |
| `GET` | `/api/alerts/{alert_id}/evidence` | Alerts | Forensic evidence packet for a specific fraud alert. |
| `GET` | `/api/transactions/{transaction_id}/evidence` | Transactions | Grounded evidence packet for a transaction. |
| `GET` | `/api/retrieval/documents/{document_id}` | Semantic Retrieval | Direct access to a normalized retrieval document. |

---

## 3. Endpoint Specifications

### 3.1 POST /api/retrieval/query
* **Purpose:** Primary entrypoint for forensic investigation questions and multi-vector search queries.
* **Request Body:**
```json
{
  "query": "Why was customer CUS-00014 flagged?",
  "entity_type": "customer",
  "entity_id": "CUS-00014",
  "filters": {
    "severity": "CRITICAL"
  },
  "limit": 10,
  "include_evidence_packet": true,
  "relationship_depth": 2
}
```

* **Response (200 OK):**
```json
{
  "query": "Why was customer CUS-00014 flagged?",
  "intent": "INVESTIGATE_ENTITY",
  "total_retrieved": 5,
  "resolved_entities": [
    {
      "entity_type": "customer",
      "entity_id": "CUS-00014",
      "canonical_id": "CUS-00014",
      "confidence": 1.0,
      "matching_method": "exact_id",
      "matched_text": "CUS-00014",
      "is_ambiguous": false,
      "candidates": [],
      "details": {
        "customer_id": "CUS-00014",
        "full_name": "Christelle Mutombo",
        "customer_segment": "SME",
        "registered_city": "Lubumbashi",
        "risk_category": "High"
      }
    }
  ],
  "results": [
    {
      "document": {
        "document_id": "doc_cus_CUS-00014",
        "entity_type": "customer",
        "entity_id": "CUS-00014",
        "title": "Customer CUS-00014: Christelle Mutombo (SME)",
        "source_table": "customers",
        "source_id": "CUS-00014",
        "text": "Customer Dossier: Christelle Mutombo (ID: CUS-00014)...",
        "structured_fields": { ... },
        "metadata": { ... }
      },
      "relevance_score": 0.85,
      "relevance_reasons": [
        "exact_identifier_match(customer:CUS-00014)",
        "primary_resolved_entity",
        "keyword_lexical_match(bm25=0.29)"
      ],
      "provenance": {
        "source_table": "customers",
        "source_id": "CUS-00014",
        "query_intent": "INVESTIGATE_ENTITY"
      }
    }
  ],
  "evidence_packet": {
    "query": "Why was customer CUS-00014 flagged?",
    "generated_at": "2026-09-28T20:39:54.164282+00:00",
    "target_entity": { ... },
    "resolved_entities": [ ... ],
    "exact_data": [ ... ],
    "calculated_information": [ ... ],
    "retrieved_evidence": [ ... ],
    "counter_evidence": [ ... ],
    "relationships": [ ... ],
    "evidence_gaps": [ ... ],
    "source_references": [ ... ],
    "deterministic_summary": "Forensic Evidence Summary for CUSTOMER CUS-00014..."
  }
}
```

* **Error Cases:**
  - `422 Unprocessable Content`: `limit` not in range $[1, 100]$ or empty query.

---

### 3.2 GET /api/search
* **Purpose:** Fast, multi-entity search supporting exact lookups, prefix matching, and hybrid attribute filtering.
* **Query Parameters:**
  - `q` (string, required): Search query string (e.g. `CUS-00014`, `impossible travel`, `iPhone`, `Kinshasa`).
  - `entity_type` (string, optional): Filter by entity: `customer`, `account`, `transaction`, `device`, `beneficiary`, `alert`.
  - `severity` (string, optional): Filter by severity: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - `scenario` (string, optional): Filter by scenario: `ATO_DRAIN`, `IMPOSSIBLE_TRAVEL`, etc.
  - `limit` (integer, default `25`, min `1`, max `100`): Maximum results to return.
* **Response (200 OK):**
```json
{
  "query": "impossible travel",
  "total_results": 2,
  "results": [
    {
      "entity_type": "alert",
      "entity_id": "ALT-00020",
      "title": "Alert ALT-00020: [HIGH] IMPOSSIBLE_TRAVEL (Score: 82)",
      "subtitle": "Fraud Alert Dossier ALT-00020: Triggered on Transaction TXN-00820...",
      "match_field": "hybrid_index",
      "match_value": "impossible travel",
      "details": {
        "alert_id": "ALT-00020",
        "scenario_type": "IMPOSSIBLE_TRAVEL",
        "severity": "HIGH",
        "composite_risk_score": 82
      },
      "relevance_score": 0.65,
      "relevance_reasons": [
        "scenario_match(IMPOSSIBLE_TRAVEL)",
        "high_severity_alert",
        "keyword_lexical_match(bm25=1.85)"
      ]
    }
  ]
}
```

---

### 3.3 GET /api/entities/{entity_type}/{entity_id}/evidence
* **Purpose:** Constructs standardized forensic evidence packet for ANY banking entity.
* **Path Parameters:**
  - `entity_type`: `customer`, `account`, `transaction`, `device`, `beneficiary`, `alert`.
  - `entity_id`: Target entity primary key (e.g. `CUS-00014`, `DEV-00125`, `BEN-00050`).
* **Response (200 OK):** Standardized `StandardEvidencePacket` containing:
  - `exact_data`: Ledger rows with field-level provenance.
  - `calculated_information`: Formulas, cluster counts, risk scores.
  - `retrieved_evidence`: Baselines, auth logs, rule signals.
  - `counter_evidence`: Mitigating factors for corporate/trusted profiles.
  - `relationships`: 1-hop and 2-hop edges.
  - `evidence_gaps`: Explicit missing evidence items.
  - `source_references`: Unique database records cited.
* **Error Cases:**
  - `400 Bad Request`: Unsupported entity type (e.g. `spaceship`).
  - `404 Not Found`: Nonexistent identifier (e.g. `CUS-99999`).

---

### 3.4 GET /api/entities/{entity_type}/{entity_id}/related
* **Purpose:** Controlled relationship graph traversal with bounded depth.
* **Query Parameters:**
  - `max_depth` (integer, default `2`, min `1`, max `3`): Graph traversal depth.
  - `limit` (integer, default `20`, min `1`, max `100`): Maximum related items per category.
* **Response (200 OK):**
```json
{
  "entity_type": "device",
  "entity_id": "DEV-00125",
  "canonical_id": "DEV-00125",
  "max_depth": 2,
  "total_relationships": 4,
  "direct_relationships": [
    {
      "source_type": "device",
      "source_id": "DEV-00125",
      "relationship": "USED_BY_PRIMARY",
      "target_type": "customer",
      "target_id": "CUS-00031",
      "target_label": "Alain Kavugho"
    }
  ],
  "second_hop_relationships": [
    {
      "source_type": "device",
      "source_id": "DEV-00125",
      "relationship": "ALSO_USED_BY",
      "target_type": "customer",
      "target_id": "CUS-00032",
      "target_label": "Baudouin Yav"
    }
  ],
  "summary": "Entity DEVICE DEV-00125 has 1 direct 1-hop connections and 3 2-hop shared cluster connections within max depth 2."
}
```

* **Error Cases:**
  - `400 Bad Request`: Unsupported entity type.
  - `404 Not Found`: Nonexistent entity ID.

---

### 3.5 GET /api/alerts/{alert_id}/evidence
* **Purpose:** Dedicated evidence packet assembly for a fraud alert dossier.
* **Path Parameters:**
  - `alert_id` (string): Primary alert key (e.g. `ALT-00001`).
* **Response (200 OK):** Full `StandardEvidencePacket` encompassing underlying transaction, customer context, fired signals, and mitigating factors.
* **Error Cases:**
  - `404 Not Found`: Nonexistent alert ID (e.g. `ALT-99999`).

---

### 3.6 GET /api/retrieval/documents/{document_id}
* **Purpose:** Direct access to normalized grounded documents in the retrieval index.
* **Path Parameters:**
  - `document_id` (string): Unique document key (e.g. `doc_cus_CUS-00014`, `doc_txn_TXN-00801`).
* **Response (200 OK):**
```json
{
  "document_id": "doc_cus_CUS-00014",
  "entity_type": "customer",
  "entity_id": "CUS-00014",
  "title": "Customer CUS-00014: Christelle Mutombo (SME)",
  "source_table": "customers",
  "source_id": "CUS-00014",
  "timestamp": "2024-03-12T08:15:00",
  "text": "Customer Dossier: Christelle Mutombo (ID: CUS-00014)...",
  "structured_fields": { ... },
  "metadata": { ... }
}
```

* **Error Cases:**
  - `404 Not Found`: Nonexistent document ID.
