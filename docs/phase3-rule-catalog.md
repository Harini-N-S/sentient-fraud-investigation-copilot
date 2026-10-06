# Phase 3 Deterministic Rule Catalogue
## Sentient Fraud Intelligence Platform (Rawbank DRC)

**Document Reference:** `docs/phase3-rule-catalog.md`  
**Execution Phase:** Phase 3 — Deterministic Fraud Intelligence  
**Rule Framework:** Pure Deterministic Python (`rules/`)  
**Resource Pack Availability:** Authoritative assignment resource pack (`SentientData_RuleSet.md`) is **NOT AVAILABLE**.

> [!CAUTION]
> **GOVERNANCE & AUDIT NOTICE**  
> All rule IDs, threshold values, formulas, and weights documented herein are:  
> **`[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`**  
> Under no circumstances should these rules be represented as official proprietary rules of Rawbank SA or official assignment rules. If the authoritative `SentientData_RuleSet.md` is supplied in a later phase, these rules can be updated without redesigning the architecture.

---

### Master Rule Inventory

| Rule Code | Rule Name | Category | Base Weight | Default Severity | Status |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **`R-VEL-01`** | High-Frequency Transaction Velocity Burst | Velocity | 25 | HIGH | [PROJECT ASSUMPTION] |
| **`R-VAL-07`** | Unusually Large Transaction Value Spike | Value_Spike | 20 | HIGH | [PROJECT ASSUMPTION] |
| **`R-DEV-02`** | Unverified or Novel Device Access | Device_Risk | 15 | MEDIUM | [PROJECT ASSUMPTION] |
| **`R-DEV-SHR-01`** | Shared Hardware Device Across Disparate Accounts | Device_Risk | 25 | HIGH | [PROJECT ASSUMPTION] |
| **`R-BEN-03`** | First-Time Recipient Beneficiary Transfer | Mule_Network | 15 | LOW | [PROJECT ASSUMPTION] |
| **`R-MULE-04`** | Multiple-Customer Beneficiary Concentration | Mule_Network | 25 | HIGH | [PROJECT ASSUMPTION] |
| **`R-GEO-03`** | Impossible Geographic Travel Velocity | Geographic_Travel | 35 | CRITICAL | [PROJECT ASSUMPTION] |
| **`R-SMURF-06`** | Near-Threshold Structuring Pattern | Structuring | 25 | HIGH | [PROJECT ASSUMPTION] |
| **`R-AUTH-08`** | Consecutive Failed Authentication Attempts | Auth_Anomaly | 20 | HIGH | [PROJECT ASSUMPTION] |
| **`R-ATO-05`** | Critical Security Event Preceding Transfer | Credential_ATO | 35 | CRITICAL | [PROJECT ASSUMPTION] |
| **`R-BEH-09`** | Customer Profile Behavioural Deviation | Value_Spike | 15 | MEDIUM | [PROJECT ASSUMPTION] |

---

### Detailed Rule Specifications

---

#### 1. Rule `R-VEL-01`: High-Frequency Transaction Velocity Burst
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects automated or urgent account liquidation via high-frequency successive outbound transfers.
* **Input Tables:** `transactions`
* **Calculation:**  
  $$\text{Count}(T_i) \quad \text{where } T_i.\text{customer\_id} = C \text{ and } T_i.\text{timestamp} \in [t - W, t]$$
  where $W = 300\text{ seconds}$ (5 minutes).
* **Threshold:** $\ge 4\text{ transactions}$ within 300 seconds (or $\ge 6$ for CRITICAL).
* **Output Signal:** `SIG-XXXXX` with category `Velocity` and confidence $0.75 + (N \times 0.04)$.
* **Evidence Generated:** `transaction_count`, `window_threshold_seconds`, `observed_elapsed_seconds`, `total_volume_usd`, `transaction_ids`.
* **Severity Contribution:** +25 risk points (HIGH) or +35 risk points (CRITICAL if count $\ge 6$).
* **False-Positive Considerations:** Batch corporate payroll or merchant point-of-sale rapid scanning (mitigated if customer is Corporate/Merchant segment).
* **Example Positive Case:** `TXN-00807` (Customer `CUS-00022` executed 5 transfers in 240 seconds totaling $27,270 USD).
* **Example Negative Case:** `TXN-00001` (Routine standalone retail transaction).

---

