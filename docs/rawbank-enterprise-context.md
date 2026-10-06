# Rawbank Enterprise Context
## Enterprise Fraud Intelligence Platform (aXtrLabs)

**Organization:** Rawbank SA  
**Headquarters:** Kinshasa, Democratic Republic of the Congo (DRC)  
**Domain:** Banking & Financial Services (BFSI)  
**Phase:** Phase 1 — Project Foundation & Enterprise Context  
**Document Status:** Foundation Specification

> [!IMPORTANT]
> **SYNTHETIC DATA DISCLAIMER**  
> All banking operations, customer records, transactions, account numbers, and fraud patterns described or used in this project are strictly **synthetic** and designed for educational, research, and technical evaluation purposes. Under no circumstances should synthetic data or simulated fraud typologies be construed as representing real customer records or actual internal vulnerability data of Rawbank SA.

---

### Information Provenance Framework

To maintain strict analytical rigor, all information throughout this document is classified under three distinct categories:
1. **[Supplied by Assignment]**: Direct constraints and specifications provided in the project prompt.
2. **[Verified Public Research]**: Factual data obtained from verified public disclosures, annual reports, regulatory publications (Banque Centrale du Congo), and official brand communications.
3. **[Assumptions Requiring Validation]**: Operational and synthetic modelling assumptions formulated for system design, to be confirmed once authoritative assignment resources (such as `SentientData_RuleSet.md` or `SyntheticData_Fuel`) are supplied.

---

### 1. Rawbank Business Context

* **Institutional Profile [Verified Public Research]:** Founded in 2002 by the Rawji family, Rawbank is the largest commercial private bank in the Democratic Republic of the Congo. It operates nationwide across all major economic provinces, serving as a pillar of the Congolese financial system.
* **Strategic Role [Verified Public Research]:** Rawbank bridges traditional corporate banking (particularly servicing the extensive mining and infrastructure sectors in Katanga and Kolwezi) with mass-market retail financial inclusion through mobile wallets and agency banking.
* **Regulatory Environment [Verified Public Research]:** Regulated by the *Banque Centrale du Congo* (BCC) under Congolese banking laws, adhering to international AML/CFT (Anti-Money Laundering / Combating the Financing of Terrorism) standards, FATF guidelines, and regional financial reporting mandates.
* **Dual Currency Paradigm [Verified Public Research]:** The DRC operates under a pervasive dual-currency regime. The Congolese Franc (CDF) and the United States Dollar (USD) co-circulate in everyday transactions, pricing, and bank accounts. Rawbank accounts and transactions natively operate in both CDF and USD.
* **Enterprise Fraud Challenge [Supplied by Assignment & Verified Public Research]:** As digital payments, mobile wallets, and agency networks expand across a vast territory, financial institutions face escalating fraud vectors—ranging from account takeovers (ATO) and SIM swapping to mule networks, structuring, and internal collusion. Detecting these threats requires combining deterministic financial rules with contextual, AI-grounded intelligence.

---

### 2. Customer Segments

| Customer Segment | Profile & Economic Characteristics | Primary Interaction Mode | Typical Fraud Exposure |
| :--- | :--- | :--- | :--- |
| **Retail / Mass Market** *[Verified Public Research]* | Everyday citizens, wage earners, students, and unbanked populations entering the formal economy. High transaction count, moderate-to-low ticket size. Highly mobile-reliant. | IllicoCash mobile wallet, USSD, Agency Banking kiosks, ATMs. | SIM swap, phishing/vishing for mobile PINs, social engineering, unauthorized cardless ATM cash-outs. |
| **High Net Worth Individuals (HNWI) & Executives** *[Verified Public Research]* | Senior corporate executives, expatriates, diplomats, and business owners holding substantial balances in USD and CDF. | RawbankOnline (Web), Priority Branch Desks, Platinum Debit/Credit cards. | Targeted spear-phishing, credential stuffing, high-value unauthorized wire transfers, device hijacking. |
| **Small & Medium Enterprises (SMEs) & Merchants** *[Verified Public Research]* | Local retail stores, logistics suppliers, importers, service companies, and merchant distributors. Frequent daily turnover. | IllicoCash Merchant QR, POS terminals, RawbankOnline Business, branch cash drops. | False invoice redirection, merchant QR code tampering, rapid fund diversion via compromised business accounts. |
| **Large Corporates & Mining Conglomerates** *[Verified Public Research]* | Multinational mining firms (copper/cobalt in Haut-Katanga & Lualaba), telecommunications, FMCG distributors, international NGOs. Massive volume & high value. | RawbankOnline Enterprise, host-to-host ERP integration, corporate treasury services. | Corporate payroll manipulation (ghost employees), unauthorized bulk transfer beneficiary tampering, insider threat / dual-control bypass. |
| **Agency Banking Operators (Rawbank Express Agents)** *[Verified Public Research]* | Independent third-party merchants authorized to perform cash-in (deposits) and cash-out (withdrawals) on behalf of Rawbank in remote and urban areas. | Specialized agent POS terminals, dedicated agent mobile portals. | Agent-assisted cash-out of compromised funds, structuring deposits to evade AML limits, phantom float inflation, collusion with illicit syndicates. |

