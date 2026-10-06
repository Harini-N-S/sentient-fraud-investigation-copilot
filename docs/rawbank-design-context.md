# Rawbank Design Context & Enterprise UI/UX Specification
## Sentient Fraud Intelligence Platform (aXtrLabs)

**Application Type:** High-Density Enterprise Risk Operations Console & Forensic Copilot  
**Brand Context:** Rawbank (Democratic Republic of Congo)  
**Phase:** Phase 1 — Project Foundation & Design Specification  
**Design Philosophy:** Contextually Grounded Enterprise Ergonomics (Not a Public Marketing Clone)

---

### 1. Design Purpose & Strategic Objective

The Sentient Fraud Intelligence Platform is a mission-critical enterprise workstation engineered for Tier-1 fraud triage operators, senior fraud analysts, and AML investigators at Rawbank.

* **Primary Mandate:** The goal is **not** to replicate Rawbank's public consumer website (`rawbank.com`) or consumer mobile app (`IllicoCash`).
* **Enterprise Focus:** The objective is to design an ultra-refined, high-density, low-latency enterprise operations environment that reflects Rawbank's institutional prestige, authority, and Congolese cultural heritage while adhering to international banking workstation standards (e.g., Bloomberg Terminal, Palantir Foundry, Actimize).
* **Missing Official Assets Notice:** Official internal Rawbank UI component libraries (Figma design systems, enterprise design tokens, internal brand guidelines) were **not supplied** in the workspace. In accordance with Phase 1 instructions, missing proprietary assets are documented as absent. The design system defined herein establishes a tailored, modern design specification that honors Rawbank's public brand evolution without fabricating non-existent internal design systems.

---

### 2. Visual Identity & Brand Integration

* **Brand Evolution Grounding:** In 2025, Rawbank unveiled an updated visual identity inspired by the **Congolese leopard**—symbolizing vigilance, agility, strategic composure, and quiet strength. The brand's signature dual pillars are **Vibrant Warm Yellow / Amber** (representing vitality, economic optimism, and innovation) paired with **Deep Obsidian / Pitch Black** (representing institutional stability, trust, and bedrock reliability).
* **Enterprise Application Adaptation:**
  * For consumer marketing, high-saturation yellow is often used as a dominant hero color.
  * In a high-stress, 24/7 fraud monitoring console, large fields of high-saturation yellow would cause severe visual fatigue and eye strain.
  * Therefore, the enterprise platform employs an **Obsidian & Deep Slate dark foundation** with **Warm Amber / Gold accents** applied selectively for primary interactions, system brand accents, active state indicators, and critical focus triggers.

---

### 3. Color Direction & Design Tokens

The color architecture is built around functional luminance, high contrast (WCAG AAA compliant for critical text and badges), and distinct semantic alert levels.

#### A. Surface & Background Tokens (Dark Mode Console)
* **Canvas / Viewport Base:** `#0B0E14` (Deep Space Obsidian — ultra-low luminance, eliminates monitor glare during night shifts)
* **Panel / Card Surface:** `#121721` (Refined Dark Slate — high depth separation)
* **Elevated / Popover Surface:** `#1A2232` (Elevated Midnight Surface — used for modals, dropdowns, and flyout inspectors)
* **Subtle Borders & Separators:** `#263248` (Slate Border — 1px crisp architectural division)
* **Hover / Highlight State:** `#243046` (Subtle interactive wash)

#### B. Brand & Primary Interaction Tokens
* **Rawbank Primary Gold / Amber:** `#F5A623` (Signature Warm Amber — active action buttons, brand badges, key metrics)
* **Rawbank Gold Bright Hover:** `#FFB733` (State highlight on hover/focus)
* **Rawbank Amber Subdued / Fill:** `rgba(245, 166, 35, 0.12)` (Pill badge backgrounds, active tab indicators)

#### C. Semantic Alert & Risk Tokens
Risk colors must never be ambiguous in a fraud room:
* **Critical / Confirmed Fraud (Tier 1):** `#EF4444` (Vivid Crimson) / Fill: `rgba(239, 68, 68, 0.15)`
* **High Risk / Escalation Required:** `#F97316` (High-Energy Tangerine) / Fill: `rgba(249, 115, 22, 0.15)`
* **Medium Risk / Anomaly Detected:** `#F59E0B` (Vigilance Amber) / Fill: `rgba(245, 158, 11, 0.15)`
* **Low Risk / Informational:** `#3B82F6` (Operational Blue) / Fill: `rgba(59, 130, 246, 0.15)`
* **Verified Normal / Cleared:** `#10B981` (Safe Emerald) / Fill: `rgba(16, 185, 129, 0.15)`

#### D. Typography Colors
* **Primary Text:** `#F8FAFC` (Slate 50 — maximum readability)
* **Secondary Text:** `#94A3B8` (Slate 400 — labels, metadata headers, timestamps)
* **Muted / Tertiary Text:** `#64748B` (Slate 500 — inactive indicators, structural guides)
* **Monospace Data:** `#38BDF8` (Cyan 400 — raw IDs, hash digests, IP addresses)

---

### 4. Typography Direction

