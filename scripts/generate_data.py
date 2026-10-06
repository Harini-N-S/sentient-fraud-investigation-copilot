#!/usr/bin/env python3
"""
Rawbank Sentient Fraud Intelligence Platform
Phase 2 Synthetic Banking Data Generator
-----------------------------------------------------------------------------
Generates a realistic, deterministic, fully interconnected synthetic banking
environment representing Rawbank's Congolese operating context (CDF/USD).

Target: Exactly 2,500 records across 9 relational tables:
  1. customers:             120
  2. accounts:              240
  3. devices:               150
  4. beneficiaries:         180
  5. behavioural_baselines: 120
  6. auth_activities:       450
  7. transactions:          900
  8. fraud_signals:         200
  9. alerts:                140
  Total:                  2,500 records

ALL DATA IS 100% SYNTHETIC. NO REAL CUSTOMER PII OR VULNERABILITY DATA IS USED.
"""

import os
import sys
import json
import random
import sqlite3
import hashlib
from datetime import datetime, timedelta

# Fixed seed for 100% deterministic reproducibility
SEED = 42
random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema", "init_schema.sql")
DB_PATH = os.path.join(BASE_DIR, "database", "synthetic_bank.db")
DATA_DIR = os.path.join(BASE_DIR, "data", "synthetic")

# DRC Geographic Centers
CITIES = ["Kinshasa", "Lubumbashi", "Kolwezi", "Goma", "Matadi", "Bukavu"]
CITY_WEIGHTS = [0.50, 0.25, 0.10, 0.08, 0.05, 0.02]

# First and Last Names for DRC synthetic profiles
FIRST_NAMES = [
    "Jean", "Patrice", "Dieudonné", "Kavira", "Mireille", "Ephrem", "Bibiche", 
    "Moïse", "Christian", "Espérance", "Fabrice", "Bijou", "Guylain", "Dorcas", 
    "Serge", "Naomie", "Alain", "Chantal", "Rodrigue", "Fifi", "Aimé", "Solange",
    "Godefroid", "Nadine", "Yannick", "Clarisse", "Blaise", "Rachel", "Arsène", "Christelle"
]
LAST_NAMES = [
    "Ilunga", "Kalombo", "Mwamba", "Mutombo", "Tshisekedi", "Kabila", "Lumumba",
    "Mukendi", "Mbuyi", "Kasongo", "Kazadi", "Ngoy", "Kanyinda", "Bondo", "Kanku",
    "Masika", "Kambale", "Kavugho", "Lukusa", "Tshimanga", "Yav", "Muteba", "Kyungu"
]

CUSTOMER_SEGMENTS = ["Retail", "HNWI", "SME", "Corporate", "AgencyBankingOperator"]
SEGMENT_WEIGHTS = [0.65, 0.08, 0.15, 0.04, 0.08]

INSTITUTIONS = [
    "Rawbank_Internal", "Vodacom_M_Pesa", "Airtel_Money", 
    "Orange_Money", "EquityBCDC", "Standard_Bank"
]

DEVICE_MODELS = [
    ("Mobile_Android", "Samsung Galaxy A14", "Android 13"),
    ("Mobile_Android", "Tecno Spark 10", "Android 12"),
    ("Mobile_Android", "Infinix Hot 30", "Android 13"),
    ("Mobile_Android", "Xiaomi Redmi 12", "Android 13"),
    ("Mobile_iOS", "Apple iPhone 13", "iOS 17.2"),
    ("Mobile_iOS", "Apple iPhone 14 Pro", "iOS 17.4"),
    ("Desktop_Windows", "Dell Latitude 5420", "Windows 11"),
    ("Desktop_Windows", "HP ProBook 450", "Windows 10"),
    ("Desktop_Mac", "Apple MacBook Pro M2", "macOS Sonoma")
]

CHANNELS = ["IllicoCash_App", "RawbankOnline_Web", "ATM_Cardless", "Agency_Express_POS", "SWIFT_Wire"]

BASE_DATE = datetime(2026, 9, 1, 0, 0, 0)


def gen_phone(prefix="81"):
    return f"+243-{prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def gen_email(first, last, index):
    clean_first = first.lower().replace("ï", "i").replace("é", "e").replace("è", "e")
    clean_last = last.lower().replace("ï", "i").replace("é", "e").replace("è", "e")
    domains = ["gmail.com", "yahoo.fr", "outlook.com", "rawbank-client.cd", "mining-katanga.cd"]
    return f"{clean_first}.{clean_last}{index}@{random.choice(domains)}"


