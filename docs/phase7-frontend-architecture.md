# Phase 7 — Sentient Command Centre & Fraud Investigation Copilot Frontend Architecture

## Executive Summary
Phase 7 delivers the enterprise-grade single-page application experience required by the *iTech Pre-Sales Technical Build Assignment*. It integrates **USE CASE 1: Sentient Command Centre** (Monitor → Prioritise → Analyse → Drill Down) and **USE CASE 2: Sentient Fraud Investigation Copilot** (Investigate → Correlate → Explain → Recommend → Escalate) into one unified, cohesive operational platform.

Built on React 19, Vite 8, and TypeScript with a maintainable, typed component hierarchy, the platform strictly consumes the live Phase 4–6 FastAPI backend endpoints with **zero frontend mock business data** and adheres strictly to the documented Rawbank enterprise design context (Obsidian `#0B0E14` base, Dark Slate `#121721` panels, Warm Amber `#F5A623` brand accents, and tabular numerals).

---

## 1. Technology Stack & Architectural Principles

| Layer | Technology | Rationale & Responsibility |
| :--- | :--- | :--- |
| **Framework** | React 19 + TypeScript (strict) | Component-driven architecture with compile-time type safety against backend API schemas. |
| **Build Tooling** | Vite 8 + ESNext bundler | Sub-second HMR, optimized production tree-shaking, and development proxy to FastAPI (`127.0.0.1:8000`). |
| **Styling & Design System** | Vanilla CSS Tokens (`styles/index.css`) | Maximum flexibility without heavy framework abstractions; implements Rawbank obsidian dark mode and typography. |
| **Iconography** | `lucide-react` | Clean, semantic banking and investigation icons with zero decorative clutter. |
| **Testing** | `vitest` + `@testing-library/react` + `jsdom` | 18 automated frontend unit and integration tests verifying triage, filters, drawers, evidence, and session preservation. |
| **API Client** | Centralized Service Layer (`services/api.ts`) | Strict typed contracts matching backend Pydantic models; handles pagination, errors, and live response normalization. |

### Architectural Invariants
1. **Evidence Before Intelligence:** Every risk score, severity badge, transaction amount, and customer profile is grounded in the backend SQLite synthetic database. No frontend analytics or hard-coded metrics are permitted.
2. **Deterministic Risk Authority:** The Copilot and Command Centre strictly display the Phase 3 deterministic risk scores ($0–100$) and official severity ratings. The LLM never invents or overrides risk scores.
3. **Provenance Transparency:** Every evidence item renders clickable `[Source: ID]` pills that open the exact entity dossier directly in the slide-over drawer.
4. **Single Synthetic Environment:** Both Use Case 1 (Command Centre) and Use Case 2 (Copilot) operate over the identical synthetic Rawbank DRC banking database (120 customers, 150 accounts, 1,000 transactions, 142 alerts).

---