* **Typeface Strategy:** Modern, clean, geometric sans-serif with high x-height and legible numerals.
  * **Primary UI & Headings:** `Inter`, `Plus Jakarta Sans`, or modern system font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`).
  * **Numerical & Data Code:** Monospace font with tabular alignment (`JetBrains Mono`, `Fira Code`, or `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas`).
* **Tabular Numbers Standard:** All financial amounts, account numbers, timestamps, and velocity metrics must employ `font-variant-numeric: tabular-nums` to guarantee vertical column alignment across dense tables.
* **Typographic Scale:**
  * `Heading 1` (Dashboard Title / View Header): 22px / Semi-bold (600) / Tracking: -0.02em
  * `Heading 2` (Section / Drawer Title): 16px / Semi-bold (600) / Tracking: -0.01em
  * `Body Regular` (General text, Copilot responses): 13px / Regular (400) / Line-height: 1.5
  * `Metadata / Table Cell`: 12px / Medium (500) / Tabular
  * `Micro Badges & Captions`: 10px / Semi-bold (600) / Uppercase / Tracking: +0.05em

---

### 5. Spacing System & Grid Architecture

* **Grid Base:** Strictly adhering to an **8px base grid** with a **4px sub-grid** for micro-components (chips, badges, icon padding).
  * `4px` — Micro gap (badge padding, icon-to-label spacing)
  * `8px` — Standard compact element padding (table cells, list item gaps)
  * `12px` — Moderate gap (card internal padding in high-density views)
  * `16px` — Standard container padding (panel margins, drawer gutters)
  * `24px` — Section division spacing
* **Responsive Multi-Pane Viewport:**
  * Target Resolution: Optimized for desktop displays (1920x1080 / 1440x900) standard in SOC control rooms.
  * Layout Partition:
    * Left Global Nav / Context Bar (64px collapsed or 220px expanded)
    * Central Command & Triage Stream (Dynamic 60%–70% width)
    * Right Contextual Inspector & Copilot Workspace (Dynamic 30%–40% width, dockable/expandable)

---

### 6. Information Hierarchy

The visual hierarchy ensures that an analyst can assess operational reality in under 5 seconds:
1. **Global Health Strip (Top Bar):** Operational environment badge (Synthetic Environment Active), system time (Kinshasa UTC+1 / Lubumbashi UTC+2), active threat level, total flagged transaction velocity.
2. **Prioritization KPI Ribbon:** Quick-filter buckets (`Severe / Unassigned`, `Active Triage`, `Awaiting Customer Callback`, `Escalated to AML`).
3. **Primary Queue (Command Centre):** Sorted by computed composite risk score descending. Critical alerts demand attention via glowing edge indicators and crimson risk pill tags.
4. **Drill-Down Inspector Panel:** Immediate contextual pivot showing transaction breakdown, customer profile, and device fingerprints without navigating away from the triage stream.
5. **Fraud Investigation Copilot Console:** Persistent, interactive right-rail providing structured AI reasoning, evidence links, and action buttons.

---

### 7. Banking UI Patterns & Conventions

* **Dual Currency Display:** Congolese transactions frequently switch between CDF and USD. The UI must explicitly present the original transaction currency with formatted thousands separators, with secondary equivalent conversion clearly noted:
  * Example: `CDF 25,000,000` *(≈ USD 9,250.00 @ 2,700)* or `USD 5,000.00`.
* **Four-Tier Information Classification Badges:** To prevent analyst confusion between raw facts and AI hypotheses, every piece of displayed data must visually indicate its analytical grade:
  * `[EXACT DATA]` — Pill in Monospace Gray (`#64748B`)
  * `[CALCULATED]` — Pill in Cyan (`#0EA5E9`)
  * `[EVIDENCE]` — Pill in Amber (`#F59E0B`)
  * `[AI REASONING]` — Pill in Purple/Violet (`#8B5CF6`)
* **Entity Identifiers:** Masked sensitive identifiers with click-to-copy utility:
  * Customer ID: `RAW-CUST-88319`
  * Account Number: `0100-****-****-4412 (USD)`
  * Transaction Hash: `TX-8912-A109`

---

### 8. Interaction Language & Micro-Interactions

* **Frictionless Drill-Down:** Clicking any row in the Command Centre instantaneously populates the Inspector and initializes the Copilot's working memory with the selected entity.
* **Instant Filtering & Zero Full-Page Reloads:** Real-time client-side filtering by channel (`IllicoCash`, `ATM`, `Agency`, `SWIFT`), currency (`USD`, `CDF`), risk tier, and trigger rule.
* **Keyboard Shortcuts for Speed:** High-volume operators can triage using hotkeys (e.g., `J`/`K` for list navigation, `Space` to inspect, `E` to escalate, `C` to invoke Copilot).
* **Hover State Elevation:** Interactive cards subtly lift with a 1px border brighten (`#334155`) and slight shadow rather than drastic color shifts.

---

### 9. Enterprise Application Design Principles

1. **Information Density over Decorative White Space:** Analysts need immediate access to complex relationships; whitespace should structure data, not isolate it.
2. **Never Obscure Raw Evidence:** The analyst is legally responsible for regulatory reporting. The UI must always allow an analyst to view the raw JSON event payload and deterministic rule calculations backing any AI statement.
3. **Auditability by Design:** Every analyst interaction (triage mark, escalation, Copilot prompt, dismiss action) must visually generate an immutable audit trail entry with an analyst ID and UTC timestamp.
4. **Clear State Indicators:** Loading, error, empty, and streaming states must be crisp, non-blocking, and communicative.