def gen_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main():
    print("=" * 70)
    print("RAWBANK SENTIENT FRAUD INTELLIGENCE PLATFORM — PHASE 2 DATA GENERATION")
    print("=" * 70)
    print(f"Random seed set to: {SEED}")
    print(f"Target Database: {DB_PATH}")

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed previous database instance at {DB_PATH}")

    # Initialize SQLite Database Schema
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    print("Database schema successfully applied from init_schema.sql.")

    cursor = conn.cursor()

    # -------------------------------------------------------------------------
    # 1. GENERATE CUSTOMERS (120 records)
    # -------------------------------------------------------------------------
    print("Generating 120 customers...")
    customers = []
    for i in range(1, 121):
        cid = f"CUS-{i:05d}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        full_name = f"{fn} {ln}"
        seg = random.choices(CUSTOMER_SEGMENTS, weights=SEGMENT_WEIGHTS, k=1)[0]
        
        # Segment-specific KYC & risk
        if seg == "Retail":
            kyc = random.choices(["Tier_1_Basic", "Tier_2_Standard"], weights=[0.4, 0.6])[0]
            risk = random.choices(["Low", "Medium", "High"], weights=[0.75, 0.20, 0.05])[0]
        elif seg == "HNWI":
            kyc = "Tier_3_Full"
            risk = random.choices(["Low", "Medium"], weights=[0.8, 0.2])[0]
        elif seg == "SME":
            kyc = random.choices(["Tier_2_Standard", "Tier_3_Full"], weights=[0.3, 0.7])[0]
            risk = random.choices(["Low", "Medium", "High"], weights=[0.6, 0.3, 0.1])[0]
        elif seg == "Corporate":
            kyc = "Tier_3_Full"
            risk = "Low"
        else: # AgencyBankingOperator
            kyc = "Tier_3_Full"
            risk = random.choices(["Low", "Medium", "High"], weights=[0.5, 0.35, 0.15])[0]

        city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
        created_dt = BASE_DATE - timedelta(days=random.randint(60, 700))
        phone = gen_phone(random.choice(["81", "82", "85", "89", "99"]))
        email = gen_email(fn, ln, i)

        cust_rec = (cid, full_name, seg, kyc, phone, email, city, risk, created_dt.isoformat())
        customers.append(cust_rec)

    cursor.executemany("""
        INSERT INTO customers (customer_id, full_name, customer_segment, kyc_status, primary_phone, email, registered_city, risk_category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, customers)
    print("  -> Inserted 120 customers.")

    # -------------------------------------------------------------------------
    # 2. GENERATE ACCOUNTS (240 records: 2 per customer - 1 CDF, 1 USD)
    # -------------------------------------------------------------------------
    print("Generating 240 accounts (1 CDF and 1 USD per customer)...")
    accounts = []
    acc_idx = 1
    for c in customers:
        cid = c[0]
        seg = c[2]
        
        # Account 1: CDF Account (Current or Mobile Wallet)
        acc_id_cdf = f"ACC-{acc_idx:05d}"
        acc_idx += 1
        acc_type_cdf = "IllicoCash_Mobile_Wallet" if seg == "Retail" else ("Agent_Float_Ledger" if seg == "AgencyBankingOperator" else "Current_Checking")
        bal_cdf = random.randint(500000, 35000000) if seg in ["Retail", "SME"] else random.randint(25000000, 250000000)
        accounts.append((acc_id_cdf, cid, acc_type_cdf, "CDF", float(bal_cdf), float(bal_cdf), "Active", c[8]))

        # Account 2: USD Account (Savings or Current)
        acc_id_usd = f"ACC-{acc_idx:05d}"
        acc_idx += 1
        acc_type_usd = "Savings_Deposit" if seg in ["Retail", "HNWI"] else "Current_Checking"
        bal_usd = random.randint(200, 15000) if seg == "Retail" else (random.randint(15000, 120000) if seg == "HNWI" else random.randint(10000, 85000))
        accounts.append((acc_id_usd, cid, acc_type_usd, "USD", float(bal_usd), float(bal_usd), "Active", c[8]))

    cursor.executemany("""
        INSERT INTO accounts (account_id, customer_id, account_type, currency, current_balance, available_balance, account_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, accounts)
    print("  -> Inserted 240 accounts.")

    # -------------------------------------------------------------------------
    # 3. GENERATE DEVICES (150 records)
    # -------------------------------------------------------------------------
    print("Generating 150 devices...")
    devices = []
    # Assign 1 device to each of the 120 customers (120 devices)
    for i in range(1, 121):
        dev_id = f"DEV-{i:05d}"
        cid = f"CUS-{i:05d}"
        dtype, dmodel, os_ver = random.choice(DEVICE_MODELS)
        cust_city = customers[i-1][6]
        ip = f"197.234.{random.randint(1, 254)}.{random.randint(1, 254)}"
        fp = gen_hash(f"{dev_id}-{dmodel}-{cid}")
        first_seen = (BASE_DATE - timedelta(days=random.randint(30, 300))).isoformat()
        last_seen = (BASE_DATE + timedelta(days=28, hours=random.randint(1, 23))).isoformat()
        devices.append((dev_id, cid, dtype, dmodel, os_ver, fp, ip, cust_city, 0, 0, "Trusted_Enrolled", first_seen, last_seen))

    # Add 30 additional devices (secondary phones, new unverified devices, and shared fraud devices)
    for i in range(121, 151):
        dev_id = f"DEV-{i:05d}"
        target_cust = random.randint(1, 120)
        cid = f"CUS-{target_cust:05d}"
        dtype, dmodel, os_ver = random.choice(DEVICE_MODELS)
        city = random.choice(CITIES)
        
        # Scenarios for specific devices:
        # DEV-00125: Shared syndicate device (Scenario C)
        # DEV-00126: Foreign VPN device (Scenario H)
        # DEV-00127: ATO attack device (Scenario A)
        if dev_id == "DEV-00125":
            cid = "CUS-00031" # Primary anchor
            trust = "Suspicious_Blacklisted"
            is_rooted = 1
            is_vpn = 0
            ip = "197.234.40.10"
            city = "Kinshasa"
        elif dev_id == "DEV-00126":
            cid = "CUS-00078"
            trust = "New_Unverified"
            is_rooted = 0
            is_vpn = 1
            ip = "185.220.101.44" # Known Tor / VPN exit node
            city = "Goma"
        elif dev_id == "DEV-00127":
            cid = "CUS-00014"
            trust = "New_Unverified"
            is_rooted = 0
            is_vpn = 0
            ip = "102.164.210.88"
            city = "Goma"
        else:
            trust = random.choices(["Trusted_Enrolled", "New_Unverified"], weights=[0.7, 0.3])[0]
            is_rooted = 0
            is_vpn = 1 if random.random() < 0.05 else 0
            ip = f"197.234.{random.randint(1, 254)}.{random.randint(1, 254)}"

        fp = gen_hash(f"{dev_id}-{dmodel}-{cid}")
        first_seen = (BASE_DATE - timedelta(days=random.randint(1, 45))).isoformat()
        last_seen = (BASE_DATE + timedelta(days=28, hours=random.randint(1, 23))).isoformat()
        devices.append((dev_id, cid, dtype, dmodel, os_ver, fp, ip, city, is_vpn, is_rooted, trust, first_seen, last_seen))

    cursor.executemany("""
        INSERT INTO devices (device_id, primary_customer_id, device_type, device_model, os_version, device_fingerprint_hash, ip_address, ip_city, is_vpn_or_tor, is_rooted_jailbroken, trust_status, first_seen_timestamp, last_seen_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, devices)
    print("  -> Inserted 150 devices.")

    # -------------------------------------------------------------------------
    # 4. GENERATE BENEFICIARIES (180 records)
    # -------------------------------------------------------------------------
    print("Generating 180 beneficiaries...")
    beneficiaries = []
    MERCHANT_NAMES = [
        "Kin-Mart Supermarché", "Alilac Alimentation", "Congo Motors SARL", 
        "Hôpital du Cinquantenaire", "Pharmacie Centrale Goma", "Kipushi Mining Logistics",
        "TotalEnergies Station Kinshasa", "Shoprite Lubumbashi", "Canal+ RDC", "SNEL Électricité"
    ]
    
    for i in range(1, 181):
        bid = f"BEN-{i:05d}"
        inst = random.choice(INSTITUTIONS)
        city = random.choices(CITIES, weights=CITY_WEIGHTS, k=1)[0]
        
        # Dedicated Scenarios:
        # BEN-00050: Mule aggregator (Scenario D)
        # BEN-00088: ATO rogue destination (Scenario A)
        if bid == "BEN-00050":
            bname = "Kavira Mule Aggregator"
            btype = "Mobile_Money_Agent"
            inst = "Vodacom_M_Pesa"
            acct_phone = "+243-81-999-0050"
            is_mule = 1
            city = "Goma"
        elif bid == "BEN-00088":
            bname = "Tshimanga Quick Cash"
            btype = "Individual_Peer"
            inst = "Airtel_Money"
            acct_phone = "+243-99-444-0088"
            is_mule = 1
            city = "Goma"
        elif i <= 30:
            bname = random.choice(MERCHANT_NAMES) + f" #{i}"
            btype = "Merchant_Store"
            acct_phone = f"MERCH-RAW-{i:04d}"
            is_mule = 0
        elif i <= 50:
            bname = f"Société Commerciale {random.choice(LAST_NAMES)} SARL"
            btype = "Corporate_Vendor"
            acct_phone = f"CORP-ACC-{i:04d}"
            is_mule = 0
        else:
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            bname = f"{fn} {ln}"
            btype = "Individual_Peer"
            acct_phone = gen_phone(random.choice(["81", "82", "85", "99"]))
            is_mule = 1 if i in [75, 92, 110] else 0

        created = (BASE_DATE - timedelta(days=random.randint(10, 400))).isoformat()
        beneficiaries.append((bid, bname, inst, acct_phone, btype, city, is_mule, created))

    cursor.executemany("""
        INSERT INTO beneficiaries (beneficiary_id, beneficiary_name, institution_name, account_or_phone, beneficiary_type, registered_city, is_known_mule, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, beneficiaries)
    print("  -> Inserted 180 beneficiaries.")

    # -------------------------------------------------------------------------
    # 5. GENERATE BEHAVIOURAL BASELINES (120 records: 1 per customer)
    # -------------------------------------------------------------------------
    print("Generating 120 behavioural baselines...")
    baselines = []
    for i in range(1, 121):
        base_id = f"BASE-{i:05d}"
        cid = f"CUS-{i:05d}"
        seg = customers[i-1][2]
        city = customers[i-1][6]

        if seg == "Retail":
            avg_vol = float(random.randint(300, 2200))
            avg_tx = float(random.randint(25, 180))
            max_tx = float(random.randint(250, 800))
            active_hours = json.dumps([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
            common_chans = json.dumps(["IllicoCash_App"])
        elif seg == "HNWI":
            avg_vol = float(random.randint(15000, 65000))
            avg_tx = float(random.randint(1200, 4500))
            max_tx = float(random.randint(12000, 35000))
            active_hours = json.dumps([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21])
            common_chans = json.dumps(["RawbankOnline_Web", "IllicoCash_App"])
        elif seg == "SME":
            avg_vol = float(random.randint(8000, 35000))
            avg_tx = float(random.randint(400, 1800))
            max_tx = float(random.randint(3000, 10000))
            active_hours = json.dumps([8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
            common_chans = json.dumps(["RawbankOnline_Web", "Agency_Express_POS"])
        elif seg == "Corporate":
            avg_vol = float(random.randint(80000, 450000))
            avg_tx = float(random.randint(8000, 35000))
            max_tx = float(random.randint(50000, 120000))
            active_hours = json.dumps([8, 9, 10, 11, 12, 13, 14, 15, 16])
            common_chans = json.dumps(["RawbankOnline_Web", "SWIFT_Wire"])
        else: # AgencyBankingOperator
            avg_vol = float(random.randint(25000, 95000))
            avg_tx = float(random.randint(250, 950))
            max_tx = float(random.randint(2500, 7500))
            active_hours = json.dumps([7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
            common_chans = json.dumps(["Agency_Express_POS", "IllicoCash_App"])

        # Frequent beneficiaries (pick 2-3)
        sample_bens = [f"BEN-{random.randint(1, 100):05d}" for _ in range(3)]
        freq_bens = json.dumps(sample_bens)
        freq_cities = json.dumps([city])
        last_calc = (BASE_DATE + timedelta(days=1)).isoformat()

        baselines.append((base_id, cid, avg_vol, avg_tx, max_tx, active_hours, common_chans, freq_bens, freq_cities, last_calc))

    cursor.executemany("""
        INSERT INTO behavioural_baselines (baseline_id, customer_id, avg_monthly_volume_usd, avg_tx_amount_usd, max_single_tx_amount_usd, typical_active_hours_utc, common_channels, frequent_beneficiary_ids, frequent_cities, last_calculated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, baselines)
    print("  -> Inserted 120 behavioural baselines.")

    # -------------------------------------------------------------------------
    # 6. GENERATE AUTHENTICATION ACTIVITIES (450 records)
    # -------------------------------------------------------------------------
    print("Generating 450 authentication/activity records...")
    auth_activities = []
    auth_idx = 1
    
    # Generate background normal logins across the 30-day window
    for _ in range(400):
        aid = f"AUTH-{auth_idx:05d}"
        auth_idx += 1
        cid_num = random.randint(1, 120)
        cid = f"CUS-{cid_num:05d}"
        dev_id = f"DEV-{cid_num:05d}" # Customer's primary device
        ev = random.choices(
            ["Login_Success", "OTP_Requested", "OTP_Verified", "Biometric_Auth_Success", "Login_Failed_InvalidPIN"],
            weights=[0.60, 0.15, 0.12, 0.10, 0.03]
        )[0]
        chan = "IllicoCash_App" if random.random() < 0.8 else "RawbankOnline_Web"
        cust_city = customers[cid_num-1][6]
        ip = f"197.234.{random.randint(1, 254)}.{random.randint(1, 254)}"
        status = "Failed" if ev == "Login_Failed_InvalidPIN" else "Success"
        reason = "Invalid PIN entered" if status == "Failed" else None
        ts = (BASE_DATE + timedelta(days=random.randint(1, 27), hours=random.randint(7, 21), minutes=random.randint(0, 59))).isoformat()
        auth_activities.append((aid, cid, dev_id, ev, chan, ip, cust_city, status, reason, ts))

    # Explicit Injected Auth Scenarios (50 records):
    # Scenario A: ATO on CUS-00014 via DEV-00127
    ato_ts = BASE_DATE + timedelta(days=15, hours=3, minutes=10)
    for ev, st, reas in [
        ("Login_Failed_InvalidPIN", "Failed", "Bad PIN attempt 1"),
        ("Login_Failed_InvalidPIN", "Failed", "Bad PIN attempt 2"),
        ("Password_Reset_Triggered", "Success", "Reset SMS intercepted"),
        ("Login_Success", "Success", None),
        ("Device_Enrolled", "Success", "New Android binding"),
        ("Beneficiary_Added", "Success", "BEN-00088 added")
    ]:
        aid = f"AUTH-{auth_idx:05d}"
        auth_idx += 1
        auth_activities.append((aid, "CUS-00014", "DEV-00127", ev, "IllicoCash_App", "102.164.210.88", "Goma", st, reas, ato_ts.isoformat()))
        ato_ts += timedelta(minutes=2)

    # Scenario F: Brute Force on CUS-00055 via DEV-00055
    bf_ts = BASE_DATE + timedelta(days=18, hours=22, minutes=5)
    for _ in range(4):
        aid = f"AUTH-{auth_idx:05d}"
        auth_idx += 1
        auth_activities.append((aid, "CUS-00055", "DEV-00055", "Login_Failed_InvalidPIN", "RawbankOnline_Web", "197.234.12.99", "Kinshasa", "Failed", "Consecutive invalid credentials", bf_ts.isoformat()))
        bf_ts += timedelta(seconds=45)
    # Then sudden login success
    aid = f"AUTH-{auth_idx:05d}"
    auth_idx += 1
    auth_activities.append((aid, "CUS-00055", "DEV-00055", "Login_Success", "RawbankOnline_Web", "197.234.12.99", "Kinshasa", "Success", None, (bf_ts + timedelta(minutes=1)).isoformat()))

    # Fill remaining to reach exactly 450
    while len(auth_activities) < 450:
        aid = f"AUTH-{auth_idx:05d}"
        auth_idx += 1
        cid_num = random.randint(1, 120)
        auth_activities.append((
            aid, f"CUS-{cid_num:05d}", f"DEV-{cid_num:05d}", "Login_Success", "IllicoCash_App",
            f"197.234.1.{random.randint(1, 200)}", customers[cid_num-1][6], "Success", None,
            (BASE_DATE + timedelta(days=random.randint(1, 25), hours=12)).isoformat()
        ))

    cursor.executemany("""
        INSERT INTO auth_activities (activity_id, customer_id, device_id, event_type, channel, ip_address, ip_city, status, failure_reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, auth_activities)
    print("  -> Inserted 450 authentication/activity records.")

    # -------------------------------------------------------------------------
    # 7. GENERATE TRANSACTIONS (900 records)
    # -------------------------------------------------------------------------
    print("Generating 900 transactions...")
    transactions = []
    txn_idx = 1
    
    # 750 Normal Background Transactions
    for _ in range(750):
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        
        cid_num = random.randint(1, 120)
        cid = f"CUS-{cid_num:05d}"
        cust = customers[cid_num-1]
        seg = cust[2]
        city = cust[6]
        
        # Pick CDF or USD account
        # Customer i has ACC-(2i-1) [CDF] and ACC-(2i) [USD]
        if random.random() < 0.60:
            aid = f"ACC-{(2*cid_num - 1):05d}"
            curr = "CDF"
            amt = float(random.randint(15000, 1500000)) if seg == "Retail" else float(random.randint(1500000, 25000000))
            amt_usd = round(amt / 2750.0, 2)
        else:
            aid = f"ACC-{(2*cid_num):05d}"
            curr = "USD"
            amt = float(random.randint(10, 600)) if seg == "Retail" else float(random.randint(500, 9500))
            amt_usd = amt

        bid = f"BEN-{random.randint(1, 120):05d}"
        dev_id = f"DEV-{cid_num:05d}"
        chan = random.choices(["IllicoCash_App", "Agency_Express_POS", "RawbankOnline_Web", "ATM_Cardless"], weights=[0.60, 0.15, 0.15, 0.10])[0]
        ttype = "Merchant_Payment" if int(bid.split("-")[1]) <= 30 else random.choice(["P2P_Transfer", "Bill_Payment", "Cardless_CashOut"])
        ts = (BASE_DATE + timedelta(days=random.randint(1, 26), hours=random.randint(7, 20), minutes=random.randint(0, 59))).isoformat()
        
        transactions.append((tid, aid, cid, bid, dev_id, chan, ttype, amt, curr, amt_usd, city, "Completed", ts))

    # Legitimate Anomalies (50 transactions)
    # 1. High-Value Corporate Payment
    for _ in range(10):
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        corp_cid = "CUS-00010" # Corporate customer
        aid = "ACC-00020" # Corporate USD
        bid = "BEN-00035" # Corporate Vendor
        amt = float(random.randint(35000, 75000))
        ts = (BASE_DATE + timedelta(days=random.randint(5, 20), hours=10, minutes=random.randint(0, 50))).isoformat()
        transactions.append((tid, aid, corp_cid, bid, "DEV-00010", "RawbankOnline_Web", "Bulk_Payroll_Disbursement", amt, "USD", amt, "Lubumbashi", "Completed", ts))

    # 2. Legitimate Customer Travel (Kinshasa -> Lubumbashi over 3 days)
    travel_cid = "CUS-00015"
    travel_aid = "ACC-00029"
    for day in [8, 9, 10]:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        ts = (BASE_DATE + timedelta(days=day, hours=14)).isoformat()
        transactions.append((tid, travel_aid, travel_cid, "BEN-00012", "DEV-00015", "IllicoCash_App", "Merchant_Payment", 85000.0, "CDF", round(85000/2750, 2), "Lubumbashi", "Completed", ts))

    # 3. Legitimate Emergency Hospital Bill (Off-Hours)
    for _ in range(5):
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        cid_num = random.randint(1, 100)
        ts = (BASE_DATE + timedelta(days=random.randint(3, 24), hours=2, minutes=30)).isoformat()
        transactions.append((tid, f"ACC-{(2*cid_num):05d}", f"CUS-{cid_num:05d}", "BEN-00004", f"DEV-{cid_num:05d}", "IllicoCash_App", "Merchant_Payment", 350.0, "USD", 350.0, "Kinshasa", "Completed", ts))

    # Remaining legitimate anomalies to reach 50
    while len(transactions) < 800:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        cid_num = random.randint(1, 120)
        transactions.append((
            tid, f"ACC-{(2*cid_num):05d}", f"CUS-{cid_num:05d}", f"BEN-{random.randint(1, 50):05d}",
            f"DEV-{cid_num:05d}", "IllicoCash_App", "P2P_Transfer", 1200.0, "USD", 1200.0,
            customers[cid_num-1][6], "Completed", (BASE_DATE + timedelta(days=random.randint(2, 22), hours=15)).isoformat()
        ))

    # Suspicious Scenarios Injections (100 transactions)
    # -------------------------------------------------------------------------
    # Scenario A: ATO Account Drain (CUS-00014 via DEV-00127 to BEN-00088)
    for amt in [4800.0, 4750.0]:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        ts = (BASE_DATE + timedelta(days=15, hours=3, minutes=25)).isoformat()
        transactions.append((tid, "ACC-00028", "CUS-00014", "BEN-00088", "DEV-00127", "IllicoCash_App", "P2P_Transfer", amt, "USD", amt, "Goma", "Completed", ts))

    # Scenario B: High Velocity Burst (CUS-00022 - 5 transfers within 4 mins)
    vel_ts = BASE_DATE + timedelta(days=12, hours=14, minutes=10)
    for k in range(5):
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        amt_cdf = 15000000.0 # ~ $5,454 USD
        transactions.append((tid, "ACC-00043", "CUS-00022", f"BEN-0006{k+1}", "DEV-00022", "IllicoCash_App", "P2P_Transfer", amt_cdf, "CDF", round(amt_cdf/2750, 2), "Lubumbashi", "Completed", vel_ts.isoformat()))
        vel_ts += timedelta(seconds=45)

    # Scenario C: Shared Device Ring (DEV-00125 used by CUS-00031, 00032, 00033, 00034)
    for c_offset, c_id_str in enumerate(["CUS-00031", "CUS-00032", "CUS-00033", "CUS-00034"]):
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        ts = (BASE_DATE + timedelta(days=16, hours=11 + c_offset)).isoformat()
        c_num = int(c_id_str.split("-")[1])
        transactions.append((tid, f"ACC-{(2*c_num):05d}", c_id_str, "BEN-00075", "DEV-00125", "IllicoCash_App", "P2P_Transfer", 3200.0, "USD", 3200.0, "Kinshasa", "Completed", ts))

    # Scenario D: Mule Fan-In (BEN-00050 receives from 6 different customers)
    mule_ts = BASE_DATE + timedelta(days=19, hours=9, minutes=0)
    for src_c in [41, 42, 43, 44, 46, 47]:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        amt = float(random.choice([2800, 3100, 3400]))
        transactions.append((tid, f"ACC-{(2*src_c):05d}", f"CUS-{src_c:05d}", "BEN-00050", f"DEV-{src_c:05d}", "IllicoCash_App", "P2P_Transfer", amt, "USD", amt, "Kinshasa", "Completed", mule_ts.isoformat()))
        mule_ts += timedelta(minutes=18)
    # Then immediate cash-out from BEN-00050 at an Agent
    tid = f"TXN-{txn_idx:05d}"
    txn_idx += 1
    transactions.append((tid, "ACC-00082", "CUS-00041", "BEN-00050", "DEV-00041", "Agency_Express_POS", "Agent_CashOut", 18000.0, "USD", 18000.0, "Goma", "Completed", (mule_ts + timedelta(minutes=15)).isoformat()))

    # Scenario E: Impossible Travel (CUS-00045 Kinshasa at 14:10, Lubumbashi at 14:40)
    tid = f"TXN-{txn_idx:05d}"
    txn_idx += 1
    t1_ts = BASE_DATE + timedelta(days=21, hours=14, minutes=10)
    transactions.append((tid, "ACC-00089", "CUS-00045", "BEN-00001", "DEV-00045", "IllicoCash_App", "Merchant_Payment", 45000.0, "CDF", round(45000/2750, 2), "Kinshasa", "Completed", t1_ts.isoformat()))
    
    tid = f"TXN-{txn_idx:05d}"
    txn_idx += 1
    t2_ts = BASE_DATE + timedelta(days=21, hours=14, minutes=40)
    transactions.append((tid, "ACC-00090", "CUS-00045", "BEN-00002", "DEV-00045", "ATM_Cardless", "Cardless_CashOut", 1500.0, "USD", 1500.0, "Lubumbashi", "Completed", t2_ts.isoformat()))

    # Scenario F: Brute Force Anomaly -> Cardless Cash-Out (CUS-00055)
    tid = f"TXN-{txn_idx:05d}"
    txn_idx += 1
    f_ts = BASE_DATE + timedelta(days=18, hours=22, minutes=15)
    transactions.append((tid, "ACC-00110", "CUS-00055", "BEN-00010", "DEV-00055", "ATM_Cardless", "Cardless_CashOut", 4500.0, "USD", 4500.0, "Kinshasa", "Completed", f_ts.isoformat()))

    # Scenario G: Structuring / Smurfing (CUS-00062: 4 transfers just under $10,000 threshold)
    smurf_ts = BASE_DATE + timedelta(days=23, hours=13, minutes=0)
    for smurf_amt in [9500.0, 9650.0, 9400.0, 9800.0]:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        transactions.append((tid, "ACC-00124", "CUS-00062", f"BEN-{random.randint(100, 150):05d}", "DEV-00062", "RawbankOnline_Web", "P2P_Transfer", smurf_amt, "USD", smurf_amt, "Kinshasa", "Completed", smurf_ts.isoformat()))
        smurf_ts += timedelta(minutes=12)

    # Scenario H: Multi-Signal Critical Convergence (CUS-00078 via DEV-00126)
    tid = f"TXN-{txn_idx:05d}"
    txn_idx += 1
    h_ts = (BASE_DATE + timedelta(days=25, hours=3, minutes=45)).isoformat()
    transactions.append((tid, "ACC-00156", "CUS-00078", "BEN-00110", "DEV-00126", "IllicoCash_App", "P2P_Transfer", 12500.0, "USD", 12500.0, "Goma", "Completed", h_ts))

    # Fill remaining transactions to reach exactly 900
    while len(transactions) < 900:
        tid = f"TXN-{txn_idx:05d}"
        txn_idx += 1
        cid_num = random.randint(1, 120)
        amt = float(random.randint(25, 450))
        transactions.append((
            tid, f"ACC-{(2*cid_num):05d}", f"CUS-{cid_num:05d}", f"BEN-{random.randint(1, 100):05d}",
            f"DEV-{cid_num:05d}", "IllicoCash_App", "P2P_Transfer", amt, "USD", amt,
            customers[cid_num-1][6], "Completed", (BASE_DATE + timedelta(days=random.randint(1, 26), hours=16)).isoformat()
        ))

    cursor.executemany("""
        INSERT INTO transactions (transaction_id, account_id, customer_id, beneficiary_id, device_id, channel, transaction_type, amount, currency, amount_usd_equivalent, location_city, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, transactions)
    print("  -> Inserted 900 transactions.")

    # -------------------------------------------------------------------------
    # 8. GENERATE FRAUD SIGNALS (200 records) & 9. ALERTS (140 records)
    # -------------------------------------------------------------------------
    print("Generating 140 alerts and 200 fraud signals...")
    alerts = []
    fraud_signals = []
    alt_idx = 1
    sig_idx = 1

    # Map of transaction IDs for quick lookup
    txn_map = {t[0]: t for t in transactions}

    # Helper function to generate an alert and associated signals
    def add_alert(txn_id, severity, risk_score, scenario, reason, signals_list):
        nonlocal alt_idx, sig_idx
        t = txn_map[txn_id]
        aid = f"ALT-{alt_idx:05d}"
        alt_idx += 1
        created = t[12] # Same as transaction timestamp
        status = "NEW_UNASSIGNED" if severity in ["HIGH", "CRITICAL"] else random.choice(["NEW_UNASSIGNED", "UNDER_INVESTIGATION", "DISMISSED_FALSE_POSITIVE"])
        analyst = "A. Mukendi" if status == "UNDER_INVESTIGATION" else None

        alerts.append((aid, txn_id, t[2], t[1], severity, risk_score, status, reason, scenario, analyst, created))

        for rcode, rname, rcat, rsev, conf, desc in signals_list:
            sid = f"SIG-{sig_idx:05d}"
            sig_idx += 1
            fraud_signals.append((sid, aid, txn_id, rcode, rname, rcat, rsev, conf, desc, created))

    # A. Injected High/Critical Alerts for Suspicious Scenarios:
    # ---------------------------------------------------------
    # Scenario A (ATO Drain): 2 transactions
    add_alert("TXN-00801", "CRITICAL", 96, "ATO_DRAIN", "Account takeover: Password reset on untrusted device followed by instant maximum drain.", [
        ("R-ATO-05", "Credential Password Reset Followed by Outbound Transfer", "Credential_ATO", "CRITICAL", 0.95, "Password reset occurred 15 minutes prior on newly enrolled device DEV-00127"),
        ("R-DEV-02", "Unverified Novel Device", "Device_Risk", "HIGH", 0.90, "Hardware signature DEV-00127 has never been previously observed for CUS-00014"),
        ("R-VAL-07", "Value Spike Exceeding 99th Percentile", "Value_Spike", "HIGH", 0.88, "Transfer amount ($4,800 USD) is 18x customer median ($260 USD)")
    ])
    add_alert("TXN-00802", "CRITICAL", 98, "ATO_DRAIN", "Account takeover: Secondary drain transaction exhausting remaining liquid balance.", [
        ("R-ATO-05", "Sequential Post-Compromise Transfer", "Credential_ATO", "CRITICAL", 0.96, "Repeated drain attempt within 2 minutes to external mobile wallet"),
        ("R-VEL-01", "Rapid Consecutive Transfers", "Velocity", "HIGH", 0.92, "Two maximum transfers totaling $9,550 USD within 120 seconds")
    ])

    # Scenario B (Velocity Burst): 5 transactions
    for b_idx in range(803, 808):
        t_id = f"TXN-{b_idx:05d}"
        add_alert(t_id, "HIGH", 88, "VELOCITY_BURST", "High velocity: Multiple rapid transfers to separate recipients within 4 minutes.", [
            ("R-VEL-01", "High-Frequency Burst Transfer", "Velocity", "HIGH", 0.91, "5 consecutive transfers executed within 240 seconds"),
            ("R-VAL-07", "Aggregate Volume Anomaly", "Value_Spike", "MEDIUM", 0.82, "Cumulative 15-minute outflow exceeds 24-hour limit")
        ])

    # Scenario C (Shared Device Ring): 4 transactions
    for c_idx in range(808, 812):
        t_id = f"TXN-{c_idx:05d}"
        add_alert(t_id, "CRITICAL", 94, "SHARED_DEVICE_RING", "Syndicate cluster: Hardware fingerprint DEV-00125 shared across multiple customer profiles.", [
            ("R-DEV-02", "Shared Device Across Disparate Accounts", "Device_Risk", "CRITICAL", 0.97, "Hardware DEV-00125 associated with 4 distinct customers in 48 hours"),
            ("R-MULE-04", "Syndicate Fan-Out Signature", "Mule_Network", "HIGH", 0.89, "Device exhibits coordinated multi-account liquidation")
        ])

    # Scenario D (Mule Fan-In Aggregator): 7 transactions
    for d_idx in range(812, 819):
        t_id = f"TXN-{d_idx:05d}"
        add_alert(t_id, "HIGH", 85, "MULE_FAN_IN", "Mule aggregator: Central recipient BEN-00050 receiving rapid funnel transfers from disparate senders.", [
            ("R-MULE-04", "Mule Account Funnel Inflow", "Mule_Network", "HIGH", 0.93, "Beneficiary BEN-00050 received funds from 6 unrelated senders today"),
            ("R-VEL-01", "Inflow Clustering Velocity", "Velocity", "MEDIUM", 0.80, "Repetitive inbound transfers within 3 hours")
        ])

    # Scenario E (Impossible Travel): 2 transactions
    add_alert("TXN-00819", "LOW", 35, "IMPOSSIBLE_TRAVEL", "First hop in Kinshasa (legitimate merchant payment).", [
        ("R-GEO-03", "Geographic Baseline Anchor", "Geographic_Travel", "LOW", 0.40, "Transaction in primary registered city Kinshasa")
    ])
    add_alert("TXN-00820", "CRITICAL", 99, "IMPOSSIBLE_TRAVEL", "Impossible geographic velocity: ATM cash-out in Lubumbashi 30 mins after Kinshasa transaction.", [
        ("R-GEO-03", "Impossible Velocity Between Cities", "Geographic_Travel", "CRITICAL", 0.99, "Distance Kinshasa->Lubumbashi (1,560 km) traversed in 30 minutes (Required: 180 min)"),
        ("R-DEV-02", "Uncorrelated Terminal Geolocation", "Device_Risk", "HIGH", 0.91, "ATM terminal located 1,560 km from user's active device session")
    ])

    # Scenario F (Brute Force Anomaly -> Cardless Cash-Out): 1 transaction
    add_alert("TXN-00821", "HIGH", 87, "BRUTE_FORCE_DRAIN", "Multiple failed PIN attempts followed by sudden high-value ATM withdrawal.", [
        ("R-AUTH-08", "Authentication PIN Failure Anomaly", "Auth_Anomaly", "HIGH", 0.92, "4 consecutive invalid PIN attempts preceded this session"),
        ("R-ATO-05", "Immediate Post-Auth Withdrawal", "Credential_ATO", "HIGH", 0.88, "Large cardless withdrawal executed 12 minutes after session recovery")
    ])

    # Scenario G (Structuring / Smurfing): 4 transactions
    for g_idx in range(822, 826):
        t_id = f"TXN-{g_idx:05d}"
        add_alert(t_id, "HIGH", 84, "STRUCTURING_SMURF", "Structuring anomaly: Transfer amount just below $10,000 regulatory AML reporting ceiling.", [
            ("R-SMURF-06", "Near-Threshold Structuring Pattern", "Structuring", "HIGH", 0.94, "Transaction amount ($9,400-$9,800) sits immediately below BCC $10,000 threshold"),
            ("R-VEL-01", "Repeated Threshold Proximity", "Velocity", "MEDIUM", 0.81, "Multiple near-threshold disbursements executed within 60 minutes")
        ])

    # Scenario H (Multi-Signal Critical Convergence): 1 transaction
    add_alert("TXN-00826", "CRITICAL", 97, "MULTI_SIGNAL_CONVERGENCE", "High-threat convergence: Foreign VPN IP + new untrusted device + 03:45 AM off-hours transfer.", [
        ("R-DEV-02", "Blacklisted / Foreign VPN IP Address", "Device_Risk", "CRITICAL", 0.96, "Session IP 185.220.101.44 belongs to known commercial anonymizing VPN"),
        ("R-GEO-03", "Anomalous Off-Hours Activity", "Geographic_Travel", "HIGH", 0.89, "Transaction initiated at 03:45 AM UTC (Normal active hours: 08:00-18:00)"),
        ("R-VAL-07", "Extreme Balance Drain", "Value_Spike", "HIGH", 0.93, "Outbound transfer ($12,500 USD) depletes 94% of liquid balance")
    ])

    # Legitimate Anomalies (15 alerts generated to test false positive triage)
    for leg_idx in range(751, 766):
        t_id = f"TXN-{leg_idx:05d}"
        add_alert(t_id, "LOW", 28, "LEGITIMATE_ANOMALY", "High-value corporate payment with verified corporate multi-authorization.", [
            ("R-VAL-07", "High-Value Transaction Threshold", "Value_Spike", "LOW", 0.45, "Single transaction > $30,000 USD; verified against corporate baseline")
        ])

    # Routine Low/Medium Anomaly Alerts to reach exactly 140 alerts
    remaining_alert_count = 140 - len(alerts)
    print(f"Adding {remaining_alert_count} routine/borderline alerts to reach target of 140...")
    
    # Pick from routine transactions
    sample_txn_ids = [f"TXN-{random.randint(1, 700):05d}" for _ in range(remaining_alert_count)]
    for r_tid in sample_txn_ids:
        r_sev = random.choice(["LOW", "MEDIUM"])
        r_score = random.randint(20, 58)
        rule_choice = random.choice([
            ("R-DEV-02", "First-Time Browser Device", "Device_Risk", r_sev, 0.55, "Customer accessing via new desktop browser session"),
            ("R-VAL-07", "Mild Weekend Value Elevation", "Value_Spike", r_sev, 0.48, "Transfer is 2.5x above standard weekday median"),
            ("R-VEL-01", "Moderate P2P Velocity", "Velocity", r_sev, 0.52, "Two transfers in same hour to mobile wallet")
        ])
        add_alert(r_tid, r_sev, r_score, "UNUSUAL_BEHAVIOUR", "Automated monitoring flag: Moderate behavioral anomaly.", [rule_choice])

    # Now verify total fraud signals count.
    # Currently we have len(fraud_signals). Let's see how many we have:
    current_sig_count = len(fraud_signals)
    print(f"Current fraud signals generated: {current_sig_count}. Target: 200.")
    needed_sigs = 200 - current_sig_count

    if needed_sigs > 0:
        # Add secondary corroborating signals to existing alerts to hit exactly 200 signals
        print(f"Adding {needed_sigs} secondary corroborating signals to alerts...")
        eligible_alerts = [a for a in alerts if a[4] in ["HIGH", "CRITICAL", "MEDIUM"]]
        for k in range(needed_sigs):
            chosen_alert = eligible_alerts[k % len(eligible_alerts)]
            sid = f"SIG-{sig_idx:05d}"
            sig_idx += 1
            fraud_signals.append((
                sid, chosen_alert[0], chosen_alert[1], "R-BEH-09",
                "Secondary Behavioral Baseline Deviation", "Value_Spike",
                "MEDIUM", 0.72, "Activity exceeds 30-day moving average profile", chosen_alert[10]
            ))

    cursor.executemany("""
        INSERT INTO alerts (alert_id, transaction_id, customer_id, account_id, severity, composite_risk_score, status, reason_summary, scenario_type, assigned_analyst, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, alerts)
    print(f"  -> Inserted {len(alerts)} alerts.")

    cursor.executemany("""
        INSERT INTO fraud_signals (signal_id, alert_id, transaction_id, rule_code, rule_name, rule_category, severity, confidence_score, signal_description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, fraud_signals)
    print(f"  -> Inserted {len(fraud_signals)} fraud signals.")

    conn.commit()
    conn.close()

    # -------------------------------------------------------------------------
    # EXPORT SNAPSHOTS TO data/synthetic/ AS JSON FOR INSPECTION
    # -------------------------------------------------------------------------
    print("Exporting data snapshots to data/synthetic/...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = [
        "customers", "accounts", "devices", "beneficiaries", 
        "behavioural_baselines", "auth_activities", "transactions", 
        "alerts", "fraud_signals"
    ]
    summary_counts = {}
    total_records = 0

    for tbl in tables:
        cursor.execute(f"SELECT * FROM {tbl};")
        col_names = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        tbl_count = len(rows)
        summary_counts[tbl] = tbl_count
        total_records += tbl_count
        
        # Write first 50 rows to JSON preview
        preview_data = [dict(zip(col_names, row)) for row in rows[:50]]
        json_path = os.path.join(DATA_DIR, f"{tbl}_sample.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump(preview_data, jf, indent=2)

    conn.close()

    print("\n" + "=" * 70)
    print("PHASE 2 SYNTHETIC DATA GENERATION COMPLETE")
    print("=" * 70)
    for tbl, cnt in summary_counts.items():
        print(f"  * {tbl.ljust(25)} : {cnt:>5} records")
    print("-" * 70)
    print(f"  * TOTAL DATABASE RECORDS    : {total_records:>5} records (Target: 2,500)")
    print("=" * 70)

    if total_records == 2500:
        print("SUCCESS: Target of EXACTLY 2,500 records successfully achieved!")
    else:
        print(f"NOTE: Generated {total_records} records within target window 2,400-2,600.")


if __name__ == "__main__":
    main()
