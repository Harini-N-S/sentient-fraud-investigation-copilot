# Rawbank Sentient Fraud Intelligence Platform
## Phase 6: Sentient Fraud Investigation Copilot API Reference

**Status:** Completed (Phase 6 Verified)  
**Base URL:** `http://127.0.0.1:8000/api/copilot`  
**Authentication:** Server-side API key management (Client auth deferred to production gateway)  
**Content-Type:** `application/json`  

---

## 1. Overview & Architectural Principles

The Phase 6 Investigation Copilot API exposes AI-assisted fraud investigation capabilities grounded in the **Phase 5 Semantic Retrieval Layer** and **Phase 3 Deterministic Fraud Rules Engine**.

### Guarantees
- **Evidence Before Intelligence:** All factual claims derive strictly from `synthetic_bank.db`.
- **Deterministic Risk Score Preservation:** The official fraud score (`0-100`) and severity level (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NONE`) are deterministically fixed by Phase 3 rules and cannot be altered by the LLM.
- **Strict Provenance:** Citations (`[Source: <ID>]`) are validated; ungrounded citations are stripped.
- **Balanced Forensic Evaluation:** Counter-evidence is surfaced for legitimate anomalies to mitigate false positives.

---

## 2. API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/copilot/investigate` | Full investigation pipeline for natural-language analyst questions. |
| `POST` | `/api/copilot/explain-alert/{alert_id}` | Targeted forensic explanation of why an alert was triggered. |
| `POST` | `/api/copilot/explain-transaction/{transaction_id}` | Forensic review of preceding authentications, devices, and deviations for a transaction. |
| `POST` | `/api/copilot/explain-customer/{customer_id}` | Comprehensive risk profile, baseline deviations, and network connections for a customer. |

---

## 3. Endpoints Detail

### 3.1 POST `/api/copilot/investigate`

Executes the complete 12-step grounded investigation pipeline.

#### Request Schema (`CopilotInvestigateRequest`)
```json
{
  "question": "Why was customer CUS-00014 flagged?",
  "session_id": "sess_analyst_001",
  "entity_type": null,
  "entity_id": null,
  "use_mock": false
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | Yes | Analyst question (min length 3). |
| `session_id` | string | No | Conversational session ID to maintain context across questions. |
| `entity_type` | string | No | Explicit entity override (`customer`, `transaction`, `alert`, `device`, `beneficiary`). |
| `entity_id` | string | No | Explicit entity identifier override (e.g. `CUS-00014`). |
| `use_mock` | boolean | No | Force use of mock adapter (defaults to `COPILOT_USE_MOCK` env setting). |

#### Response Schema (`CopilotInvestigationResponse`)
```json
{
  "question": "Why was customer CUS-00014 flagged?",
  "session_id": "sess_analyst_001",
  "resolved_entities": [
    {
      "entity_type": "customer",
      "canonical_id": "CUS-00014",
      "confidence": 1.0,
      "is_ambiguous": false,
      "candidates": []
    }
  ],
  "summary": "Forensic investigation completed for CUS-00014. Official deterministic risk score is 98/100 (CRITICAL). Key indicators: Credential Password Reset Followed by Outbound Transfer [Source: SIG-00001]; Unverified Novel Device [Source: SIG-00002].",
  "risk_assessment": {
    "severity": "CRITICAL",
    "risk_score": 98,
    "confidence": 0.95
  },
  "supporting_evidence": [
    {
      "source_id": "TXN-00801",
      "source_table": "transactions",
      "statement": "Outbound P2P transfer of $4,800.00 USD via IllicoCash_App in Goma",
      "citation": "[Source: TXN-00801]"
    },
    {
      "source_id": "SIG-00001",
      "source_table": "fraud_signals",
      "statement": "Password reset occurred 15 minutes prior on newly enrolled device DEV-00127",
      "citation": "[Source: SIG-00001]"
    }
  ],
  "counter_evidence": [],
  "behavioural_deviation": [
    "Transfer amount ($4,800 USD) is 18x customer median ($260 USD) [Source: SIG-00003]"
  ],
  "related_activity": [
    "Connected device DEV-00127: unverified hardware signature"
  ],
  "evidence_gaps": [],
  "investigation_next_steps": [
    "Inspect recent authentication logs and credential reset audit logs [auth_activity].",
    "Contact customer via registered voice channel to confirm authorized device enrollment."
  ],
  "escalation_recommendation": "Available evidence strongly supports immediate escalation to Level 2 Senior Fraud Analyst. Official risk score is 98/100 (CRITICAL). Immediate account restriction recommended.",
  "source_references": [
    {
      "source_id": "CUS-00014",
      "source_table": "customers",
      "description": "Customer Profile"
    },
    {
      "source_id": "TXN-00801",
      "source_table": "transactions",
      "description": "Trigger Transaction"
    }
  ],
  "provenance_validated": true,
  "invalid_citations_removed": [],
  "ambiguity_detected": false,
  "unknown_entity_detected": false,
  "insufficient_evidence_detected": false,
  "model_used": "llama-3.3-70b-versatile",
  "processing_time_ms": 245.3,
  "created_at": "2026-09-28T21:00:00Z"
}
```

---

### 3.2 POST `/api/copilot/explain-alert/{alert_id}`

Targeted forensic explanation for a specific alert case.

#### Path Parameters
- `alert_id` (string, required): e.g. `ALT-00001` or `ALT-00027`.

#### Query Parameters
- `session_id` (string, optional): Conversation session ID.
- `use_mock` (boolean, optional): Force mock adapter.

#### Sample Request
```http
POST /api/copilot/explain-alert/ALT-00027?use_mock=true HTTP/1.1
Host: 127.0.0.1:8000
```

#### Sample Response (Legitimate Anomaly / False Positive Mitigation)
```json
{
  "question": "What evidence supports alert ALT-00027 and why was it flagged?",
  "summary": "Forensic review of alert ALT-00027 indicates high-value commercial transaction. Official score: 28/100 (LOW).",
  "risk_assessment": {
    "severity": "LOW",
    "risk_score": 28,
    "confidence": 0.85
  },
  "supporting_evidence": [
    {
      "source_id": "TXN-00751",
      "source_table": "transactions",
      "statement": "Commercial payment of $68,898.00 USD via RawbankOnline_Web",
      "citation": "[Source: TXN-00751]"
    }
  ],
  "counter_evidence": [
    {
      "source_id": "CUS-00010",
      "source_table": "customers",
      "statement": "Customer profile is registered Corporate entity with verified commercial baseline",
      "citation": "[Source: CUS-00010]"
    },
    {
      "source_id": "DEV-00010",
      "source_table": "devices",
      "statement": "Transaction originated from trusted, enrolled Apple MacBook Pro M2",
      "citation": "[Source: DEV-00010]"
    }
  ],
  "escalation_recommendation": "Available evidence does NOT support fraud escalation. The alert is classified as LOW (Score: 28/100) and is strongly mitigated by legitimate operational counter-evidence. Recommended for closure as a legitimate anomaly / false positive."
}
```

---

### 3.3 POST `/api/copilot/explain-transaction/{transaction_id}`

Forensic explanation of preceding authentications, devices, and deviations for a transaction.

#### Path Parameters
- `transaction_id` (string, required): e.g. `TXN-00801`.

#### Sample Request
```http
POST /api/copilot/explain-transaction/TXN-00801?use_mock=true HTTP/1.1
Host: 127.0.0.1:8000
```

---

### 3.4 POST `/api/copilot/explain-customer/{customer_id}`

Forensic review of a customer's linked accounts, devices, and risk baseline.

#### Path Parameters
- `customer_id` (string, required): e.g. `CUS-00014` or `CUS-00003`.

#### Sample Request
```http
POST /api/copilot/explain-customer/CUS-00003?use_mock=true HTTP/1.1
Host: 127.0.0.1:8000
```

#### Sample Response (Clean Normal Customer / Insufficient Evidence)
```json
{
  "question": "Why was customer CUS-00003 flagged?",
  "summary": "Investigation of CUS-00003: There is insufficient evidence in the available synthetic dataset to establish suspicious activity. No active fraud alerts, high-risk signals, or security incidents are recorded for this entity.",
  "risk_assessment": {
    "severity": "NONE",
    "risk_score": 0,
    "confidence": 0.95
  },
  "supporting_evidence": [],
  "counter_evidence": [
    {
      "source_id": "CUS-00003",
      "source_table": "alerts",
      "statement": "Zero fraud alerts or suspicious incident reports exist in the synthetic database.",
      "citation": "[Source: CUS-00003]"
    }
  ],
  "evidence_gaps": [
    {
      "gap_type": "NO_RELATED_ALERTS",
      "description": "No alert records or suspicious incident reports exist for entity CUS-00003.",
      "impact": "No evidence of fraudulent activity identified."
    }
  ],
  "escalation_recommendation": "Do not escalate. Available evidence confirms normal banking profile with no suspicious indicators."
}
```

---

## 4. Multi-Turn Conversational Context Example

Analyst conversation flow maintaining context via `session_id`:

```http
# Turn 1: Initial Investigation
POST /api/copilot/investigate
{
  "question": "Why was customer CUS-00014 flagged?",
  "session_id": "investigation_session_42"
}
--> Responds with ATO details for CUS-00014 and trigger transaction TXN-00801.

# Turn 2: Follow-up referencing "that"
POST /api/copilot/investigate
{
  "question": "What happened before that?",
  "session_id": "investigation_session_42"
}
--> Copilot resolves "that" to TXN-00801 and retrieves preceding password reset and device enrollment.
```

---

## 5. Error Handling & HTTP Status Codes

The API returns standardized JSON error responses:

| HTTP Status | Error Code | Description |
|---|---|---|
| `400 Bad Request` | `HTTP_400` | Invalid request parameter or malformed query. |
| `422 Unprocessable` | `VALIDATION_ERROR` | Schema validation error (e.g. query too short). |
| `502 Bad Gateway` | `GROQ_API_ERROR` | Groq API returned an upstream error or malformed payload. |
| `503 Service Unavailable` | `GROQ_NOT_CONFIGURED` | `GROQ_API_KEY` is missing in live mode. |
| `504 Gateway Timeout` | `GROQ_TIMEOUT` | Groq API request exceeded `GROQ_TIMEOUT_SECONDS`. |
| `500 Internal Error` | `INTERNAL_SERVER_ERROR` | Server exception without leaking internal stack traces. |

#### Error Response Format
```json
{
  "detail": "GROQ_API_KEY environment variable is not configured. Please configure GROQ_API_KEY in .env or run tests using mock adapter.",
  "error_code": "HTTP_503",
  "timestamp": "2026-09-28T21:00:00Z"
}
```
