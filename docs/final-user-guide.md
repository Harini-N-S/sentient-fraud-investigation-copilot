# Sentient Fraud Intelligence Platform — Operator & User Guide
**Rawbank Democratic Republic of Congo**
**Version:** 1.0.0 (Production-Hardened Demonstration Build)

---

## 1. Quick Start & Execution

### 1.1 Prerequisites
- **Python:** 3.11+ (Python 3.14 verified)
- **Node.js:** v18+ (Node 20+ recommended)
- **Database:** Pre-seeded SQLite database located at `database/synthetic_bank.db`.

### 1.2 Starting the Backend API Server
Open a terminal in the project root:
```bash
# Start FastAPI Uvicorn Server on port 8000
py -3.14 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- **Backend API:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/api/health`

### 1.3 Starting the Frontend Application
Open a second terminal in `frontend/`:
```bash
cd frontend
npm install
npm run dev
```
- **Web Application URL:** `http://localhost:5173` (or port indicated by Vite)

---

## 2. Navigating the Sentient Command Centre

The **Sentient Command Centre** (`/`) is the primary operational dashboard for Level 1 & Level 2 fraud analysts.

### Key Sections:
1. **Header Bar:** Shows live system health, connection status, authoritative customer/alert counts, and **dual-timezone operational clocks** (Kinshasa UTC+1 / Lubumbashi UTC+2).
2. **Executive KPI Cards:** Immediate visibility into total transaction volume ($2.31M USD), flagged fraud volume, critical alert count, and identified mule funnels.
3. **Operational Widgets:**
   - **Severity Distribution:** Visual breakdown across CRITICAL, HIGH, MEDIUM, and LOW alerts.
   - **Scenario Breakdown:** Real-time distribution across ATO, shared device syndicates, mule funnels, impossible travel, and structuring.
   - **Top Mule Aggregators:** Ranked counterparty beneficiaries with high incoming distinct-sender concentration.
4. **Real-Time Incident Queue:** Paginated, filterable table of all 140 alerts. Supports filtering by severity, status, and scenario type.

---

## 3. Alert Triage & Entity Inspection Workflow

### 3.1 Inspecting an Alert
1. In the Incident Queue, click any alert row (e.g. `ALT-00001`).
2. The **Forensic Inspection Drawer** opens on the right side of the screen.
3. Review:
   - **Deterministic Risk Score:** Preserved score (0–100) and severity rating.
   - **Rule Violations:** Specific fraud signals triggered with confidence scores.
   - **Transaction Ledger Details:** Channel, amount, timestamp, and location.
   - **Customer Context:** KYC tier, segment, registered city.

### 3.2 Topological Drill-Down
From the inspection drawer or alert detail view, click on any connected entity:
- **Customer ID** (e.g. `CUS-00014`): Opens comprehensive customer dossier, accounts, 30-day behavioral baselines, and past transaction history.
- **Device ID** (e.g. `DEV-00125`): Opens hardware specs, trust status, and the **interactive relationship graph** showing all co-users sharing the device.
- **Beneficiary ID** (e.g. `BEN-00088`): Opens incoming payment aggregation, distinct sending customers, and mule syndicate flags.

---

## 4. Global Omnibox Search

Press `Alt + K` (or `Cmd + K` on macOS) anywhere in the application to open the **Global Search Omnibox**:
- Search by **Entity ID:** `CUS-00014`, `TXN-00801`, `ALT-00001`, `DEV-00125`, `BEN-00088`.
- Search by **Customer Name:** `Christelle Mutombo`, `Blaise Kavugho`.
- Search by **Scenario or Keyword:** `Account takeover`, `Goma`, `IllicoCash`, `impossible travel`.

Selecting a result navigates directly to the target record without losing your current investigation context.

---

## 5. Using the Sentient Fraud Investigation Copilot

The **Fraud Investigation Copilot** (`/copilot`) provides an evidence-grounded AI co-investigator.

### 5.1 Investigation Capabilities
- **Explain Alert:** Explains why an alert was triggered using exact ledger facts.
- **Correlate Syndicate Links:** Discovers non-obvious relationships across devices, IPs, and beneficiaries.
- **Evaluate Counter-Evidence:** Verifies whether an anomaly can be explained as legitimate corporate or retail activity.
- **Recommend Action:** Synthesizes actionable next steps and escalation advice.

### 5.2 Example Investigation Questions
| Goal | Example Query |
|---|---|
| **Alert Explanation** | *"Why was alert ALT-00001 triggered?"* |
| **Syndicate Discovery** | *"Which customers are connected to device DEV-00125 and why is it relevant?"* |
| **Mule Analysis** | *"Who else sends money to beneficiary BEN-00088 and what pattern emerges?"* |
| **False-Positive Evaluation** | *"What evidence could explain this activity as a legitimate corporate anomaly?"* |
| **Behavioral Profiling** | *"Does the transaction for CUS-00014 deviate from historical baseline?"* |
| **Adversarial / Hallucination Test** | *"Which device did CUS-00014 use from Paris?"* *(System rejects ungrounded premise)* |

---

## 6. Understanding Evidence Packets & Source References

Every factual claim made by the Copilot is grounded in a **Standardized Forensic Evidence Packet**:
- **`[Source: TXN-00801]`**: Directly references a row in the `transactions` table.
- **`[Source: ALT-00001]`**: References an authoritative alert record and deterministic score.
- **`[Source: DEV-00125]`**: References verified device hardware and IP audit logs.
- **`Evidence Gaps`**: Explicitly documented missing records (e.g. unverified SIM swaps, ambiguous entity names).

Clicking any source badge in the Copilot interface scrolls to and highlights the underlying ledger record.

---

## 7. Groq LLM Configuration & Deterministic Fallback

The Copilot supports both live cloud inference via Groq and zero-configuration offline execution via a deterministic mock adapter.

### 7.1 Offline Mock Adapter (Default / Automated Testing)
If no `GROQ_API_KEY` is configured, or if `COPILOT_USE_MOCK=true` is set:
- The platform uses `backend/app/llm/mock_adapter.py`.
- Generates 100% grounded responses covering all 8 mandatory forensic sections using deterministic data extraction.
- Zero network latency, zero token costs, and 100% reproducible test outputs.

### 7.2 Enabling Live Groq Llama 3.3 70B
1. Obtain an API key from [console.groq.com/keys](https://console.groq.com/keys).
2. Create a `.env` file in the project root (copied from `.env.example`):
   ```env
   GROQ_API_KEY=gsk_your_actual_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   COPILOT_USE_MOCK=false
   ```
3. Restart the backend server. The Copilot will automatically use live Groq inference while maintaining strict deterministic score preservation.

---

## 8. Synthetic Data Disclaimer

> [!IMPORTANT]
> **Synthetic Banking Environment Notice:**
> All customer identities, account balances, transaction records, mobile numbers, and device identifiers are **100% synthetically generated** for demonstration and technical validation purposes.
> No real customer data, internal Rawbank operational journals, or personally identifiable information (PII) is contained within this platform.