---

### 3. Banking Products

* **Deposit Accounts [Verified Public Research]:**
  * Current Accounts (available natively in CDF and USD).
  * Savings Accounts (interest-bearing CDF and USD accounts).
  * Term Deposit Accounts (treasury and corporate fixed-term placements).
* **Payment & Transaction Products [Verified Public Research]:**
  * IllicoCash Mobile Wallet accounts (standalone or linked to core Rawbank ledger).
  * International Debit and Prepaid Cards (Visa, Mastercard in USD).
  * Corporate Payroll Disbursement solutions (batch file upload for automated salary payouts).
  * Local Interbank Transfers via the BCC national clearing switch.
  * International Wire Transfers (SWIFT transfers in USD/EUR).
* **Credit & Trade Finance [Verified Public Research]:**
  * SME working capital credit lines, overdraft facilities, letters of credit for mining and import-export operations.
* **Foreign Exchange (FX) [Verified Public Research]:**
  * Spot currency conversion between CDF and USD at official and market-clearing rates.

---

### 4. Digital Channels

1. **IllicoCash Mobile App [Verified Public Research]:** The flagship mobile banking and electronic wallet application by Rawbank. Enables self-service registration, P2P transfers, bill payments, airtime recharges, merchant QR payments, currency exchange (CDF/USD), and cardless ATM withdrawals. Available on Android and iOS.
2. **RawbankOnline (Web Portal) [Verified Public Research]:** The comprehensive internet banking platform designed for retail, SME, and institutional corporate clients. Supports bulk payments, multi-tiered transaction approval workflows, SWIFT transfers, and account reconciliation.
3. **Rawbank Express (Agency Banking) [Verified Public Research]:** Branchless banking network of authorized local shopkeepers and agents providing cash deposit and withdrawal services across high-density markets and underserved remote regions.
4. **Automated Teller Machines (ATMs) [Verified Public Research]:** Nationwide network of ATMs supporting both physical chip-and-PIN debit cards and digital cardless withdrawals using dynamic one-time tokens generated via IllicoCash.
5. **Point-of-Sale (POS) Merchant Network [Verified Public Research]:** EMV chip-and-PIN and contactless POS terminals deployed across hotels, supermarkets, fuel stations, and mining supply depots.
6. **USSD & SMS Fallback [Verified Public Research]:** Lightweight cellular telecom channels utilized for balance alerts, transaction OTPs, and feature-phone access in areas with constrained data connectivity.

---

### 5. Payment & Transaction Journeys

* **Domestic P2P Mobile Transfer (IllicoCash):**  
  *Sender opens app → Authenticates (Biometric/PIN) → Selects recipient (Phone / Account) → Enters amount & currency (CDF/USD) → Approves transaction → Real-time ledger debit & credit → Instant SMS/Push receipt to both parties.*
* **Cardless ATM Cash-Out:**  
  *User initiates cardless withdrawal on IllicoCash → System issues temporary 6-digit dynamic token with 15-minute expiration → User approaches Rawbank ATM → Enters mobile number and dynamic token → ATM dispenses physical cash without card insertion.*
* **Agency Banking Cash-In / Cash-Out:**  
  *Customer presents cash or phone at Rawbank Express Agent → Agent initiates transaction on agent terminal → Customer receives confirmation prompt/OTP on personal phone → Funds debited from wallet and handed over as physical cash (or vice versa).*
* **Corporate Bulk Payroll Processing:**  
  *Finance officer uploads encrypted batch file via RawbankOnline → System performs pre-validation → Secondary authorizer signs batch via hardware token / 2FA → Overnight or real-time batch execution disbursing salaries across thousands of individual CDF/USD accounts.*
* **Cross-Border SWIFT Outward Remittance:**  
  *Corporate client initiates international transfer → Mandatory AML/sanctions screening against OFAC/UN lists → Manual/automated compliance review → SWIFT MT103 / ISO 20022 message dispatch.*

---

### 6. Customer Touchpoints & Interaction Nodes

* **Digital Interfaces:** Native mobile apps (iOS, Android), responsive web browsers (Chrome, Edge, Safari), USSD gateway sessions.
* **Physical Touchpoints:** 100+ full-service branch offices, standalone ATM vestibules, thousands of authorized Rawbank Express agent booths.
* **Operational Touchpoints:** 24/7 Customer Care Center (Voice, WhatsApp Business, Email), Dedicated Fraud Reporting Hotline, Corporate Relationship Managers.
* **Authentication Intermediaries:** Telecom SMS OTP gateways (Vodacom, Airtel, Orange, Africell), hardware tokens, software authenticator apps, biometric face/fingerprint validation on secure mobile enclaves.

---

### 7. Geographic & Macroeconomic Context