## 2. Directory & Component Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.tsx             # Dual-timezone clocks (Kinshasa UTC+1, Lubumbashi UTC+2), status, search trigger
│   │   ├── Sidebar.tsx            # Primary navigation shell with dynamic critical alert counter badges
│   │   ├── MetricCard.tsx         # KPI metric card with semantic alert borders and tabular typography
│   │   ├── GlobalSearchModal.tsx  # Ctrl+K global entity finder querying /api/search across all 5 entity types
│   │   ├── EntityDrawer.tsx       # Slide-over inspector displaying core attributes, 4-tier evidence, and relationships
│   │   ├── EvidenceDossier.tsx    # 4-tier evidence packet (Exact Data, Calculated, Retrieved, Counter-Evidence, Gaps)
│   │   └── RelationshipTree.tsx   # Forensic 1-hop and 2-hop network graph rendering real entity links
│   ├── pages/
│   │   ├── CommandCentrePage.tsx  # USE CASE 1: Operational triage dashboard, live alert stream, mule funnels
│   │   ├── AlertsPage.tsx         # Comprehensive alert triage workspace with multi-dimensional filtering & sorting
│   │   ├── TransactionsPage.tsx   # Multi-currency ledger explorer (CDF/USD, channel, status, city)
│   │   ├── CustomersPage.tsx      # Customer risk directory (KYC tier, segment, risk profile, baselines)
│   │   └── CopilotPage.tsx        # USE CASE 2: Dedicated fraud investigation console with structured sections
│   ├── services/
│   │   └── api.ts                 # Centralized, strongly typed API client consuming Phase 4-6 endpoints
│   ├── types/
│   │   └── index.ts               # Domain types, evidence packets, copilot schemas, and search responses
│   ├── styles/
│   │   └── index.css              # Rawbank dark mode design tokens, badge utilities, and layout classes
│   ├── test/
│   │   ├── setup.ts               # Vitest environment setup and DOM polyfills
│   │   └── frontend.test.tsx      # 18 automated test suites verifying full frontend operational readiness
│   ├── App.tsx                    # Top-level shell integrating navigation, modals, drawer, and active view
│   └── main.tsx                   # React root entry point
├── package.json                   # Dependencies, build scripts, and test runner configuration
├── tsconfig.json                  # TypeScript project references
├── tsconfig.app.json              # Client compiler options
└── vite.config.ts                 # Vite server, /api proxy to FastAPI port 8000, and Vitest configuration
```

---

## 3. Core Page Workspaces

### 3.1 Sentient Command Centre (`CommandCentrePage.tsx`)
The operational nerve centre providing real-time situational awareness across Rawbank's synthetic DRC environment:
- **Operational KPI Row:** Consumes `GET /api/overview` to render real metrics: Total Alerts, Critical Alerts, High-Risk Alerts, Total Transactions, Active Fraud Signals, Monitored Customers, and Monitored Devices.
- **Immediate Operational Triage Table:** Displays recent critical alerts requiring immediate analyst intervention. Clicking any row opens its `EntityDrawer` with complete 4-tier evidence; clicking `Investigate` transitions directly into the Copilot with a pre-filled investigation prompt.
- **Scenario Distribution Panel:** Visualizes rule distribution across Account Takeover (ATO), Mule Aggregation, Velocity Bursts, and Structuring/Smurfing.
- **Mule Funnel Watchlist:** Real-time surveillance of destination accounts aggregating velocity across multiple unique senders via IllicoCash or mobile money rails.

### 3.2 Fraud Alerts Workspace (`AlertsPage.tsx`)
High-density triage workspace for risk operations:
- **Multi-Vector Filtering:** Filter by Severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), Scenario Type, Customer ID, Rule Code (`R-ATO-05`, `R-VEL-01`, etc.).
- **Deterministic Ordering:** Sort dynamically by Composite Risk Score ($0–100$) or Alert Timestamp (Ascending / Descending).
- **Server-Side Pagination:** Supports paginated browsing (`page`, `page_size`, `total_pages`).

### 3.3 Transaction Ledger (`TransactionsPage.tsx`)
Real-time financial stream across CDF and USD rails:
- **Currency & Channel Triage:** Filter by currency (`USD`, `CDF`), banking channel (`MOBILE_APP`, `ONLINE_BANKING`, `AGENCY_BANKING`, `ATM`, `BRANCH`), and Congolese city (`Kinshasa`, `Lubumbashi`, `Goma`, `Kolwezi`).
- **Amounts:** Displays dual currencies with real-time USD equivalents.
- **One-Click Escalation:** Launch direct investigation into why an individual transaction is anomalous.

### 3.4 Customer Risk Directory (`CustomersPage.tsx`)
Demographic and behavioral surveillance of bank clientele:
- **Segmentation & KYC:** Filters across Customer Segments (`RETAIL`, `SME`, `CORPORATE`, `VIP`) and KYC Tiers (`FULL`, `PARTIAL`, `PENDING`).
- **Risk Tiers:** Instant classification into High, Medium, and Low risk bands based on historical behavioral profiles.

### 3.5 Sentient Fraud Investigation Copilot (`CopilotPage.tsx`)
The centerpiece of **USE CASE 2**, moving beyond generic chat into structured, evidence-grounded forensic reasoning:
- **Separate Forensic Response Sections:**
  1. *Executive Investigation Summary*: High-level synthesis of observed fraud patterns.
  2. *Risk Assessment*: Official deterministic risk score ($0–100$), severity badge, and evidence confidence score.
  3. *Supporting Evidence*: Concrete fraud indicators with source table and interactive `[Source: ID]` pills.
  4. *Counter-Evidence (Mitigating Context)*: Visually distinct emerald panel highlighting facts opposing fraud (e.g., trusted device, KYC Tier 2, clean 3-year tenure).
  5. *Behavioural Deviation*: Quantified divergence from 90-day moving baselines.
  6. *Correlated Activity*: Connected device clusters, shared mule beneficiaries, and related accounts.
  7. *Evidence Gaps & Blindspots*: Explicit display of unconfirmed telemetry (e.g., missing cell tower coordinates or unverified device fingerprint).
  8. *Investigation Next Steps & Escalation Recommendation*: Actionable checklist for the fraud analyst (e.g., account debit freeze, customer callback, SAR filing).
- **Multi-Turn Session Continuity:** Preserves `session_id` across turns so analysts can ask contextual follow-up questions ("What happened before that?") without losing state.
- **Safety & Boundary Banners:** Automatic warning alerts when identity ambiguity is detected (e.g., multiple "Jean Mutombo" records) or unknown entities are queried (`CUS-99999`).

---

## 4. Reusable Entity & Evidence System

### 4.1 Slide-Over Entity Drawer (`EntityDrawer.tsx`)
A universal slide-over drawer accessible from any entity link, table row, or search result across the application.
- **Tab 1 — Overview & Attributes:** Displays raw database fields for Alerts, Transactions, Customers, Devices, or Beneficiaries.
- **Tab 2 — Evidence Packet:** Embeds the full `EvidenceDossier` component showing field-level provenance across 4 tiers.
- **Tab 3 — Relationship Network:** Embeds the `RelationshipTree` component displaying bounded 1-hop and 2-hop topological connections.
- **Copilot Action Launcher:** Header button pre-populates Copilot with entity context and seamlessly switches views.

### 4.2 Evidence Dossier Component (`EvidenceDossier.tsx`)
Visualizes the Phase 5 four-tier standard evidence packet:
- **Tier 1 (Exact Data):** Primary transaction records, timestamps, and amounts.
- **Tier 2 (Calculated Indicators):** Velocity multipliers, threshold ratios, and deviation scores.
- **Tier 3 (Retrieved Evidence):** Cross-table correlations (authentication logs, device fingerprints).
- **Tier 4 (Counter-Evidence):** Mitigating facts defending the customer against false positives.
- **Evidence Gaps:** Explicit warnings highlighting data points unavailable in synthetic telemetry.

### 4.3 Relationship Tree (`RelationshipTree.tsx`)
Forensic network visualizer displaying real database foreign-key relationships:
- Customer $\to$ Accounts $\to$ Transactions $\to$ Beneficiaries.
- Customer $\to$ Shared Devices $\to$ Colluding Customers.
- Destination Beneficiary $\to$ Multiple Sending Accounts.

---

## 5. Security & Secret Handling
1. **Zero Secret Exposure:** No API keys, database credentials, or secret tokens are bundled or accessible in client-side code.
2. **Server-Side LLM Orchestration:** The backend FastAPI service alone manages communication with Groq or deterministic fallbacks.
3. **Sanitized Error Messaging:** Server errors are translated into clean, analyst-friendly notices without leaking internal Python stack traces, file paths, or environment variables.
4. **Synthetic Disclaimer:** Persistent notices in the top navigation and footers explicitly affirm that all records represent synthetic DRC banking data.

---

## 6. Verification & Test Coverage
The frontend architecture was verified with **18 comprehensive automated tests** (`vitest run`):
- Command Centre rendering, KPI aggregation, and live critical triage stream.
- Multi-vector alert filtering by severity, customer, and rule code.
- EntityDrawer attribute and evidence packet rendering for alerts, customers, and transactions.
- Global search query execution and multi-type match resolution.
- Multi-hop relationship network visualization.
- Copilot question submission, multi-section report rendering, clickable provenance pills, counter-evidence styling, evidence gaps, and session ID persistence across follow-ups.
- Graceful API error handling and async loading spinner states.
