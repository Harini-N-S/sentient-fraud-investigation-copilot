#!/usr/bin/env python3
"""
Rawbank Sentient Fraud Intelligence Platform
Phase 3 Deterministic Fraud Rules Engine Test Suite
-----------------------------------------------------------------------------
Automated unit and integration test suite executing against the actual
synthetic database (database/synthetic_bank.db).

Verifies the 24 mandated test scenarios:
  1. Velocity positive case (TXN-00807)
  2. Velocity negative case (TXN-00001)
  3. Value-spike positive case (TXN-00801)
  4. Value-spike normal case (TXN-00005)
  5. New-device positive case (TXN-00801)
  6. Known-device case (TXN-00001)
  7. New-beneficiary positive case (TXN-00801)
  8. Existing-beneficiary case (recurrent merchant)
  9. Geographic anomaly positive case (TXN-00820)
 10. Normal geographic case (TXN-00819)
 11. Shared-device case (TXN-00808)
 12. Normal device relationship (TXN-00001)
 13. Shared-beneficiary case (TXN-00812)
 14. Structuring-like case (TXN-00825)
 15. Normal transaction sequence (TXN-00010)
 16. Authentication anomaly positive case (TXN-00821)
 17. Normal authentication case (TXN-00001)
 18. Behavioural deviation positive case (TXN-00826)
 19. Normal behaviour case (TXN-00015)
 20. Multi-signal correlation (TXN-00826)
 21. Legitimate high-value activity false-positive test (TXN-00751)
 22. Legitimate travel scenario test (TXN-00761)
 23. Legitimate off-hours activity test (TXN-00771)
 24. Legitimate device upgrade verification test

ALL TESTS OPERATE ON PURE DETERMINISTIC CALCULATIONS (ZERO LLM).
"""

import os
import sys
import unittest
import sqlite3

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rules.engine import FraudIntelligenceEngine
from rules.velocity import VelocityRule
from rules.value_spike import ValueSpikeRule
from rules.device import NewDeviceRule, SharedDeviceRule
from rules.beneficiary import NewBeneficiaryRule, SharedBeneficiaryRule
from rules.geographic import GeographicVelocityRule
from rules.structuring import StructuringRule
from rules.authentication import AuthenticationAnomalyRule, ATOPatternRule
from rules.behavioural import BehaviouralDeviationRule

DB_PATH = os.path.join(BASE_DIR, "database", "synthetic_bank.db")


class TestDeterministicFraudRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = FraudIntelligenceEngine(DB_PATH)
        cls.conn = sqlite3.connect(DB_PATH)
        cls.conn.execute("PRAGMA foreign_keys = ON;")

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # -------------------------------------------------------------------------
    # Test 1 & 2: Velocity
    # -------------------------------------------------------------------------
    def test_01_velocity_positive_case(self):
        """Scenario B: 5 transfers within 240 seconds on CUS-00022."""
        rule = VelocityRule(window_seconds=300, min_transaction_count=4)
        signals = rule.evaluate(self.conn, "TXN-00807")
        self.assertTrue(len(signals) >= 1, "Expected velocity signal on TXN-00807")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-VEL-01")
        self.assertIn(sig.severity, ["HIGH", "CRITICAL"])
        self.assertGreaterEqual(sig.evidence_data["transaction_count"], 4)
        self.assertLessEqual(sig.evidence_data["observed_elapsed_seconds"], 300)

    def test_02_velocity_negative_case(self):
        """Normal routine transaction has no burst velocity."""
        rule = VelocityRule(window_seconds=300, min_transaction_count=4)
        signals = rule.evaluate(self.conn, "TXN-00001")
        self.assertEqual(len(signals), 0, "Did not expect velocity signal on routine transaction TXN-00001")

    # -------------------------------------------------------------------------
    # Test 3 & 4: Value Spike
    # -------------------------------------------------------------------------
    def test_03_value_spike_positive_case(self):
        """Scenario A: $4,800 USD transfer on account with $260 USD baseline average."""
        rule = ValueSpikeRule()
        signals = rule.evaluate(self.conn, "TXN-00801")
        self.assertTrue(len(signals) >= 1, "Expected value spike on TXN-00801")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-VAL-07")
        self.assertGreaterEqual(sig.evidence_data["deviation_percentage"], 400.0)

    def test_04_value_spike_normal_case(self):
        """Small routine transaction well within historical limits."""
        rule = ValueSpikeRule()
        signals = rule.evaluate(self.conn, "TXN-00005")
        self.assertEqual(len(signals), 0, "Normal amount should not trigger value spike")

    # -------------------------------------------------------------------------
    # Test 5 & 6: New Device
    # -------------------------------------------------------------------------
    def test_05_new_device_positive_case(self):
        """Scenario A: DEV-00127 is unverified device used for ATO drain."""
        rule = NewDeviceRule()
        signals = rule.evaluate(self.conn, "TXN-00801")
        self.assertTrue(len(signals) >= 1, "Expected new device signal on TXN-00801")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-DEV-02")
        self.assertEqual(sig.evidence_data["device_id"], "DEV-00127")

    def test_06_known_device_case(self):
        """Routine transaction on enrolled trusted primary device."""
        rule = NewDeviceRule()
        signals = rule.evaluate(self.conn, "TXN-00001")
        self.assertEqual(len(signals), 0, "Enrolled trusted device should not trigger new device signal")

    # -------------------------------------------------------------------------
    # Test 7 & 8: New Beneficiary
    # -------------------------------------------------------------------------
    def test_07_new_beneficiary_positive_case(self):
        """First time transfer to rogue beneficiary BEN-00088."""
        rule = NewBeneficiaryRule()
        signals = rule.evaluate(self.conn, "TXN-00801")
        self.assertTrue(len(signals) >= 1, "Expected new beneficiary signal on TXN-00801")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-BEN-03")
        self.assertEqual(sig.evidence_data["beneficiary_id"], "BEN-00088")

    def test_08_existing_beneficiary_case(self):
        """Subsequent transaction to already utilized beneficiary."""
        # Query a pair that has >= 2 transactions
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT customer_id, beneficiary_id 
            FROM transactions 
            GROUP BY customer_id, beneficiary_id 
            HAVING COUNT(*) > 1 
            LIMIT 1;
        """)
        pair = cursor.fetchone()
        if pair:
            cid, bid = pair
            cursor.execute("SELECT transaction_id FROM transactions WHERE customer_id = ? AND beneficiary_id = ? ORDER BY timestamp DESC LIMIT 1;", (cid, bid))
            second_tx = cursor.fetchone()[0]
            rule = NewBeneficiaryRule()
            signals = rule.evaluate(self.conn, second_tx)
            self.assertEqual(len(signals), 0, "Repeated beneficiary transfer should not trigger new beneficiary signal")

    # -------------------------------------------------------------------------
    # Test 9 & 10: Geographic / Impossible Travel
    # -------------------------------------------------------------------------
    def test_09_geographic_anomaly_positive_case(self):
        """Scenario E: ATM cash-out in Lubumbashi 30 mins after POS payment in Kinshasa."""
        rule = GeographicVelocityRule(max_plausible_speed_kmh=600.0)
        signals = rule.evaluate(self.conn, "TXN-00820")
        self.assertTrue(len(signals) >= 1, "Expected impossible travel signal on TXN-00820")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-GEO-03")
        self.assertEqual(sig.severity, "CRITICAL")
        self.assertGreater(sig.evidence_data["implied_speed_kmh"], 600.0)
        self.assertEqual(sig.evidence_data["distance_km"], 1560.0)

    def test_10_normal_geographic_case(self):
        """Transaction in customer's primary registered city."""
        rule = GeographicVelocityRule(max_plausible_speed_kmh=600.0)
        signals = rule.evaluate(self.conn, "TXN-00819")
        self.assertEqual(len(signals), 0, "Normal city transaction should not trigger impossible travel")

    # -------------------------------------------------------------------------
    # Test 11 & 12: Shared Device
    # -------------------------------------------------------------------------
    def test_11_shared_device_positive_case(self):
        """Scenario C: DEV-00125 shared across 4 distinct customers."""
        rule = SharedDeviceRule(min_distinct_customers=2)
        signals = rule.evaluate(self.conn, "TXN-00808")
        self.assertTrue(len(signals) >= 1, "Expected shared device signal on TXN-00808")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-DEV-SHR-01")
        self.assertGreaterEqual(sig.evidence_data["distinct_customers_count"], 4)

    def test_12_normal_device_relationship_case(self):
        """Device associated strictly with 1 customer."""
        rule = SharedDeviceRule(min_distinct_customers=2)
        signals = rule.evaluate(self.conn, "TXN-00001")
        self.assertEqual(len(signals), 0, "Exclusive device should not trigger shared device signal")

    # -------------------------------------------------------------------------
    # Test 13: Shared Beneficiary / Mule Aggregator
    # -------------------------------------------------------------------------
    def test_13_shared_beneficiary_positive_case(self):
        """Scenario D: BEN-00050 receives funds from multiple distinct customers."""
        rule = SharedBeneficiaryRule(min_distinct_senders=3)
        signals = rule.evaluate(self.conn, "TXN-00812")
        self.assertTrue(len(signals) >= 1, "Expected mule aggregator signal on TXN-00812")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-MULE-04")
        self.assertGreaterEqual(sig.evidence_data["distinct_senders_count"], 3)

    # -------------------------------------------------------------------------
    # Test 14 & 15: Structuring / Smurfing
    # -------------------------------------------------------------------------
    def test_14_structuring_positive_case(self):
        """Scenario G: 4 sequential transfers between $9,400 and $9,800 on CUS-00062."""
        rule = StructuringRule(reporting_threshold_usd=10000.0)
        signals = rule.evaluate(self.conn, "TXN-00825")
        self.assertTrue(len(signals) >= 1, "Expected structuring signal on TXN-00825")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-SMURF-06")
        self.assertGreaterEqual(sig.evidence_data["cluster_transaction_count"], 2)

    def test_15_normal_transaction_sequence(self):
        """Standard small P2P transfer does not trigger structuring."""
        rule = StructuringRule()
        signals = rule.evaluate(self.conn, "TXN-00010")
        self.assertEqual(len(signals), 0, "Routine transaction should not trigger structuring")

    # -------------------------------------------------------------------------
    # Test 16 & 17: Authentication Anomaly
    # -------------------------------------------------------------------------
    def test_16_authentication_anomaly_positive_case(self):
        """Scenario F: CUS-00055 has 4 consecutive failed PIN attempts preceding TXN-00821."""
        rule = AuthenticationAnomalyRule(min_failed_attempts=3)
        signals = rule.evaluate(self.conn, "TXN-00821")
        self.assertTrue(len(signals) >= 1, "Expected authentication anomaly signal on TXN-00821")
        sig = signals[0]
        self.assertEqual(sig.rule_code, "R-AUTH-08")
        self.assertGreaterEqual(sig.evidence_data["failed_attempts_count"], 3)

    def test_17_normal_authentication_case(self):
        """Clean session without failed credential attempts."""
        rule = AuthenticationAnomalyRule(min_failed_attempts=3)
        signals = rule.evaluate(self.conn, "TXN-00001")
        self.assertEqual(len(signals), 0, "Clean login history should not trigger auth anomaly")

    # -------------------------------------------------------------------------
    # Test 18 & 19: Behavioural Deviation
    # -------------------------------------------------------------------------
    def test_18_behavioural_deviation_positive_case(self):
        """Scenario H: 03:45 AM off-hours transfer outside customer baseline."""
        rule = BehaviouralDeviationRule()
        signals = rule.evaluate(self.conn, "TXN-00826")
        self.assertTrue(len(signals) >= 1, "Expected behavioral off-hours deviation on TXN-00826")
        sig = signals[0]
        self.assertIn("R-BEH-09", sig.rule_code)

    def test_19_normal_behaviour_case(self):
        """Daytime transaction during customer's active hours."""
        rule = BehaviouralDeviationRule()
        signals = rule.evaluate(self.conn, "TXN-00015")
        self.assertEqual(len(signals), 0, "Normal active hour transaction should not trigger deviation")

    # -------------------------------------------------------------------------
    # Test 20: Multi-Signal Correlation
    # -------------------------------------------------------------------------
    def test_20_multi_signal_correlation(self):
        """TXN-00826 combines New Device + VPN IP + Off-Hours + High Value."""
        res = self.engine.evaluate_transaction("TXN-00826")
        self.assertIsNotNone(res)
        self.assertTrue(res.is_flagged)
        self.assertGreaterEqual(len(res.signals), 2)
        self.assertGreaterEqual(res.risk_score, 85)
        self.assertEqual(res.severity, "CRITICAL")
        self.assertIsNotNone(res.evidence_packet)
        self.assertIn("tier_1_exact_data", res.evidence_packet.to_dict())
        self.assertIn("tier_2_calculated", res.evidence_packet.to_dict())
        self.assertIn("tier_3_retrieved_evidence", res.evidence_packet.to_dict())

    # -------------------------------------------------------------------------
    # Test 21: Legitimate High-Value False Positive Mitigation
    # -------------------------------------------------------------------------
    def test_21_legitimate_high_value_mitigation(self):
        """TXN-00751 is a $68,898 USD corporate vendor payment with mitigating factors."""
        res = self.engine.evaluate_transaction("TXN-00751")
        self.assertIsNotNone(res)
        # Even with high amount, mitigating factors (Corporate KYC Tier-3 + Vendor) keep score controlled
        self.assertLess(res.risk_score, 70, "Legitimate corporate payment risk score should be discounted by mitigations")
        self.assertIn(res.severity, ["LOW", "MEDIUM"])

    # -------------------------------------------------------------------------
    # Test 22: Legitimate Travel Scenario
    # -------------------------------------------------------------------------
    def test_22_legitimate_travel_scenario(self):
        """TXN-00761 is customer travelling over 3 days (plausible elapsed time)."""
        rule = GeographicVelocityRule(max_plausible_speed_kmh=600.0)
        signals = rule.evaluate(self.conn, "TXN-00761")
        self.assertEqual(len(signals), 0, "Multi-day travel is physically plausible and should not trigger velocity anomaly")

    # -------------------------------------------------------------------------
    # Test 23: Legitimate Off-Hours Activity Context
    # -------------------------------------------------------------------------
    def test_23_legitimate_off_hours_context(self):
        """TXN-00764 hospital payment at 02:30 AM."""
        res = self.engine.evaluate_transaction("TXN-00764")
        self.assertIsNotNone(res)
        # Verify evidence packet captures the merchant hospital beneficiary
        packet = res.evidence_packet
        self.assertEqual(packet.exact_data["beneficiary"]["beneficiary_id"], "BEN-00004")

    # -------------------------------------------------------------------------
    # Test 24: Legitimate Device Upgrade Verification
    # -------------------------------------------------------------------------
    def test_24_legitimate_device_upgrade_verification(self):
        """Clean device verification workflow."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT device_id FROM devices WHERE trust_status = 'Trusted_Enrolled' LIMIT 1;")
        trusted_dev = cursor.fetchone()[0]
        cursor.execute("SELECT transaction_id FROM transactions WHERE device_id = ? LIMIT 1;", (trusted_dev,))
        tx_id = cursor.fetchone()[0]
        rule = NewDeviceRule()
        signals = rule.evaluate(self.conn, tx_id)
        self.assertEqual(len(signals), 0, "Trusted enrolled device should pass cleanly")


if __name__ == "__main__":
    unittest.main()
