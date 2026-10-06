# Rawbank Enterprise Design System
## Sentient Fraud Intelligence Platform (aXtrLabs)

**Document Reference:** `docs/rawbank-design-system.md`  
**Brand:** Rawbank SA (Democratic Republic of the Congo)  
**Version:** 2.0 (Phase A — Brand Essence & Design System Alignment)  
**Primary Corporate Reference:** [Rawbank Official Corporate Portal](https://rawbank.com/) / `rawbank.cd`  
**Application Type:** High-Density Enterprise Risk Operations Console & Forensic Copilot  
**Compliance Context:** Banque Centrale du Congo (BCC) Regulatory Standards / FATF AML Guidelines  

---

> [!IMPORTANT]
> **SYNTHETIC ENVIRONMENT NOTICE**  
> This design system governs an enterprise operations workstation monitoring **100% synthetic fraud intelligence data**. It establishes an authentic, authoritative Rawbank visual language while maintaining a strict, prominent visual boundary:  
> *"Synthetic banking environment — No real customer data"*.  
> Under no circumstances must this application imply that the synthetic dataset comprises real customer PII or actual internal Rawbank records.

---

## A. Brand Essence

Founded in 2002 by the Rawji family, **Rawbank** is the leading commercial private bank in the Democratic Republic of the Congo. The bank stands as a foundational pillar of the national economy, connecting high-value industrial mining corporations in Katanga and Lualaba with broad-based financial inclusion across Kinshasa, North/South Kivu, and Kongo Central through digital platforms (`IllicoCash`, `RawbankOnline`, `Rawbank Express`).

In April 2025, Rawbank unveiled an updated visual identity rooted in the **Congolese Leopard (*Panthera pardus*)**, the national animal of the DRC. The brand essence integrates:
1. **The Congolese Leopard:** Symbolizes vigilance, agile responsiveness, resilience, and strategic composure. In a fraud operations console, this translates into sharp situational awareness and instantaneous forensic triage.
2. **Selective Yellow (`#FCB900`):** Embodies vitality, economic optimism, dynamic energy, and faith in the future of the Congo. It is the color of the leopard's agile claws and forward momentum.
3. **Solid Pitch Black & Deep Obsidian (`#0E131B` / `#11141A`):** Reflects the bedrock trust, institutional solidity, reliability, and security that customers and regulatory authorities place in Rawbank.
4. **Corporate Purpose ("Rawbank is my bank"):** Grounded proximity, transparency, customer empowerment, and continental leadership.
5. **Stated Corporate Values:** Ambition, Initiative, Collaboration, Innovation, and Rendement (performance/yield).

---

## B. Brand Personality

The visual language communicates an **authoritative, high-performance banking operations environment**, not a consumer marketing site or a generic cyberpunk security dashboard:

| Brand Attribute | Operational Expression | What to Avoid |
| :--- | :--- | :--- |
| **Trust & Institutional Authority** | Deep obsidian slate surfaces, crisp 1px borders, verified data grades, strict BCC compliance cues. | Casual playful styling, unanchored floating elements, low-contrast text. |
| **Strength & Agility** | Instant client-side filtering, sub-second Copilot retrieval, prominent high-impact KPI counters. | Sluggish transitions, decorative animations, excessive whitespace. |
| **Congolese Banking Grounding** | Dual currency display (CDF/USD), dual operational timezones (Kinshasa UTC+1 / Lubumbashi UTC+2), local channel tags (`IllicoCash`, `Agency Express`). | Generic US/EU-only references, missing currency distinctions. |
| **Clarity & Transparency** | Multi-tier evidence grades (`[EXACT DATA]`, `[CALCULATED]`, `[EVIDENCE]`, `[AI REASONING]`), clickable source citations `[Source: ID]`. | Black-box AI assertions, unverified claims, opaque risk scores. |
| **Operational Composure** | Calibrated luminance dark-mode, eliminating eye strain during 24/7 night shifts; intentional yellow accentuation. | Saturated yellow background floods, neon cyberpunk glows, purple/magenta gaming aesthetics. |

---

## C. Color Tokens

The palette is anchored by Rawbank's verified corporate colors: **Selective Yellow (`#FCB900`)**, **Obsidian Base (`#0E131B`)**, and **Mine Shaft Slate (`#192231`)**, complemented by strict WCAG AAA semantic alert indicators.

```css
:root {
  /* ==========================================================================
   * 1. RAWBANK BRAND CORE TOKENS
   * ========================================================================== */
  --rawbank-yellow: #FCB900;                 /* Primary Rawbank Brand Gold/Yellow */
  --rawbank-yellow-hover: #E5A700;           /* Interactive Hover State */
  --rawbank-yellow-light: #FFD24D;           /* Bright State / Highlight */
  --rawbank-yellow-fill: rgba(252, 185, 0, 0.12); /* Subtle Brand Wash */
  --rawbank-yellow-border: rgba(252, 185, 0, 0.35); /* Focus & Active Card Outline */
  --rawbank-yellow-glow: 0 0 16px rgba(252, 185, 0, 0.22); /* Focus / Selected Glow */

  /* ==========================================================================
   * 2. OBSIDIAN & SLATE SURFACES (Low Fatigue Dark Mode)
   * ========================================================================== */
  --rawbank-black: #0E131B;                  /* Canvas Viewport Base (Lowest Luminance) */
  --rawbank-surface: #141B26;                /* Panel / Sidebar / Navigation Background */
  --rawbank-surface-card: #192231;           /* Elevated Cards & Triage Rows */
  --rawbank-surface-elevated: #202B3C;       /* Modals, Drawers & Popovers */
  --rawbank-surface-hover: #263346;          /* Table Row & Button Hover Wash */
  --rawbank-surface-active: #2C3C52;         /* Selected Table Row / Active Node */

  /* ==========================================================================
   * 3. ARCHITECTURAL BORDERS & SEPARATORS
   * ========================================================================== */
  --rawbank-border: #233044;                 /* Subtle 1px Row Divider */
  --rawbank-border-default: #2C3D56;         /* Container & Card Border */
  --rawbank-border-strong: #3D5375;          /* Interactive Input & Active Border */
  --rawbank-border-gold: rgba(252, 185, 0, 0.45); /* Brand Emphasis Border */

  /* ==========================================================================
   * 4. TYPOGRAPHY TOKENS
   * ========================================================================== */
  --rawbank-text-primary: #F8FAFC;           /* Highest Contrast Primary Text */
  --rawbank-text-secondary: #94A3B8;         /* Secondary Metadata, Subtitles */
  --rawbank-text-muted: #64748B;             /* Inactive Guides, Timestamps */
  --rawbank-text-inverse: #0E131B;           /* Dark Text on Yellow Badges/Buttons */
  --rawbank-text-mono: #38BDF8;              /* Monospace Technical IDs (IDs/Hashes) */

  /* ==========================================================================
   * 5. SEMANTIC RISK & STATUS TOKENS (Preserving Operational Meaning)
   * ========================================================================== */
  --rawbank-danger: #EF4444;                 /* Critical Risk (Tier 1 Fraud Alert) */
  --rawbank-danger-bg: rgba(239, 68, 68, 0.14);
  --rawbank-danger-border: rgba(239, 68, 68, 0.45);

  --rawbank-high: #F97316;                   /* High Risk / Escalation Required */
  --rawbank-high-bg: rgba(249, 115, 22, 0.14);
  --rawbank-high-border: rgba(249, 115, 22, 0.45);

  --rawbank-warning: #F59E0B;                /* Medium Risk / Anomaly Detected */
  --rawbank-warning-bg: rgba(245, 158, 11, 0.14);
  --rawbank-warning-border: rgba(245, 158, 11, 0.45);

  --rawbank-low: #38BDF8;                    /* Low Risk / Operational Informational */
  --rawbank-low-bg: rgba(56, 189, 248, 0.14);
  --rawbank-low-border: rgba(56, 189, 248, 0.45);

  --rawbank-success: #10B981;                /* Verified Normal / Cleared Account */
  --rawbank-success-bg: rgba(16, 185, 129, 0.14);
  --rawbank-success-border: rgba(16, 185, 129, 0.45);
}
```

### Color Token Usage Matrix

| Token Name | Hex / Value | Purpose & Where Used | What NOT to Do |
| :--- | :--- | :--- | :--- |
| `--rawbank-yellow` | `#FCB900` | Primary brand emblem, primary CTAs, active navigation, key KPI emphasis, Copilot send button. | **DO NOT** use as full-page background or large container fills. Causes severe glare. |
| `--rawbank-yellow-fill` | `rgba(252, 185, 0, 0.12)` | Active tab pill backgrounds, brand badges, selected state highlights. | **DO NOT** use for text. Lacks sufficient contrast. |
| `--rawbank-black` | `#0E131B` | Viewport canvas background, scroll tracks. | **DO NOT** use pure `#000000` for cards; prevents optical depth layering. |
| `--rawbank-surface` | `#141B26` | Main panels, navigation sidebar, top navbar. | **DO NOT** use random grays or blue gradients. |
| `--rawbank-surface-card` | `#192231` | Dense table bodies, KPI metric cards, Copilot response containers. | **DO NOT** mix transparent and solid cards randomly. |
| `--rawbank-danger` | `#EF4444` | Confirmed fraud, Critical severity pills, emergency account freeze actions. | **DO NOT** substitute brand yellow for critical fraud; yellow is not red. |
| `--rawbank-high` | `#F97316` | High risk tier, AML structuring alerts, urgent review flags. | **DO NOT** confuse with medium risk amber. |
| `--rawbank-success` | `#10B981` | Synthetic environment badge, cleared risk baselines, verified OTPs. | **DO NOT** use for marketing buttons. Reserved strictly for truth states. |

---

## D. Typography Tokens

Rawbank's corporate communications use modern, bold, approachable typography. In digital engineering, **Montserrat** represents the closest geometric sans-serif match to Rawbank's brand font, while **Inter** provides industry-leading legibility at small sizes (10px–13px) in dense data tables.

* **Primary Heading & UI Font:** `Inter`, `Montserrat`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `sans-serif`
* **Data, Numeric & Code Font:** `JetBrains Mono`, `ui-monospace`, `SFMono-Regular`, `Consolas`, `monospace`
* **Tabular Standard:** All currency amounts (`USD`, `CDF`), account numbers, transaction hashes, and risk scores **must** declare `font-variant-numeric: tabular-nums` to ensure exact column alignment.

### Typography Hierarchy

| Token | Size | Weight | Tracking / Line-Height | Application | What NOT to Do |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Display` | 26px | 700 (Bold) | `-0.025em / 1.2` | Platform master header, executive reports | No decorative serifs or cursive fonts |
| `H1` | 22px | 700 (Bold) | `-0.02em / 1.25` | View titles (`Command Centre`, `Copilot`) | Do not use full uppercase strings |
| `H2` | 16px | 600 (Semi-bold) | `-0.015em / 1.3` | Section headings, panel headers | Do not skip heading levels |
| `H3` | 13.5px | 600 (Semi-bold) | `-0.01em / 1.4` | Card titles, drawer subheadings | Do not use font-weight below 500 |
| `Body` | 13px | 400 (Regular) | `0 / 1.5` | Copilot explanations, descriptions | Do not use low-contrast text below `#94A3B8` |
| `Body Small` | 12px | 400 / 500 | `0 / 1.4` | Table cell data, input fields, labels | Do not use below 11px for critical body text |
| `Label` | 11px | 600 (Semi-bold) | `+0.04em / 1.2` | Table headers, form field labels (Uppercase) | Do not make uppercase labels low-contrast |
| `Caption` | 10px | 500 (Medium) | `+0.05em / 1.2` | Timestamp metadata, channel pills | Do not use for primary numbers |
| `KPI Value` | 24px | 700 (Bold) | `-0.02em / 1.1` | Primary metric count cards | Always pair with tabular numbers |
| `Monospace` | 11.5px | 500 (Medium) | `0 / 1.3` | Entity IDs (`CUS-00014`, `TXN-00801`) | Never use variable-width fonts for IDs |

---

## E. Spacing Tokens

The spacing architecture strictly adheres to an **8px base grid** with a **4px sub-grid**:

```css
--space-1: 4px;   /* Micro-gap: icon to label, chip padding */
--space-2: 8px;   /* Standard compact element gap */
--space-3: 12px;  /* Card internal padding, button padding */
--space-4: 16px;  /* Standard container padding, panel margin */
--space-5: 20px;  /* Section gap in command center */
--space-6: 24px;  /* Major column and workspace gutter */
--space-8: 32px;  /* Large section divisions */
```

* **Usage Rule:** Use `--space-2` (8px) and `--space-3` (12px) for high-density tables and inspector lists to maximize visible information per screen.
* **What NOT to Do:** Do not use arbitrary values like `17px`, `23px`, or `37px`.

---

## F. Border & Radius Tokens

```css
--radius-xs: 2px;     /* Monospace code tags, micro keycaps */
--radius-sm: 4px;     /* Table rows, action buttons, status badges */
--radius-md: 8px;     /* Panels, metric cards, modal dialogs */
--radius-lg: 12px;    /* Floating drawer panels, Copilot response boxes */
--radius-full: 9999px; /* Status pills, avatar emblems, environment badges */

--border-width: 1px;  /* Clean architectural hairline division */
```

* **Usage Rule:** High-density enterprise tools require structured, crisp borders (`4px` to `8px`).
* **What NOT to Do:** Avoid bubbly, oversized pill radius (`24px`+) on enterprise cards or tables.

---

## G. Shadow & Elevation Rules

Elevation in dark-mode operations consoles is achieved through **luminance layering** combined with soft, natural occlusion shadows:

```css
--elevation-0: none; /* Base canvas */
--elevation-1: 0 1px 2px 0 rgba(0, 0, 0, 0.4); /* Table rows, subtle cards */
--elevation-2: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.5); /* Floating panels */
--elevation-3: 0 10px 15px -3px rgba(0, 0, 0, 0.7), 0 4px 6px -4px rgba(0, 0, 0, 0.7); /* Modals, Drawers */
--elevation-glow: 0 0 16px rgba(252, 185, 0, 0.22); /* Active state emphasis */
```

* **What NOT to Do:** Avoid colorful neon drop-shadows (e.g. bright blue or magenta shadows) that resemble video games.

---

## H. Button Styles

Buttons follow strict hierarchy:

1. **Primary Brand Action (`.btn-primary`):**
   - Background: `var(--rawbank-yellow)` (`#FCB900`)
   - Text: `var(--rawbank-text-inverse)` (`#0E131B`) — Bold 600
   - Hover: `var(--rawbank-yellow-hover)` (`#E5A700`)
   - Use: Execute investigation, submit Copilot inquiry, confirm freeze.
2. **Secondary Utility (`.btn-secondary`):**
   - Background: `var(--rawbank-surface-card)` (`#192231`)
   - Text: `var(--rawbank-text-primary)` (`#F8FAFC`) — Medium 500
   - Border: `1px solid var(--rawbank-border)`
   - Hover: `var(--rawbank-surface-hover)` with `var(--rawbank-border-strong)`
   - Use: Filter controls, refresh telemetry, export dossier.
3. **Investigation Sparkle Button (`.btn-investigate`):**
   - Background: `var(--rawbank-yellow-fill)`
   - Border: `1px solid var(--rawbank-yellow-border)`
   - Color: `var(--rawbank-yellow)`
   - Hover: Background `rgba(252, 185, 0, 0.22)`, border `var(--rawbank-yellow)`
   - Use: Instant Copilot investigation launcher on alerts, transactions, and customers.
4. **Destructive Action (`.btn-danger`):**
   - Background: `var(--rawbank-danger-bg)`
   - Border: `1px solid var(--rawbank-danger-border)`
   - Color: `var(--rawbank-danger)`
   - Use: Account lock, terminate session, file SAR to Central Bank.

---

## I. Card Styles

1. **Metric Card (`MetricCard`):**
   - Background: `var(--rawbank-surface)` (`#141B26`)
   - Border: `1px solid var(--rawbank-border-default)`
   - Border Accent: Corresponding severity or brand gold
   - Padding: `12px 14px`
   - Hover: Subtle `translateY(-2px)` with refined shadow
2. **Content Panel (`.panel`):**
   - Structure: Header (`.panel-header`) + Body (`.panel-body`)
   - Header Background: `var(--rawbank-surface-card)` with `1px solid var(--rawbank-border)` bottom edge.

---

## J. Table Styles

Dense enterprise data tables are the operational backbone:

- **Header (`th`):** `10px` uppercase, semi-bold, letter-spacing `0.06em`, color `var(--rawbank-text-secondary)`, background `var(--rawbank-surface-card)`.
- **Data Rows (`td`):** `12px`, padding `10px 14px`, hairline border `var(--rawbank-border)`.
- **Hover:** Immediate background shift to `var(--rawbank-surface-hover)` (`#263346`).
- **Numbers:** Tabular alignment (`font-variant-numeric: tabular-nums`).

---

## K. Badge & Status Styles

Badges must be concise, crisp, and high-contrast:

- **Shape:** `border-radius: var(--radius-sm)`, padding `2px 8px`, `font-size: 10.5px`, `font-weight: 600`.
- **Typography:** Uppercase, tracking `+0.05em`.
- **Variants:**
  - `badge-gold`: Brand indicator, Copilot signals (`#FCB900` text, fill `rgba(252, 185, 0, 0.14)`).
  - `badge-safe`: Verified normal, zero fraud, live environment active.
  - `badge-neutral`: System telemetry, KYC tier standard.

---

## L. Alert Severity Styles

Fraud severity indicators must **never** be visually diluted by brand colors. Semantic colors remain distinct:

| Severity Tier | Text Color | Fill / Background | Border | Action Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL** | `#EF4444` (Crimson) | `rgba(239, 68, 68, 0.14)` | `rgba(239, 68, 68, 0.45)` | Immediate account containment required (<5 min) |
| **HIGH** | `#F97316` (Tangerine) | `rgba(249, 115, 22, 0.14)` | `rgba(249, 115, 22, 0.45)` | Tier-2 investigator manual review queue |
| **MEDIUM** | `#F59E0B` (Amber) | `rgba(245, 158, 11, 0.14)` | `rgba(245, 158, 11, 0.45)` | Anomaly flagged; awaiting customer callback |
| **LOW** | `#38BDF8` (Sky Cyan) | `rgba(56, 189, 248, 0.14)` | `rgba(56, 189, 248, 0.45)` | Informational baseline shift |
| **CLEARED / SAFE**| `#10B981` (Emerald) | `rgba(16, 185, 129, 0.14)` | `rgba(16, 185, 129, 0.45)` | Verified authentic transaction |

---

## M. Navigation Styles

1. **Top Navbar (`Navbar`):**
   - Sticky `56px` height.
   - Brand lockup: Stylized Rawbank Leopard shield emblem + "RAWBANK" wordmark + "SENTIENT" badge.
   - Prominent disclaimer chip: `[● SYNTHETIC BANKING ENVIRONMENT | Zero Real PII]`.
   - Dual-zone digital clocks: Kinshasa (WAT, UTC+1) and Lubumbashi (CAT, UTC+2).
   - Global search trigger: `⌘K` / `Ctrl+K`.
2. **Sidebar (`Sidebar`):**
   - Width `240px`, docked left.
   - Active view highlighted with `var(--rawbank-yellow-fill)` and `1px solid var(--rawbank-yellow-border)`.
   - Critical alert count pill in vivid red (`#EF4444`).
   - Bottom protocol status: `Rule Engine v1.0 • 11 Forensic Rules Active • Grounded Verification`.

---

## N. Form & Input Styles

- Height `34px`, font-size `12px`, background `var(--rawbank-black)`.
- Border `1px solid var(--rawbank-border-default)`, focus border `var(--rawbank-yellow)`.
- Focus outline: `2px solid var(--rawbank-yellow)` with `1px` offset.
- Placeholders in `var(--rawbank-text-muted)` (`#64748B`).

---

## O. Modal & Drawer Styles

1. **Slide-Over Entity Drawer (`EntityDrawer`):**
   - Width `680px`, sliding in from right viewport edge.
   - Backdrop: `rgba(0, 0, 0, 0.75)` with `backdrop-filter: blur(2px)`.
   - Displays complete 4-tier evidence packet, entity profile, and relationship tree.
2. **Global Search Modal (`GlobalSearchModal`):**
   - Width `600px`, centered, shortcut `Ctrl+K` / `⌘K`.
   - Immediate search across Customers, Accounts, Transactions, Devices, and Beneficiaries.

---

## P. Chart & Data Visualization Rules

- **Palette Hierarchy:** Brand yellow `#FCB900` is reserved for current activity, highlighted scenarios, and focal metrics.
- **Backgrounds:** Transparent or `var(--rawbank-surface-card)` to avoid optical clashes.
- **Scenario Bars:** Gradient from `var(--rawbank-yellow)` (`#FCB900`) to `var(--rawbank-yellow-light)` (`#FFD24D`).
- **Tooltips:** Elevated midnight container (`#202B3C`) with `1px solid var(--rawbank-border-default)`.

---

## Q. Iconography Rules

- **Icon Set:** Clean, standardized stroke icons from `lucide-react`.
- **Stroke Width:** `1.75px` to `2px` for crisp legibility on high-DPI displays.
- **Size Standards:**
  - Micro / Inline: `12px`–`14px`
  - Action buttons / Table actions: `14px`–`16px`
  - Navigation / Section headers: `18px`–`20px`
- **Color Rule:** Icons inherit parent text color or specific semantic risk color.

---

## R. Voice & UI Language

The system communicates with the **calm, rigorous authority of an enterprise bank forensic officer**:

### UI Terminology Standards
| Preferred Operational Term | Do NOT Use | Reason |
| :--- | :--- | :--- |
| **Investigation** | Chat / Prompt | This is a forensic audit tool, not a social bot. |
| **Evidence Dossier** | AI Answer / Response | Emphasizes deterministic grounding and legal auditability. |
| **Evidence Gap** | Missing info / AI confusion | Precise forensic classification of data blindspots. |
| **Counter-Evidence** | Good stuff / Exceptions | Objective mitigating facts in forensic balance. |
| **Recommended Operational Disposition** | Suggestion / What to do | Standard banking triage decision protocol. |
| **Customer Risk Surveillance** | User Tracker | Financial institutional terminology. |
| **Synthetic Transaction Ledger** | Fake Transactions | Accurately describes synthetic financial records. |
| **Mule Funnel Watchlist** | Bad guys / Suspicious people | Formal anti-money laundering (AML) classification. |

---

## S. Accessibility Rules (WCAG 2.1 AA / AAA Compliance)

1. **Contrast Ratio Standard:**
   - Primary text (`#F8FAFC` on `#0E131B` / `#141B26`): **15.2:1** (Exceeds WCAG AAA requirement of 7:1).
   - Secondary text (`#94A3B8` on `#141B26`): **6.8:1** (Exceeds WCAG AA requirement of 4.5:1).
   - Brand Yellow text on dark background (`#FCB900` on `#0E131B`): **11.4:1** (Exceeds WCAG AAA).
   - Inverted dark text on Brand Yellow buttons (`#0E131B` on `#FCB900`): **11.4:1** (Exceeds WCAG AAA).
2. **Never Color-Alone:**
   - Every severity badge combines color, bold uppercase text (`CRITICAL`, `HIGH`, `MEDIUM`), and contextual risk score (`94 / 100`).
3. **Keyboard Navigable:**
   - Full focus rings (`outline: 2px solid var(--rawbank-yellow)`), search shortcut (`Ctrl+K`), and keyboard-accessible modal dismiss (`Esc`).
4. **Semantic HTML:**
   - Header, main, nav, section, table, thead, tbody, th, td, button elements used exclusively.