#### 2. Rule `R-VAL-07`: Unusually Large Transaction Value Spike
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects sudden anomalous transfers that drastically exceed the customer’s historical spending capacity.
* **Input Tables:** `transactions`, `behavioural_baselines`, `customers`
* **Calculation:**  
  $$\text{DeviationPct} = \left(\frac{T.\text{amount\_usd\_equivalent}}{\text{Baseline}.\text{avg\_tx\_amount\_usd}}\right) \times 100$$
  $$\text{RatioToMax} = \frac{T.\text{amount\_usd\_equivalent}}{\text{Baseline}.\text{max\_single\_tx\_amount\_usd}}$$
* **Threshold:** $T \ge \$250\text{ USD}$ AND ($\text{DeviationPct} \ge 400\%$ OR $\text{RatioToMax} \ge 1.5$).
* **Output Signal:** `SIG-XXXXX` with category `Value_Spike` and confidence $0.75\text{--}0.95$.
* **Evidence Generated:** `current_amount_usd`, `baseline_avg_amount_usd`, `baseline_max_amount_usd`, `deviation_percentage`, `ratio_to_historical_max`.
* **Severity Contribution:** +20 risk points (HIGH) or +30 risk points (CRITICAL if ratio $\ge 3.0$).
* **False-Positive Considerations:** High-net-worth annual tax payment or legitimate corporate capital equipment purchase.
* **Example Positive Case:** `TXN-00801` ($4,800 USD transfer on account with $260 USD baseline average = 1,846% deviation).
* **Example Negative Case:** `TXN-00005` (Routine retail payment matching baseline average).

---

#### 3. Rule `R-DEV-02`: Unverified or Novel Device Access
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Flags transactions originating from hardware never before seen in the customer's transaction history or marked untrusted.
* **Input Tables:** `transactions`, `devices`
* **Calculation:**  
  Evaluate if `Device.trust_status` $\in \{\text{'New\_Unverified'}, \text{'Suspicious\_Blacklisted'}\}$ OR $\text{AgeHours} \le 24.0$ OR `device_id` $\notin \text{CustomerDeviceHistory}$.
