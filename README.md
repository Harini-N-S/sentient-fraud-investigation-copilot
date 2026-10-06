# Rawbank Sentient Fraud Investigation Copilot

**AI-Assisted Evidence-Grounded Forensic Investigation Platform**  
*System 2 of the Rawbank Sentient Fraud Intelligence Platform*

---

## 1. System Overview & Purpose

The **Sentient Fraud Investigation Copilot** is a dedicated forensic investigation environment designed for deep inquiry, multi-entity correlation, causal explanation, next-step recommendations, and case escalation in the Democratic Republic of the Congo (DRC) banking sector.

### Core Philosophy:
* **The LLM is NOT the database**: Natural language questions never query the LLM's parametric memory for facts. All entity data and transaction history derive strictly from the verified local synthetic banking database.
* **Evidence-Grounded Reasoning**: Every statement and conclusion must be backed by a verified entity citation `[Source: ID]`. Hallucinated or unverifiable citations are stripped automatically.
* **Deterministic Risk Scores**: The risk score is mathematically computed by the 11 registered forensic rules engine and cannot be overridden by LLM output.
* **Balanced Forensic Objectivity**: Every investigation synthesizes supporting fraud indicators alongside counter-evidence (mitigating context) and explicit evidence blindspots.

---

## 2. Assignment Use Case & Primary Workflow

* **Primary Use Case**: Forensic Fraud Investigation, Hypothesis Evaluation, and Escalation Synthesis
* **Investigative Workflow**:
  ```
  Investigate  ──►  Correlate  ──►  Explain  ──►  Recommend  ──►  Escalate
       │                 │             │              │              │
  Natural Language  Multi-hop Graph  Grounded   Actionable Next  Formal Risk Tier
     Inquiry        & Device Links   Reasoning       Steps          Handoff
  ```

---

## 3. Technology Stack

* **Frontend**: React 19, TypeScript, Vite, TailwindCSS (Phase A Rawbank Design System), Lucide Icons
* **Backend**: FastAPI, Python 3.14, Uvicorn, SQLite
* **Retrieval & Evidence**: Entity resolution, 3-tier grounded evidence dossiers, citation validation
* **AI & Reasoning Layer**: Groq LLM integration (`llama-3.3-70b-versatile`) with deterministic offline fallback adapter
* **Design System**: Official Rawbank Brand Identity (`#FCB900` Selective Yellow, `#0E131B` Obsidian, typography, and leopard emblem)

---

## 4. Retained Functional Scope

* **Investigation Copilot Console**: Natural-language conversational workspace with session persistence and prompt history.
* **Forensic Case Templates**: Pre-configured DRC fraud inquiry scenarios (Account Takeover, Mule Funnel, Structuring / Smurfing, Impossible Travel, Dormant Revival, Device Sharing).
* **Multi-Turn Session Continuity**: Context-aware follow-up queries that maintain entity memory without hallucinating unobserved facts.
* **Citation-Linked Slide-Over Drawer**: Clicking any `[Source: ID]` badge immediately displays the complete 3-tier evidence dossier and graph relationship network.
* **Structured Response Sections**:
  * Executive Investigation Summary
  * Authoritative Deterministic Risk Score & Severity Badge
  * Supporting Evidence (Fraud Indicators with Source Badges)
  * Counter-Evidence (Mitigating Context with Source Badges)
  * Behavioral Baseline Deviations (Observed vs. Historical Multipliers)
  * Evidence Gaps & Data Blindspots (Explicit Investigation Uncertainties)
  * Actionable Next Steps & Required Investigator Inquiries
  * Escalation Recommendation & Assigned Analyst Tier

---

## 5. Synthetic Data Disclaimer

> **ANALYTICAL SAFETY BOUNDARY**:  
> This platform operates exclusively on a **100% synthetic research database** generated for demonstration, testing, and evaluation purposes. **No real Rawbank customer data, account numbers, or real transaction records are contained or accessed by this system.** All names, account identifiers, phone numbers, and device fingerprints are procedurally generated mathematical constructs.

---

## 6. How to Run

### Backend API Server
```bash
# From repository root
py -3.14 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
* **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
* **Copilot Investigation**: [http://127.0.0.1:8000/api/copilot/investigate](http://127.0.0.1:8000/api/copilot/investigate)

### Frontend Web Application
```bash
# Navigate to frontend directory
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
* **Web UI**: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

---

## 7. Testing & Verification

### Run Backend Unit Tests (85 tests)
```bash
py -3.14 -m unittest discover -s tests -p "test_*.py"
```

### Run Frontend Vitest Suite (12 tests)
```bash
cd frontend
npm run test
```

### Run Production Frontend Build
```bash
cd frontend
npm run build
```

---

## 8. Important Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | *(Optional)* | API key for Groq Cloud. If unset, deterministic mock adapter executes automatically |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | LLM model used for grounded forensic reasoning |
| `LLM_TEMPERATURE` | `0.1` | Low temperature for strictly grounded, deterministic reasoning |
| `APP_ENV` | `development` | Deployment environment mode |
| `HOST` | `127.0.0.1` | API bind address |
| `PORT` | `8000` | API bind port |
| `DB_PATH` | `database/synthetic_bank.db` | Local SQLite database file path |
