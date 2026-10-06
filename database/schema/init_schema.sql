-- ==============================================================================
-- Rawbank Sentient Fraud Intelligence Platform
-- Phase 2 Relational Database Schema (SQLite 3 DDL)
-- All tables and fields are strictly SYNTHETIC and designed for demonstration.
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    customer_segment TEXT NOT NULL CHECK(customer_segment IN ('Retail', 'HNWI', 'SME', 'Corporate', 'AgencyBankingOperator')),
    kyc_status TEXT NOT NULL CHECK(kyc_status IN ('Tier_1_Basic', 'Tier_2_Standard', 'Tier_3_Full')),
    primary_phone TEXT NOT NULL,
    email TEXT NOT NULL,
    registered_city TEXT NOT NULL CHECK(registered_city IN ('Kinshasa', 'Lubumbashi', 'Kolwezi', 'Goma', 'Matadi', 'Bukavu')),
    risk_category TEXT NOT NULL CHECK(risk_category IN ('Low', 'Medium', 'High')),
    created_at TEXT NOT NULL
);

-- 2. Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_type TEXT NOT NULL CHECK(account_type IN ('Current_Checking', 'Savings_Deposit', 'IllicoCash_Mobile_Wallet', 'Agent_Float_Ledger')),
    currency TEXT NOT NULL CHECK(currency IN ('CDF', 'USD')),
    current_balance REAL NOT NULL CHECK(current_balance >= 0.0),
    available_balance REAL NOT NULL CHECK(available_balance >= 0.0),
    account_status TEXT NOT NULL CHECK(account_status IN ('Active', 'Dormant', 'Frozen', 'Under_Investigation')),
    created_at TEXT NOT NULL
);

-- 3. Devices Table
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    primary_customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    device_type TEXT NOT NULL CHECK(device_type IN ('Mobile_Android', 'Mobile_iOS', 'Desktop_Windows', 'Desktop_Mac')),
    device_model TEXT NOT NULL,
    os_version TEXT NOT NULL,
    device_fingerprint_hash TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    ip_city TEXT NOT NULL,
    is_vpn_or_tor INTEGER NOT NULL DEFAULT 0 CHECK(is_vpn_or_tor IN (0, 1)),
    is_rooted_jailbroken INTEGER NOT NULL DEFAULT 0 CHECK(is_rooted_jailbroken IN (0, 1)),
    trust_status TEXT NOT NULL CHECK(trust_status IN ('Trusted_Enrolled', 'New_Unverified', 'Suspicious_Blacklisted')),
    first_seen_timestamp TEXT NOT NULL,
    last_seen_timestamp TEXT NOT NULL
);

-- 4. Beneficiaries Table
CREATE TABLE IF NOT EXISTS beneficiaries (
    beneficiary_id TEXT PRIMARY KEY,
    beneficiary_name TEXT NOT NULL,
    institution_name TEXT NOT NULL,
    account_or_phone TEXT NOT NULL,
    beneficiary_type TEXT NOT NULL CHECK(beneficiary_type IN ('Individual_Peer', 'Merchant_Store', 'Corporate_Vendor', 'Mobile_Money_Agent')),
    registered_city TEXT NOT NULL,
    is_known_mule INTEGER NOT NULL DEFAULT 0 CHECK(is_known_mule IN (0, 1)),
    created_at TEXT NOT NULL
);

-- 5. Behavioural Baselines Table
CREATE TABLE IF NOT EXISTS behavioural_baselines (
    baseline_id TEXT PRIMARY KEY,
    customer_id TEXT UNIQUE NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    avg_monthly_volume_usd REAL NOT NULL,
    avg_tx_amount_usd REAL NOT NULL,
    max_single_tx_amount_usd REAL NOT NULL,
    typical_active_hours_utc TEXT NOT NULL,
    common_channels TEXT NOT NULL,
    frequent_beneficiary_ids TEXT NOT NULL,
    frequent_cities TEXT NOT NULL,
    last_calculated_at TEXT NOT NULL
);

-- 6. Authentication Activities Table
CREATE TABLE IF NOT EXISTS auth_activities (
    activity_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    event_type TEXT NOT NULL CHECK(event_type IN ('Login_Success', 'Login_Failed_InvalidPIN', 'OTP_Requested', 'OTP_Verified', 'Password_Reset_Triggered', 'Biometric_Auth_Success', 'Device_Enrolled', 'Beneficiary_Added')),
    channel TEXT NOT NULL CHECK(channel IN ('IllicoCash_App', 'RawbankOnline_Web')),
    ip_address TEXT NOT NULL,
    ip_city TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Success', 'Failed', 'Challenge_Required')),
    failure_reason TEXT,
    timestamp TEXT NOT NULL
);

-- 7. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    beneficiary_id TEXT NOT NULL REFERENCES beneficiaries(beneficiary_id),
    device_id TEXT NOT NULL REFERENCES devices(device_id),
    channel TEXT NOT NULL CHECK(channel IN ('IllicoCash_App', 'RawbankOnline_Web', 'ATM_Cardless', 'Agency_Express_POS', 'SWIFT_Wire')),
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('P2P_Transfer', 'Merchant_Payment', 'Cardless_CashOut', 'Agent_CashOut', 'Agent_CashIn', 'Bulk_Payroll_Disbursement', 'FX_Conversion', 'Bill_Payment')),
    amount REAL NOT NULL CHECK(amount > 0.0),
    currency TEXT NOT NULL CHECK(currency IN ('CDF', 'USD')),
    amount_usd_equivalent REAL NOT NULL CHECK(amount_usd_equivalent > 0.0),
    location_city TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Completed', 'Pending_Review', 'Blocked_Declined')),
    timestamp TEXT NOT NULL
);

-- 8. Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    account_id TEXT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    severity TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    composite_risk_score INTEGER NOT NULL CHECK(composite_risk_score BETWEEN 0 AND 100),
    status TEXT NOT NULL CHECK(status IN ('NEW_UNASSIGNED', 'UNDER_INVESTIGATION', 'ESCALATED_AML', 'DISMISSED_FALSE_POSITIVE', 'RESOLVED_CONFIRMED_FRAUD')),
    reason_summary TEXT NOT NULL,
    scenario_type TEXT NOT NULL,
    assigned_analyst TEXT,
    created_at TEXT NOT NULL
);

-- 9. Fraud Signals Table
CREATE TABLE IF NOT EXISTS fraud_signals (
    signal_id TEXT PRIMARY KEY,
    alert_id TEXT NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    rule_code TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    rule_category TEXT NOT NULL CHECK(rule_category IN ('Velocity', 'Device_Risk', 'Geographic_Travel', 'Mule_Network', 'Credential_ATO', 'Structuring', 'Value_Spike', 'Auth_Anomaly')),
    severity TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    confidence_score REAL NOT NULL CHECK(confidence_score BETWEEN 0.0 AND 1.0),
    signal_description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Indexes for Query & Relationship Performance
CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_beneficiary_id ON transactions(beneficiary_id);
CREATE INDEX IF NOT EXISTS idx_transactions_device_id ON transactions(device_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_auth_activities_customer_id ON auth_activities(customer_id);
CREATE INDEX IF NOT EXISTS idx_auth_activities_device_id ON auth_activities(device_id);
CREATE INDEX IF NOT EXISTS idx_alerts_transaction_id ON alerts(transaction_id);
CREATE INDEX IF NOT EXISTS idx_alerts_customer_id ON alerts(customer_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_fraud_signals_alert_id ON fraud_signals(alert_id);
CREATE INDEX IF NOT EXISTS idx_fraud_signals_rule_code ON fraud_signals(rule_code);