* **Threshold:** First observation within 24 hours of transaction or blacklisted/VPN flags.
* **Output Signal:** `SIG-XXXXX` with category `Device_Risk`.
* **Evidence Generated:** `device_id`, `device_model`, `trust_status`, `device_age_hours_at_tx`, `is_vpn_or_tor`, `is_rooted_jailbroken`, `ip_address`.
* **Severity Contribution:** +15 risk points (MEDIUM) up to +30 risk points (CRITICAL if VPN/rooted).
* **False-Positive Considerations:** Customer legitimately purchased and enrolled a new smartphone.
* **Example Positive Case:** `TXN-00801` (Initiated via `DEV-00127`, trust status `New_Unverified`, first seen 0.2 hours prior).
* **Example Negative Case:** `TXN-00001` (Initiated via customer's primary enrolled `Trusted_Enrolled` device).

---

#### 4. Rule `R-DEV-SHR-01`: Shared Hardware Device Across Disparate Accounts
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Identifies hardware fingerprints linked to multiple distinct banking customers (syndicate / mule ring detection).
* **Input Tables:** `transactions`, `devices`
* **Calculation:**  
  $$\text{DistinctCustomers}(D) = \text{Count}(\text{DISTINCT } T.\text{customer\_id}) \quad \text{where } T.\text{device\_id} = D$$
* **Threshold:** $\ge 2\text{ distinct customers}$ on the same device.
* **Output Signal:** `SIG-XXXXX` with category `Device_Risk`.
* **Evidence Generated:** `device_id`, `distinct_customers_count`, `linked_customer_ids`, `total_transactions_on_device`, `total_volume_usd_on_device`.
* **Severity Contribution:** +25 risk points (HIGH) or +35 risk points (CRITICAL if $\ge 4$ customers).
* **False-Positive Considerations:** Agency banking terminal or shared family smartphone in low-income households.
* **Example Positive Case:** `TXN-00808` (`DEV-00125` utilized by 4 distinct customers within 48 hours moving $12,800 USD).
* **Example Negative Case:** `TXN-00001` (`DEV-00001` exclusive to customer `CUS-00001`).

---

#### 5. Rule `R-BEN-03`: First-Time Recipient Beneficiary Transfer
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects initial transfer events to unfamiliar beneficiaries.
* **Input Tables:** `transactions`, `beneficiaries`
* **Calculation:**  
  $$\text{PriorTransfers}(C, B) = \text{Count}(T) \quad \text{where } T.\text{customer\_id} = C \land T.\text{beneficiary\_id} = B \land T.\text{timestamp} < t$$
* **Threshold:** $\text{PriorTransfers} = 0$.
* **Output Signal:** `SIG-XXXXX` with category `Mule_Network`.
* **Evidence Generated:** `beneficiary_id`, `beneficiary_name`, `institution_name`, `is_known_mule_flag`, `transfer_amount_usd`.
* **Severity Contribution:** +15 risk points (LOW) or +30 risk points (CRITICAL if `is_known_mule` = 1).
* **False-Positive Considerations:** Everyday routine new payee addition (e.g. paying a new merchant).
* **Example Positive Case:** `TXN-00801` (First transfer to rogue counterparty `BEN-00088`).
* **Example Negative Case:** Recurring payment to established merchant supermarket.

---

#### 6. Rule `R-MULE-04`: Multiple-Customer Beneficiary Concentration
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Uncovers money mule aggregators receiving inbound funds from multiple unrelated accounts.
* **Input Tables:** `transactions`, `beneficiaries`
* **Calculation:**  
  $$\text{DistinctSenders}(B) = \text{Count}(\text{DISTINCT } T.\text{customer\_id}) \quad \text{where } T.\text{beneficiary\_id} = B$$
* **Threshold:** $\ge 3\text{ distinct senders}$ (or $\ge 6$ for CRITICAL).
* **Output Signal:** `SIG-XXXXX` with category `Mule_Network`.
* **Evidence Generated:** `beneficiary_id`, `beneficiary_name`, `distinct_senders_count`, `sender_customer_ids`, `total_inbound_transactions`, `total_aggregated_volume_usd`.
* **Severity Contribution:** +25 risk points (HIGH) or +35 risk points (CRITICAL).
* **False-Positive Considerations:** Legitimate utility merchant (e.g. SNEL electricity or Canal+ subscriptions).
* **Example Positive Case:** `TXN-00812` (Beneficiary `BEN-00050` receiving inbound transfers from 6 distinct senders).
* **Example Negative Case:** Standalone P2P recipient receiving money from a single family member.

---

#### 7. Rule `R-GEO-03`: Impossible Geographic Travel Velocity
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects physically impossible human transit between consecutive transactions or sessions.
* **Input Tables:** `transactions`, `auth_activities`
* **Calculation:**  
  $$\text{Distance} = \text{GeodesicTable}(\text{City}_1, \text{City}_2)$$
  $$\text{ElapsedHours} = \frac{T_2.\text{timestamp} - T_1.\text{timestamp}}{3600}$$
  $$\text{ImpliedSpeed} = \frac{\text{Distance}}{\text{ElapsedHours}} \quad (\text{km/h})$$
* **Threshold:** $\text{ImpliedSpeed} > 600.0\text{ km/h}$ (exceeds commercial passenger aviation turnaround velocity).
* **Output Signal:** `SIG-XXXXX` with category `Geographic_Travel`.
* **Evidence Generated:** `current_location`, `previous_location`, `distance_km`, `elapsed_time_minutes`, `implied_speed_kmh`, `speed_threshold_kmh`.
* **Severity Contribution:** +35 risk points (CRITICAL).
* **False-Positive Considerations:** Multi-user shared corporate accounts across branch offices.
* **Example Positive Case:** `TXN-00820` (Kinshasa POS at 14:10 UTC followed by Lubumbashi ATM at 14:40 UTC: 1,560 km in 30 mins = 3,120 km/h).
* **Example Negative Case:** `TXN-00761` (Kinshasa to Lubumbashi transit over 3 days = ~21 km/h).

---

#### 8. Rule `R-SMURF-06`: Near-Threshold Structuring Pattern
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects intentional structuring / smurfing aimed at avoiding the BCC $10,000 AML declaration limit.
* **Input Tables:** `transactions`
* **Calculation:**  
  Identify $\ge 2\text{ transactions}$ within 4 hours where each transaction amount sits within $[85\%, 99.9\%]$ of the $\$10,000\text{ USD}$ threshold.
* **Threshold:** $\ge 2\text{ transactions}$ between $\$8,500$ and $\$9,999.99\text{ USD}$ within 4 hours.
* **Output Signal:** `SIG-XXXXX` with category `Structuring`.
* **Evidence Generated:** `reporting_threshold_usd`, `near_threshold_band_usd`, `cluster_transaction_count`, `individual_amounts_usd`, `total_combined_volume_usd`.
* **Severity Contribution:** +25 risk points (HIGH) or +35 risk points (CRITICAL).
* **False-Positive Considerations:** Multiple large legitimate invoices accidentally falling in the same price range.
* **Example Positive Case:** `TXN-00825` (Customer `CUS-00062` executed 4 sequential transfers of $9,400 to $9,800 USD within 60 mins).
* **Example Negative Case:** Single routine payment of $1,200 USD.

---

#### 9. Rule `R-AUTH-08`: Consecutive Failed Authentication Attempts
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects credential brute-forcing or PIN guessing attempts.
* **Input Tables:** `auth_activities`, `transactions`
* **Calculation:**  
  $$\text{FailedCount} = \text{Count}(\text{Auth}) \quad \text{where } \text{status} = \text{'Failed'} \land \text{timestamp} \in [t - 30\text{ mins}, t]$$
* **Threshold:** $\ge 3\text{ consecutive failed authentication attempts}$.
* **Output Signal:** `SIG-XXXXX` with category `Auth_Anomaly`.
* **Evidence Generated:** `failed_attempts_count`, `window_minutes`, `failed_activity_ids`, `failure_reasons`, `attempt_ips`.
* **Severity Contribution:** +20 risk points (HIGH) or +30 risk points (CRITICAL).
* **False-Positive Considerations:** Customer temporarily forgot PIN and successfully recovered credentials.
* **Example Positive Case:** `TXN-00821` (4 consecutive failed PIN attempts preceding ATM cash-out).
* **Example Negative Case:** `TXN-00001` (Clean login session with zero prior failures).

---

#### 10. Rule `R-ATO-05`: Critical Security Event Preceding Transfer
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects Account Takeover (ATO) sequence: administrative password reset or device binding immediately followed by liquidation.
* **Input Tables:** `auth_activities`, `transactions`
* **Calculation:**  
  Identify `Password_Reset_Triggered` or `Device_Enrolled` occurring within 60 minutes prior to transaction.
* **Threshold:** Administrative security event $\le 60\text{ minutes}$ before transaction.
* **Output Signal:** `SIG-XXXXX` with category `Credential_ATO`.
* **Evidence Generated:** `security_event_type`, `security_event_device_id`, `security_event_ip`, `elapsed_minutes_to_transaction`, `transaction_amount_usd`.
* **Severity Contribution:** +35 risk points (CRITICAL).
* **False-Positive Considerations:** Legitimate customer resetting password and immediately making an urgent planned payment.
* **Example Positive Case:** `TXN-00801` (Password reset on unverified Android device 15 mins prior to $4,800 drain).
* **Example Negative Case:** Regular payment without any preceding security credential alterations.

---

#### 11. Rule `R-BEH-09`: Customer Profile Behavioural Deviation
* **Status:** `[PROJECT ASSUMPTION — RESOURCE PACK UNAVAILABLE]`
* **Purpose:** Detects out-of-character behavior across time-of-day, channels, and geography.
* **Input Tables:** `transactions`, `behavioural_baselines`
* **Calculation:**  
  Check if transaction hour $\notin \text{Baseline}.\text{typical\_active\_hours\_utc}$, or channel $\notin \text{common\_channels}$.
* **Threshold:** Transaction initiated outside established active window with amount $\ge \$250\text{ USD}$.
* **Output Signal:** `SIG-XXXXX` with category `Value_Spike`.
* **Evidence Generated:** `transaction_time_utc`, `transaction_hour`, `normal_active_hours_range`, `deviation_type`.
* **Severity Contribution:** +12 to +20 risk points (MEDIUM/HIGH).
* **False-Positive Considerations:** Customer working night shifts or paying for an emergency medical situation.
* **Example Positive Case:** `TXN-00826` (Transaction initiated at 03:45 AM UTC when normal baseline hours are 08:00–18:00 UTC).
* **Example Negative Case:** `TXN-00015` (Midday 14:00 UTC transaction matching normal baseline).
