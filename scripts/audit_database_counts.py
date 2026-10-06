import sqlite3
from pathlib import Path

db_path = Path("database/synthetic_bank.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("================================================================================")
print("RAWBANK SENTIENT FRAUD INTELLIGENCE PLATFORM — DATABASE CONSISTENCY AUDIT")
print("================================================================================\n")

print(f"Database File: {db_path} ({db_path.stat().st_size:,} bytes)")

table_counts = {}
for t in [
    "customers", "accounts", "transactions", "alerts", 
    "fraud_signals", "devices", "beneficiaries", 
    "auth_activities", "behavioural_baselines"
]:
    cursor.execute(f"SELECT COUNT(*) as c FROM \"{t}\"")
    c = cursor.fetchone()["c"]
    table_counts[t] = c
    print(f"  {t:<25}: {c:>6,} records")

print(f"\nTOTAL SYNTHETIC DATABASE RECORDS: {sum(table_counts.values()):,}\n")

# Transaction volume
cursor.execute("SELECT COUNT(*) as count, SUM(amount_usd_equivalent) as vol FROM transactions")
row = cursor.fetchone()
total_txns = row["count"]
total_vol = row["vol"]

cursor.execute("SELECT status, COUNT(*) as c, SUM(amount_usd_equivalent) as vol FROM transactions GROUP BY status ORDER BY c DESC")
txns_by_status = {row["status"]: (row["c"], row["vol"]) for row in cursor.fetchall()}

# Alert severities & scenarios
cursor.execute("SELECT severity, COUNT(*) as c FROM alerts GROUP BY severity ORDER BY c DESC")
alerts_by_sev = {row["severity"]: row["c"] for row in cursor.fetchall()}

cursor.execute("SELECT scenario_type, COUNT(*) as c FROM alerts GROUP BY scenario_type ORDER BY c DESC")
alerts_by_scenario = {row["scenario_type"]: row["c"] for row in cursor.fetchall()}

# Beneficiaries & Devices
cursor.execute("SELECT COUNT(*) as c FROM beneficiaries WHERE is_known_mule = 1")
known_mules = cursor.fetchone()["c"]

cursor.execute("SELECT trust_status, COUNT(*) as c FROM devices GROUP BY trust_status")
devices_by_trust = {row["trust_status"]: row["c"] for row in cursor.fetchall()}

cursor.execute("SELECT COUNT(*) as c FROM devices WHERE is_vpn_or_tor = 1 OR is_rooted_jailbroken = 1")
suspicious_devices = cursor.fetchone()["c"]

# Customer distribution
cursor.execute("SELECT kyc_status, COUNT(*) as c FROM customers GROUP BY kyc_status")
kyc_counts = {row["kyc_status"]: row["c"] for row in cursor.fetchall()}

cursor.execute("SELECT customer_segment, COUNT(*) as c FROM customers GROUP BY customer_segment")
segment_counts = {row["customer_segment"]: row["c"] for row in cursor.fetchall()}

cursor.execute("SELECT risk_category, COUNT(*) as c FROM customers GROUP BY risk_category")
risk_category_counts = {row["risk_category"]: row["c"] for row in cursor.fetchall()}

print("--- Transaction Aggregate Statistics ---")
print(f"Total Transactions: {total_txns:,}")
print(f"Total Volume: ${total_vol:,.2f} USD")
for status, (count, vol) in txns_by_status.items():
    print(f"  - Status '{status}': {count:,} transactions (${vol:,.2f} USD)")

print("\n--- Alert Severity Breakdown (Phase 3 Deterministic Output) ---")
for sev, count in alerts_by_sev.items():
    pct = (count / table_counts["alerts"]) * 100
    print(f"  - {sev:<10}: {count:>3} alerts ({pct:5.1f}%)")

print("\n--- Alert Scenario Types ---")
for scn, count in alerts_by_scenario.items():
    print(f"  - {scn:<25}: {count:>3} alerts")

print("\n--- Network & Forensic Entities ---")
print(f"Known Mule Beneficiaries: {known_mules} / {table_counts['beneficiaries']}")
print(f"Device Trust Breakdown: {devices_by_trust}")
print(f"Suspicious Hardware (VPN/Tor/Rooted): {suspicious_devices}")

print("\n--- Customer Demographics ---")
print(f"Customer Segments: {segment_counts}")
print(f"KYC Verification Statuses: {kyc_counts}")
print(f"Risk Categories: {risk_category_counts}")
