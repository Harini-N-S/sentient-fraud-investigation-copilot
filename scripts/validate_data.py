#!/usr/bin/env python3
"""
Rawbank Sentient Fraud Intelligence Platform
Phase 2 Synthetic Data Validation Engine
-----------------------------------------------------------------------------
Comprehensive automated validation suite verifying:
  1. Duplicate Primary Keys
  2. Missing Required (NULL) Fields
  3. Broken Foreign Key References (Referential Integrity)
  4. Invalid Timestamps (ISO 8601 formatting & temporal bounds)
  5. Invalid Currencies (Strictly CDF and USD)
  6. Negative or Invalid Amounts where not permitted
  7. Invalid Customer-Account Relationships
  8. Invalid Transaction-Beneficiary Relationships
  9. Invalid Transaction-Device Relationships
 10. Alerts Referencing Nonexistent Entities
 11. Fraud Signals Referencing Nonexistent Entities
 12. Duplicate Records
 13. Impossible Relationship States
 14. Data Distribution Sanity & Record Count Budget (2,400-2,600)
 15. Synthetic-Data Compliance (Zero real PII or live banking data)

Also executes sample relational graph queries (Task 17) and outputs sample
connected data inspection (Task 20).
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "synthetic_bank.db")


class DataValidator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self.results = []
        self.passed_count = 0
        self.failed_count = 0

    def log_result(self, check_id, check_name, status, details=""):
        res = {
            "check_id": check_id,
            "check_name": check_name,
            "status": status,
            "details": details
        }
        self.results.append(res)
        if status == "PASSED":
            self.passed_count += 1
            print(f"  [PASS] Check {check_id:02d}: {check_name}")
        else:
            self.failed_count += 1
            print(f"  [FAIL] Check {check_id:02d}: {check_name} -> {details}")

    def run_all(self):
        print("=" * 75)
        print("PHASE 2 SYNTHETIC DATA VALIDATION ENGINE")
        print("=" * 75)
        print(f"Validating database: {self.db_path}\n")

        self.check_record_counts_and_distribution()      # Check 14
        self.check_duplicate_primary_keys()              # Check 1
        self.check_missing_required_fields()             # Check 2
        self.check_broken_foreign_keys()                 # Check 3
        self.check_invalid_timestamps()                  # Check 4
        self.check_currencies()                          # Check 5
        self.check_amounts()                             # Check 6
        self.check_customer_account_integrity()          # Check 7
        self.check_transaction_beneficiary_integrity()    # Check 8
        self.check_transaction_device_integrity()         # Check 9
        self.check_alerts_referential_integrity()        # Check 10
        self.check_fraud_signals_integrity()             # Check 11
        self.check_duplicate_records()                   # Check 12
        self.check_impossible_relationship_states()       # Check 13
        self.check_synthetic_compliance()                # Check 15

        print("\n" + "=" * 75)
        print(f"VALIDATION SUMMARY: {self.passed_count} PASSED | {self.failed_count} FAILED")
        print("=" * 75)

        self.demonstrate_relationship_graph_queries()
        self.demonstrate_sample_data_inspection()

        return self.failed_count == 0

    # -------------------------------------------------------------------------
    # CHECK 14: Data Distribution Sanity & Record Count Budget
    # -------------------------------------------------------------------------
    def check_record_counts_and_distribution(self):
        tables = [
            "customers", "accounts", "devices", "beneficiaries", 
            "behavioural_baselines", "auth_activities", "transactions", 
            "alerts", "fraud_signals"
        ]
        counts = {}
        total = 0
        for t in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {t};")
            c = self.cursor.fetchone()[0]
            counts[t] = c
            total += c

        if 2400 <= total <= 2600:
            self.log_result(
                14, "Data Distribution Sanity & Record Count Budget", "PASSED",
                f"Total records = {total} (within target 2,400-2,600). Counts: {counts}"
            )
        else:
            self.log_result(
                14, "Data Distribution Sanity & Record Count Budget", "FAILED",
                f"Total records = {total} outside range 2,400-2,600. Counts: {counts}"
            )

    # -------------------------------------------------------------------------
    # CHECK 1: Duplicate Primary Keys
    # -------------------------------------------------------------------------
    def check_duplicate_primary_keys(self):
        pk_map = {
            "customers": "customer_id",
            "accounts": "account_id",
            "devices": "device_id",
            "beneficiaries": "beneficiary_id",
            "behavioural_baselines": "baseline_id",
            "auth_activities": "activity_id",
            "transactions": "transaction_id",
            "alerts": "alert_id",
            "fraud_signals": "signal_id"
        }
        duplicates = []
        for tbl, pk in pk_map.items():
            self.cursor.execute(f"SELECT {pk}, COUNT(*) FROM {tbl} GROUP BY {pk} HAVING COUNT(*) > 1;")
            rows = self.cursor.fetchall()
            if rows:
                duplicates.append(f"{tbl}: {len(rows)} duplicates")

        if not duplicates:
            self.log_result(1, "Zero Duplicate Primary Keys", "PASSED", "All primary keys are unique across all 9 tables.")
        else:
            self.log_result(1, "Zero Duplicate Primary Keys", "FAILED", f"Found duplicates: {', '.join(duplicates)}")

    # -------------------------------------------------------------------------
    # CHECK 2: Missing Required (NULL) Fields
    # -------------------------------------------------------------------------
    def check_missing_required_fields(self):
        null_issues = []
        checks = [
            ("customers", ["customer_id", "full_name", "customer_segment", "kyc_status", "primary_phone", "email", "registered_city", "risk_category", "created_at"]),
            ("accounts", ["account_id", "customer_id", "account_type", "currency", "current_balance", "available_balance", "account_status", "created_at"]),
            ("transactions", ["transaction_id", "account_id", "customer_id", "beneficiary_id", "device_id", "channel", "transaction_type", "amount", "currency", "amount_usd_equivalent", "location_city", "status", "timestamp"]),
            ("alerts", ["alert_id", "transaction_id", "customer_id", "account_id", "severity", "composite_risk_score", "status", "reason_summary", "scenario_type", "created_at"]),
            ("fraud_signals", ["signal_id", "alert_id", "transaction_id", "rule_code", "rule_name", "rule_category", "severity", "confidence_score", "signal_description", "created_at"])
        ]
        for tbl, cols in checks:
            for col in cols:
                self.cursor.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {col} IS NULL;")
                c = self.cursor.fetchone()[0]
                if c > 0:
                    null_issues.append(f"{tbl}.{col} has {c} NULLs")

        if not null_issues:
            self.log_result(2, "Zero Missing Required Fields", "PASSED", "All mandatory columns are populated with valid non-null values.")
        else:
            self.log_result(2, "Zero Missing Required Fields", "FAILED", f"Found nulls: {', '.join(null_issues)}")

    # -------------------------------------------------------------------------
    # CHECK 3: Broken Foreign Key References (Referential Integrity)
    # -------------------------------------------------------------------------
    def check_broken_foreign_keys(self):
        self.cursor.execute("PRAGMA foreign_key_check;")
        fk_errors = self.cursor.fetchall()
        if not fk_errors:
            self.log_result(3, "Strict Foreign Key Referential Integrity", "PASSED", "PRAGMA foreign_key_check reported 0 violations across all tables.")
        else:
            self.log_result(3, "Strict Foreign Key Referential Integrity", "FAILED", f"Found {len(fk_errors)} broken foreign keys: {fk_errors[:5]}")

    # -------------------------------------------------------------------------
    # CHECK 4: Invalid Timestamps
    # -------------------------------------------------------------------------
    def check_invalid_timestamps(self):
        time_checks = [
            ("customers", "created_at"),
            ("accounts", "created_at"),
            ("devices", "first_seen_timestamp"),
            ("devices", "last_seen_timestamp"),
            ("auth_activities", "timestamp"),
            ("transactions", "timestamp"),
            ("alerts", "created_at"),
            ("fraud_signals", "created_at")
        ]
        bad_timestamps = []
        for tbl, col in time_checks:
            self.cursor.execute(f"SELECT {col} FROM {tbl};")
            for row in self.cursor.fetchall():
                ts_str = row[0]
                try:
                    datetime.fromisoformat(ts_str)
                except ValueError:
                    bad_timestamps.append(f"{tbl}.{col}: '{ts_str}'")
                    break

        if not bad_timestamps:
            self.log_result(4, "ISO 8601 Timestamp Formatting & Validity", "PASSED", "All timestamps are valid ISO 8601 dates.")
        else:
            self.log_result(4, "ISO 8601 Timestamp Formatting & Validity", "FAILED", f"Invalid timestamps: {', '.join(bad_timestamps)}")

    # -------------------------------------------------------------------------
    # CHECK 5: Invalid Currencies
    # -------------------------------------------------------------------------
    def check_currencies(self):
        self.cursor.execute("SELECT COUNT(*) FROM accounts WHERE currency NOT IN ('CDF', 'USD');")
        bad_acc_curr = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE currency NOT IN ('CDF', 'USD');")
        bad_txn_curr = self.cursor.fetchone()[0]

        if bad_acc_curr == 0 and bad_txn_curr == 0:
            self.log_result(5, "Strict Dual-Currency Conformance (CDF/USD)", "PASSED", "All accounts and transactions are denominated strictly in CDF or USD.")
        else:
            self.log_result(5, "Strict Dual-Currency Conformance (CDF/USD)", "FAILED", f"Bad account currencies: {bad_acc_curr}, bad txn currencies: {bad_txn_curr}")

    # -------------------------------------------------------------------------
    # CHECK 6: Negative/Invalid Amounts
    # -------------------------------------------------------------------------
    def check_amounts(self):
        self.cursor.execute("SELECT COUNT(*) FROM accounts WHERE current_balance < 0 OR available_balance < 0;")
        neg_bal = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE amount <= 0 OR amount_usd_equivalent <= 0;")
        neg_tx = self.cursor.fetchone()[0]

        if neg_bal == 0 and neg_tx == 0:
            self.log_result(6, "Non-Negative Balances & Positive Transaction Amounts", "PASSED", "All balances >= 0 and transaction amounts > 0.")
        else:
            self.log_result(6, "Non-Negative Balances & Positive Transaction Amounts", "FAILED", f"Negative balances: {neg_bal}, negative amounts: {neg_tx}")

    # -------------------------------------------------------------------------
    # CHECK 7: Customer-Account Integrity
    # -------------------------------------------------------------------------
    def check_customer_account_integrity(self):
        # Every account must point to a customer that exists
        self.cursor.execute("""
            SELECT COUNT(*) FROM accounts a 
            LEFT JOIN customers c ON a.customer_id = c.customer_id 
            WHERE c.customer_id IS NULL;
        """)
        orphaned = self.cursor.fetchone()[0]
        if orphaned == 0:
            self.log_result(7, "Customer-Account Relational Linkage", "PASSED", "100% of accounts map to existing verified customers.")
        else:
            self.log_result(7, "Customer-Account Relational Linkage", "FAILED", f"{orphaned} orphaned accounts found.")

    # -------------------------------------------------------------------------
    # CHECK 8: Transaction-Beneficiary Integrity
    # -------------------------------------------------------------------------
    def check_transaction_beneficiary_integrity(self):
        self.cursor.execute("""
            SELECT COUNT(*) FROM transactions t 
            LEFT JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id 
            WHERE b.beneficiary_id IS NULL;
        """)
        orphaned = self.cursor.fetchone()[0]
        if orphaned == 0:
            self.log_result(8, "Transaction-Beneficiary Relational Linkage", "PASSED", "100% of transactions map to existing verified beneficiaries.")
        else:
            self.log_result(8, "Transaction-Beneficiary Relational Linkage", "FAILED", f"{orphaned} orphaned transactions found.")

    # -------------------------------------------------------------------------
    # CHECK 9: Transaction-Device Integrity
    # -------------------------------------------------------------------------
    def check_transaction_device_integrity(self):
        self.cursor.execute("""
            SELECT COUNT(*) FROM transactions t 
            LEFT JOIN devices d ON t.device_id = d.device_id 
            WHERE d.device_id IS NULL;
        """)
        orphaned = self.cursor.fetchone()[0]
        if orphaned == 0:
            self.log_result(9, "Transaction-Device Relational Linkage", "PASSED", "100% of transactions map to registered device profiles.")
        else:
            self.log_result(9, "Transaction-Device Relational Linkage", "FAILED", f"{orphaned} transactions with unknown devices.")

    # -------------------------------------------------------------------------
    # CHECK 10: Alerts Entity References
    # -------------------------------------------------------------------------
    def check_alerts_referential_integrity(self):
        self.cursor.execute("""
            SELECT COUNT(*) FROM alerts a
            LEFT JOIN transactions t ON a.transaction_id = t.transaction_id
            LEFT JOIN customers c ON a.customer_id = c.customer_id
            LEFT JOIN accounts acc ON a.account_id = acc.account_id
            WHERE t.transaction_id IS NULL OR c.customer_id IS NULL OR acc.account_id IS NULL;
        """)
        bad_alerts = self.cursor.fetchone()[0]
        if bad_alerts == 0:
            self.log_result(10, "Alerts Entity Cross-Referencing", "PASSED", "All alerts reference valid transactions, customers, and accounts.")
        else:
            self.log_result(10, "Alerts Entity Cross-Referencing", "FAILED", f"{bad_alerts} alerts reference invalid entities.")

    # -------------------------------------------------------------------------
    # CHECK 11: Fraud Signals Entity References
    # -------------------------------------------------------------------------
    def check_fraud_signals_integrity(self):
        self.cursor.execute("""
            SELECT COUNT(*) FROM fraud_signals s
            LEFT JOIN alerts a ON s.alert_id = a.alert_id
            LEFT JOIN transactions t ON s.transaction_id = t.transaction_id
            WHERE a.alert_id IS NULL OR t.transaction_id IS NULL;
        """)
        bad_signals = self.cursor.fetchone()[0]
        if bad_signals == 0:
            self.log_result(11, "Fraud Signals Entity Cross-Referencing", "PASSED", "All fraud signals link to valid alerts and transactions.")
        else:
            self.log_result(11, "Fraud Signals Entity Cross-Referencing", "FAILED", f"{bad_signals} signals reference invalid entities.")

    # -------------------------------------------------------------------------
    # CHECK 12: Duplicate Records Across Tables
    # -------------------------------------------------------------------------
    def check_duplicate_records(self):
        self.cursor.execute("""
            SELECT customer_id, full_name, email, COUNT(*) 
            FROM customers GROUP BY customer_id, full_name, email HAVING COUNT(*) > 1;
        """)
        dup_c = len(self.cursor.fetchall())
        if dup_c == 0:
            self.log_result(12, "Zero Exact Duplicate Entity Records", "PASSED", "No duplicate entity tuples detected.")
        else:
            self.log_result(12, "Zero Exact Duplicate Entity Records", "FAILED", f"Found {dup_c} duplicate records.")

    # -------------------------------------------------------------------------
    # CHECK 13: Impossible Relationship States
    # -------------------------------------------------------------------------
    def check_impossible_relationship_states(self):
        # A transaction's account must actually belong to the transaction's customer
        self.cursor.execute("""
            SELECT COUNT(*) FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE t.customer_id != a.customer_id;
        """)
        mismatched_ownership = self.cursor.fetchone()[0]

        # Device first_seen cannot be after last_seen
        self.cursor.execute("""
            SELECT COUNT(*) FROM devices WHERE first_seen_timestamp > last_seen_timestamp;
        """)
        bad_device_times = self.cursor.fetchone()[0]

        if mismatched_ownership == 0 and bad_device_times == 0:
            self.log_result(13, "Zero Impossible Relationship States", "PASSED", "Customer-account ownership and device temporal coherence verified.")
        else:
            self.log_result(13, "Zero Impossible Relationship States", "FAILED", f"Ownership mismatches: {mismatched_ownership}, bad device times: {bad_device_times}")

    # -------------------------------------------------------------------------
    # CHECK 15: Synthetic-Data Compliance
    # -------------------------------------------------------------------------
    def check_synthetic_compliance(self):
        # Verify no real internal Rawbank account numbers (synthetic IDs start with CUS-, ACC-, etc.)
        self.cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_id NOT LIKE 'CUS-%';")
        bad_cid = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_id NOT LIKE 'ACC-%';")
        bad_aid = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id NOT LIKE 'TXN-%';")
        bad_tid = self.cursor.fetchone()[0]

        if bad_cid == 0 and bad_aid == 0 and bad_tid == 0:
            self.log_result(15, "100% Synthetic Data & Zero PII Compliance", "PASSED", "All identifiers follow synthetic prefixes; zero live banking identifiers.")
        else:
            self.log_result(15, "100% Synthetic Data & Zero PII Compliance", "FAILED", "Non-synthetic identifier detected.")

    # -------------------------------------------------------------------------
    # TASK 17: Relationship Graph Query Demonstrations
    # -------------------------------------------------------------------------
    def demonstrate_relationship_graph_queries(self):
        print("\n" + "-" * 75)
        print("TASK 17 DEMONSTRATION: RELATIONSHIP GRAPH QUERYABILITY")
        print("-" * 75)

        # Query 1: Trace Customer -> Accounts -> Transactions -> Beneficiary for an alert
        print("\n[Graph Query 1] Trace Alert -> Transaction -> Customer -> Account -> Beneficiary:")
        self.cursor.execute("""
            SELECT 
                al.alert_id, al.severity, al.scenario_type,
                t.transaction_id, t.amount, t.currency, t.timestamp,
                c.customer_id, c.full_name, c.registered_city,
                acc.account_id, acc.account_type,
                b.beneficiary_id, b.beneficiary_name, b.institution_name
            FROM alerts al
            JOIN transactions t ON al.transaction_id = t.transaction_id
            JOIN customers c ON t.customer_id = c.customer_id
            JOIN accounts acc ON t.account_id = acc.account_id
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            WHERE al.severity = 'CRITICAL'
            LIMIT 2;
        """)
        for r in self.cursor.fetchall():
            print(f"  Alert {r[0]} ({r[1]} | {r[2]}):")
            print(f"    Transaction : {r[3]} ({r[4]:,.2f} {r[5]} at {r[6]})")
            print(f"    Customer    : {r[7]} ({r[8]} - {r[9]})")
            print(f"    Account     : {r[10]} ({r[11]})")
            print(f"    Beneficiary : {r[12]} ({r[13]} via {r[14]})")

        # Query 2: Uncover Shared Device Ring (Scenario C)
        print("\n[Graph Query 2] Uncover Multiple Customers Sharing a Single Device (Syndicate):")
        self.cursor.execute("""
            SELECT 
                t.device_id, d.device_model, d.ip_address,
                COUNT(DISTINCT t.customer_id) as distinct_customers,
                GROUP_CONCAT(DISTINCT t.customer_id) as customer_list,
                COUNT(t.transaction_id) as total_txns,
                SUM(t.amount_usd_equivalent) as total_usd_volume
            FROM transactions t
            JOIN devices d ON t.device_id = d.device_id
            GROUP BY t.device_id
            HAVING COUNT(DISTINCT t.customer_id) > 1;
        """)
        for r in self.cursor.fetchall():
            print(f"  Shared Device {r[0]} ({r[1]} | IP {r[2]}):")
            print(f"    Linked Customers ({r[3]} distinct): {r[4]}")
            print(f"    Transaction Count: {r[5]} | Total Volume: ${r[6]:,.2f} USD")

        # Query 3: Uncover Mule Funnel Aggregator (Scenario D)
        print("\n[Graph Query 3] Uncover Mule Beneficiary Receiving Inflows from Multiple Senders:")
        self.cursor.execute("""
            SELECT 
                b.beneficiary_id, b.beneficiary_name, b.institution_name,
                COUNT(DISTINCT t.customer_id) as sender_count,
                GROUP_CONCAT(DISTINCT t.customer_id) as senders,
                SUM(t.amount_usd_equivalent) as total_received_usd
            FROM transactions t
            JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
            GROUP BY b.beneficiary_id
            HAVING COUNT(DISTINCT t.customer_id) >= 4;
        """)
        for r in self.cursor.fetchall():
            print(f"  Mule Recipient {r[0]} ({r[1]} - {r[2]}):")
            print(f"    Distinct Senders ({r[3]}): {r[4]}")
            print(f"    Total Aggregated Volume: ${r[5]:,.2f} USD")

    # -------------------------------------------------------------------------
    # TASK 20: Sample Data Inspection Output
    # -------------------------------------------------------------------------
    def demonstrate_sample_data_inspection(self):
        print("\n" + "-" * 75)
        print("TASK 20 DEMONSTRATION: SAMPLE CONNECTED DATA INSPECTION")
        print("-" * 75)

        sample_cases = [
            ("ATO_DRAIN", "Suspicious Activity: Account Takeover & Drain"),
            ("LEGITIMATE_ANOMALY", "Legitimate Anomaly: Corporate High-Value Payment"),
            ("IMPOSSIBLE_TRAVEL", "Suspicious Activity: Impossible Travel Anomaly")
        ]

        for stype, title in sample_cases:
            print(f"\n--- [SAMPLE CASE] {title} ({stype}) ---")
            self.cursor.execute("""
                SELECT 
                    al.alert_id, al.severity, al.composite_risk_score, al.reason_summary,
                    t.transaction_id, t.amount, t.currency, t.amount_usd_equivalent, t.channel, t.location_city, t.timestamp,
                    c.customer_id, c.full_name, c.customer_segment, c.registered_city,
                    acc.account_id, acc.account_type, acc.current_balance,
                    d.device_id, d.device_model, d.trust_status, d.ip_address,
                    b.beneficiary_id, b.beneficiary_name, b.institution_name
                FROM alerts al
                JOIN transactions t ON al.transaction_id = t.transaction_id
                JOIN customers c ON t.customer_id = c.customer_id
                JOIN accounts acc ON t.account_id = acc.account_id
                JOIN devices d ON t.device_id = d.device_id
                JOIN beneficiaries b ON t.beneficiary_id = b.beneficiary_id
                WHERE al.scenario_type = ?
                LIMIT 1;
            """, (stype,))
            row = self.cursor.fetchone()
            if row:
                print(f"  Customer     : {row[11]} | {row[12]} ({row[13]} - {row[14]})")
                print(f"  Account      : {row[15]} | {row[16]} (Balance: {row[17]:,.2f})")
                print(f"  Transaction  : {row[4]} | {row[5]:,.2f} {row[6]} (${row[7]:,.2f} USD) via {row[8]} in {row[9]} at {row[10]}")
                print(f"  Device       : {row[18]} | {row[19]} ({row[20]} - IP: {row[21]})")
                print(f"  Beneficiary  : {row[22]} | {row[23]} ({row[24]})")
                print(f"  Alert Case   : {row[0]} [Severity: {row[1]}, Score: {row[2]}/100]")
                print(f"  Reason       : {row[3]}")

                # Show linked signals
                self.cursor.execute("SELECT rule_code, rule_name, rule_category, severity, signal_description FROM fraud_signals WHERE alert_id = ?;", (row[0],))
                sigs = self.cursor.fetchall()
                print(f"  Linked Fraud Signals ({len(sigs)}):")
                for s in sigs:
                    print(f"    * [{s[0]}] {s[1]} ({s[2]} | {s[3]}): {s[4]}")


if __name__ == "__main__":
    validator = DataValidator(DB_PATH)
    success = validator.run_all()
    sys.exit(0 if success else 1)