* **Country:** Democratic Republic of the Congo (DRC) — Central Africa.
* **Key Economic Corridors [Verified Public Research]:**
  * **Kinshasa:** Political, commercial, and financial capital; largest volume of retail consumer transactions and digital wallet adoption.
  * **Haut-Katanga & Lualaba (Lubumbashi, Kolwezi):** Industrial mining epicenter (copper and cobalt); predominant driver of massive corporate wire transfers, high-value payrolls, and contractor payments.
  * **North & South Kivu (Goma, Bukavu):** Eastern trade hubs with cross-border commerce (Rwanda, Uganda); high velocity of mobile money and micro-trade remittances.
  * **Kongo Central (Matadi, Boma):** Maritime logistics gateway handling import-export customs duties and port-related transactions.
* **Infrastructural Dynamics [Verified Public Research]:**
  * Variable cellular network latency across remote mining regions vs. high-speed 4G/LTE in urban Kinshasa and Lubumbashi.
  * Predominance of prepaid mobile subscriptions, making SIM swap detection and telecom carrier verification critical.
  * Multi-lingual customer base (French as official business language, Lingala in Kinshasa/West, Swahili in Katanga/East, Kikongo, Tshiluba).

---

### 8. Potential Fraud Surfaces & Threat Vectors

* **Vector 1: Account Takeover (ATO) & SIM Swapping [BFSI Standard Threat]:** Fraudsters compromise subscriber SIM cards via corrupted telecom agent workflows, intercepting SMS OTPs to log into IllicoCash or reset passwords from unauthorized devices.
* **Vector 2: Cardless ATM Exploitation [BFSI Standard Threat]:** Exploiting social engineering to trick victims into sharing dynamic one-time cardless withdrawal codes, resulting in immediate unrecoverable cash-out at unattended ATMs.
* **Vector 3: Mule Networks & Structuring (Smurfing) [BFSI Standard Threat]:** Illicit syndicates rapidly funnel stolen corporate or retail funds across 10–50 freshly registered retail or student accounts in amounts just below BCC AML declaration thresholds ($10,000 equivalent), swiftly withdrawing cash at disparate agent kiosks.
* **Vector 4: Rogue Agent Collusion [BFSI Standard Threat]:** Dishonest agency banking operators facilitating unauthorized cash-outs, pocketing customer deposits without ledger entry, or fabricating float credit.
* **Vector 5: Corporate Bulk Payroll Tampering [BFSI Standard Threat]:** Compromised corporate credentials altering payroll batch destination accounts right before authorization, redirecting payroll funds to temporary mule accounts.
* **Vector 6: FX Rate Arbitrage & Velocity Abuse [BFSI Standard Threat]:** Exploiting micro-latency or parallel-market exchange rate spreads between CDF and USD via high-velocity cyclic conversions.

---

### 9. Digital Banking Context

* **Cash-to-Digital Transition:** The DRC economy is rapidly modernizing from a cash-heavy environment to digital-first mobile wallets. This rapid shift creates a wide spectrum of user digital literacy—increasing vulnerability to social engineering and credential leakage.
* **Device Characteristics:** Widespread prevalence of Android-based entry-to-mid-tier smartphones, shared family mobile devices, and frequent SIM card swapping on dual-SIM devices. Fraud models must evaluate hardware fingerprinting (IMEI, Device UUID) alongside network identifiers.
* **Offline / Intermittent Connectivity:** System design must accommodate asynchronous synchronization and out-of-order event timestamps from remote agency terminals.

---

### 10. Operational Context for Fraud Monitoring

* **Fraud Operations Center (Fraud Ops / SOC) [Assumptions Requiring Validation]:**
  * Operates 24/7 with Tier-1 triage analysts monitoring real-time queues and Tier-2 forensic investigators handling complex escalations.
  * Target triage latency: Critical alerts must be evaluated within minutes to intercept cash-out before final settlement.
* **Analyst Cognitive Fatigue:** High false-positive rates cause operational paralysis. Deterministic rules must filter out noise, while the AI intelligence layer must synthesize multi-hop evidence and provide actionable hypotheses.
* **Regulatory Compliance (Banque Centrale du Congo):** Suspicious Activity Reports (SARs) and Currency Transaction Reports (CTRs) must be fully auditable with verifiable timestamps, immutable ledger trails, and deterministic evidence justifications.

---

### 11. Traceability & Assumptions Matrix

| Topic / Element | Source Classification | Notes & Action Required |
| :--- | :--- | :--- |
| Bank Identity & DRC Context | Verified Public Research | Grounded in official Rawbank releases, BCC reports, and economic publications. |
| IllicoCash & Channel Ecosystem | Verified Public Research | Grounded in official IllicoCash documentation and app capabilities. |
| Synthetic Data Mandate | Supplied by Assignment | Strict constraint: 100% synthetic data; zero real customer PII. |
| Two Connected Experiences | Supplied by Assignment | Command Centre + Investigation Copilot operating on single environment. |
| Specific Rule Threshold Values | Assumptions Requiring Validation | Default placeholders provided; will synchronize with `SentientData_RuleSet.md` when supplied. |
| Synthetic Record Volumes (2,500) | Supplied by Assignment | Explicitly scheduled for Phase 2 implementation. |
