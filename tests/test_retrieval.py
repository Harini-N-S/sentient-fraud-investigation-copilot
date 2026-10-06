"""
Rawbank Sentient Fraud Intelligence Platform
Phase 5 Semantic Retrieval & Evidence Layer Test Suite
-----------------------------------------------------------------------------
Comprehensive automated validation verifying:
  1. Exact customer lookup
  2. Exact transaction lookup
  3. Exact alert lookup
  4. Entity resolution (Exact IDs, normalized IDs, natural names)
  5. Unknown entity handling (Zero hallucination, explicit evidence gaps)
  6. Ambiguous entity handling (Disambiguation candidate return)
  7. Query parser intent and filter extraction
  8. Indexing sanity and multi-type document counts (2,600+ docs)
  9. Explainable ranking and BM25 scoring
 10. Standardized forensic evidence packet assembly
 11. Field-level provenance verification (source_table, source_id, field, value)
 12. Explicit evidence gap detection (MISSING_BASELINE, UNVERIFIED_DEVICE, etc.)
 13. Supporting evidence vs Counter-evidence for legitimate anomalies (False Positives)
 14. Relationship graph retrieval & bounded expansion limits
 15. All 17 Required Investigation Scenarios (Normal, ATO, Travel, Mule, Structuring, etc.)
 16. Retrieval API Endpoints (POST /api/retrieval/query, GET /api/search, etc.)
Zero LLM dependencies.
"""

import sqlite3
import unittest
from fastapi.testclient import TestClient
from backend.app.config import settings
from backend.app.main import app
from backend.app.retrieval import (
    EntityResolver,
    QueryParser,
    indexer,
    retriever,
    evidence_builder,
    RetrievalRanker
)
from backend.app.retrieval.models import StandardEvidencePacket


class TestPhase5RetrievalAndEvidence(unittest.TestCase):
    """Automated test suite for Phase 5 Semantic Retrieval & Evidence Layer."""

    @classmethod
    def setUpClass(cls):
        cls.db_path = str(settings.database_path)
        cls.conn = sqlite3.connect(cls.db_path)
        cls.client = TestClient(app)
        indexer.ensure_indexed()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # -------------------------------------------------------------------------
    # 1. ENTITY RESOLUTION TESTS
    # -------------------------------------------------------------------------
    def test_01_exact_customer_id_resolution(self):
        """Resolves exact customer ID with 1.0 confidence and exact_id method."""
        resolved = EntityResolver.resolve_text(self.conn, "investigate customer CUS-00014")
        self.assertEqual(len(resolved), 1)
        ent = resolved[0]
        self.assertEqual(ent.entity_type, "customer")
        self.assertEqual(ent.canonical_id, "CUS-00014")
        self.assertEqual(ent.confidence, 1.0)
        self.assertEqual(ent.matching_method, "exact_id")
        self.assertFalse(ent.is_ambiguous)
        self.assertIsNotNone(ent.details)
        self.assertEqual(ent.details["full_name"], "Christelle Mutombo")

    def test_02_normalized_customer_id_resolution(self):
        """Resolves variations like CUST-0012, CUS-14, CUST-14 to canonical CUS-XXXXX."""
        # Variation 1: CUST-0012
        r1 = EntityResolver.resolve_text(self.conn, "check customer CUST-0012")
        self.assertEqual(len(r1), 1)
        self.assertEqual(r1[0].canonical_id, "CUS-00012")
        self.assertEqual(r1[0].matching_method, "normalized_id")
        self.assertEqual(r1[0].confidence, 1.0)

        # Variation 2: CUS-14
        r2 = EntityResolver.resolve_text(self.conn, "profile for CUS-14")
        self.assertEqual(len(r2), 1)
        self.assertEqual(r2[0].canonical_id, "CUS-00014")
        self.assertEqual(r2[0].confidence, 1.0)

    def test_03_transaction_and_alert_id_resolution(self):
        """Resolves transaction, alert, device, and beneficiary IDs."""
        query = "transaction TXN-00801 triggered alert ALT-00001 on device DEV-00127 to beneficiary BEN-00088"
        resolved = EntityResolver.resolve_text(self.conn, query)
        types = {r.entity_type: r.canonical_id for r in resolved}
        self.assertIn("transaction", types)
        self.assertIn("alert", types)
        self.assertIn("device", types)
        self.assertIn("beneficiary", types)
        self.assertEqual(types["transaction"], "TXN-00801")
        self.assertEqual(types["alert"], "ALT-00001")
        self.assertEqual(types["device"], "DEV-00127")
        self.assertEqual(types["beneficiary"], "BEN-00088")

    def test_04_unknown_entity_resolution(self):
        """Unknown entity IDs produce confidence 0.0 and unknown_identifier without hallucination."""
        resolved = EntityResolver.resolve_text(self.conn, "customer CUS-99999 and transaction TXN-99999")
        self.assertEqual(len(resolved), 2)
        for r in resolved:
            self.assertEqual(r.confidence, 0.0)
            self.assertEqual(r.matching_method, "unknown_identifier")
            self.assertIsNone(r.details)

    def test_05_natural_language_name_resolution(self):
        """Resolves customer full name Christelle Mutombo to CUS-00014 with high confidence."""
        resolved = EntityResolver.resolve_text(self.conn, "Why was customer Christelle Mutombo flagged?")
        self.assertTrue(any(r.canonical_id == "CUS-00014" for r in resolved))
        ent = [r for r in resolved if r.canonical_id == "CUS-00014"][0]
        self.assertGreaterEqual(ent.confidence, 0.85)

    def test_06_ambiguous_entity_resolution(self):
        """Ambiguous name matching multiple customers returns is_ambiguous=True and candidate list."""
        resolved = EntityResolver.resolve_text(self.conn, "customer Jean Mutombo")
        self.assertTrue(len(resolved) > 0)
        amb_ent = resolved[0]
        self.assertTrue(amb_ent.is_ambiguous)
        self.assertEqual(amb_ent.confidence, 0.50)
        self.assertGreaterEqual(len(amb_ent.candidates), 2)
        # Verify candidate IDs exist in DB
        for cand in amb_ent.candidates:
            self.assertTrue(cand["customer_id"].startswith("CUS-"))

    # -------------------------------------------------------------------------
    # 2. QUERY PARSER TESTS
    # -------------------------------------------------------------------------
    def test_07_query_parser_intent_and_filters(self):
        """Extracts intent and metadata filters (severity, scenario, currency)."""
        pq = QueryParser.parse(self.conn, "critical alerts for impossible travel in Goma over 4000 USD")
        self.assertEqual(pq.filters.get("severity"), "CRITICAL")
        self.assertEqual(pq.filters.get("scenario_type"), "IMPOSSIBLE_TRAVEL")
        self.assertEqual(pq.filters.get("city"), "Goma")
        self.assertEqual(pq.filters.get("currency"), "USD")
        self.assertEqual(pq.filters.get("min_amount_usd"), 4000.0)
        self.assertIn("goma", [k.lower() for k in pq.keywords])

    def test_08_query_parser_relationship_intent(self):
        """Recognizes relational intent for shared devices or co-users."""
        pq = QueryParser.parse(self.conn, "customers sharing device DEV-00125")
        self.assertTrue(pq.is_relational)
        self.assertEqual(pq.relationship_target, "co_users")
        self.assertEqual(pq.intent, "FIND_RELATIONSHIPS")
        self.assertTrue(any(e.canonical_id == "DEV-00125" for e in pq.resolved_entities))

    # -------------------------------------------------------------------------
    # 3. INDEXING & RANKING TESTS
    # -------------------------------------------------------------------------
    def test_09_indexer_document_counts_and_types(self):
        """Verifies that all 9 database tables + relationship clusters are indexed."""
        self.assertGreaterEqual(len(indexer.documents), 2500)
        expected_types = {
            "customer", "account", "transaction", "device", "beneficiary",
            "auth_activity", "behavioural_baseline", "alert", "fraud_signal",
            "relationship", "rule_evidence"
        }
        indexed_types = set(indexer.by_type.keys())
        for et in expected_types:
            self.assertIn(et, indexed_types, f"Missing document type: {et}")
            self.assertGreater(len(indexer.by_type[et]), 0)

    def test_10_explainable_ranking_and_reasons(self):
        """Validates ranking transparently outputs score [0.0 - 1.0] and explainable reasons."""
        _, results = retriever.retrieve("Why was customer CUS-00014 flagged?", limit=5)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertGreater(top.relevance_score, 0.5)
        self.assertLessEqual(top.relevance_score, 1.0)
        self.assertIsInstance(top.relevance_reasons, list)
        self.assertGreater(len(top.relevance_reasons), 0)
        self.assertIn("provenance", top.model_dump())

    # -------------------------------------------------------------------------
    # 4. EVIDENCE PACKET & PROVENANCE TESTS
    # -------------------------------------------------------------------------
    def test_11_evidence_packet_provenance_preservation(self):
        """Guarantees every evidence item has strict database provenance (table, primary key, field, value)."""
        packet: StandardEvidencePacket = evidence_builder.build_for_query("investigate transaction TXN-00801")
        self.assertIsNotNone(packet.target_entity)
        self.assertGreater(len(packet.exact_data), 0)
        self.assertGreater(len(packet.calculated_information), 0)
        self.assertGreater(len(packet.retrieved_evidence), 0)

        for item in packet.exact_data:
            self.assertIn(item.type, ["EXACT_DATA", "CALCULATED", "RETRIEVED_EVIDENCE", "COUNTER_EVIDENCE"])
            self.assertTrue(item.source_table, "Evidence item missing source_table")
            self.assertTrue(item.source_id, "Evidence item missing source_id")
            self.assertTrue(item.field, "Evidence item missing field")
            self.assertIn("provenance", item.model_dump())

    def test_12_evidence_gap_detection_on_normal_customer(self):
        """Customer with no alerts explicitly surfaces NO_RELATED_ALERTS evidence gap."""
        # CUS-00003 is a normal customer with zero alerts
        packet: StandardEvidencePacket = evidence_builder.build_for_query("Why was customer CUS-00003 flagged?")
        gap_types = [g.gap_type for g in packet.evidence_gaps]
        self.assertIn("NO_RELATED_ALERTS", gap_types)
        # Verify no fabricated alerts
        alert_items = [e for e in packet.calculated_information if e.source_table == "alerts"]
        self.assertEqual(len(alert_items), 0)

    def test_13_counter_evidence_for_legitimate_anomaly(self):
        """Surfaces counter-evidence (corporate segment, trusted device, low risk) for legitimate corporate anomaly."""
        # CUS-00010, TXN-00751, ALT-00027 is a verified corporate payment
        packet: StandardEvidencePacket = evidence_builder.build_for_query("investigate corporate payment TXN-00751 for customer CUS-00010")
        self.assertGreater(len(packet.counter_evidence), 0)
        counter_fields = [ce.field for ce in packet.counter_evidence]
        self.assertTrue(any(f in ["customer_segment", "trust_status", "scenario_type"] for f in counter_fields))

    def test_14_unknown_entity_evidence_gaps_zero_fabrication(self):
        """Unknown entity queries produce explicit UNKNOWN_ENTITY gaps and zero fabricated ledger rows."""
        packet: StandardEvidencePacket = evidence_builder.build_for_query("investigate customer CUS-99999 and transaction TXN-99999")
        self.assertEqual(len(packet.exact_data), 0)
        gap_types = [g.gap_type for g in packet.evidence_gaps]
        self.assertIn("UNKNOWN_ENTITY", gap_types)

    # -------------------------------------------------------------------------
    # 5. ALL 17 REQUIRED INVESTIGATION SCENARIO VERIFICATIONS
    # -------------------------------------------------------------------------
    def test_15_scenario_01_normal_customer(self):
        """Scenario 1: Normal customer retrieval (CUS-00003)."""
        packet = evidence_builder.build_for_entity("customer", "CUS-00003")
        self.assertEqual(packet.target_entity["canonical_id"], "CUS-00003")
        self.assertTrue(any(g.gap_type == "NO_RELATED_ALERTS" for g in packet.evidence_gaps))

    def test_16_scenario_02_suspicious_customer(self):
        """Scenario 2: Suspicious customer retrieval (CUS-00014)."""
        packet = evidence_builder.build_for_entity("customer", "CUS-00014")
        self.assertEqual(packet.target_entity["canonical_id"], "CUS-00014")
        self.assertGreater(len(packet.calculated_information), 0)
        # Check alerts present
        alerts = [e for e in packet.calculated_information if e.source_table == "alerts"]
        self.assertGreater(len(alerts), 0)

    def test_17_scenario_03_high_value_legitimate_customer(self):
        """Scenario 3: High-value legitimate customer activity (CUS-00010)."""
        packet = evidence_builder.build_for_entity("customer", "CUS-00010")
        self.assertGreater(len(packet.counter_evidence), 0)

    def test_18_scenario_04_suspicious_transaction(self):
        """Scenario 4: Suspicious transaction (TXN-00801)."""
        packet = evidence_builder.build_for_entity("transaction", "TXN-00801")
        self.assertEqual(packet.target_entity["canonical_id"], "TXN-00801")
        # Check debit amount
        amt_item = [e for e in packet.exact_data if e.field == "amount_usd_equivalent"][0]
        self.assertEqual(amt_item.value, 4800.0)

    def test_19_scenario_05_shared_device(self):
        """Scenario 5: Shared device cluster (DEV-00125)."""
        packet = evidence_builder.build_for_entity("device", "DEV-00125")
        calc_items = [e for e in packet.calculated_information if e.field == "distinct_customer_count"]
        self.assertEqual(len(calc_items), 1)
        self.assertEqual(calc_items[0].value, 4)

    def test_20_scenario_06_shared_beneficiary(self):
        """Scenario 6: Shared mule beneficiary (BEN-00050)."""
        packet = evidence_builder.build_for_entity("beneficiary", "BEN-00050")
        sender_item = [e for e in packet.calculated_information if e.field == "distinct_sender_count"][0]
        self.assertGreaterEqual(sender_item.value, 10)

    def test_21_scenario_07_impossible_travel(self):
        """Scenario 7: Impossible travel scenario (ALT-00020 / CUS-00045)."""
        packet = evidence_builder.build_for_entity("alert", "ALT-00020")
        scen_items = [e for e in packet.calculated_information if "IMPOSSIBLE_TRAVEL" in str(e.description)]
        self.assertGreater(len(scen_items), 0)

    def test_22_scenario_08_authentication_anomaly(self):
        """Scenario 8: Authentication anomaly in ATO sequence."""
        packet = evidence_builder.build_for_entity("customer", "CUS-00014")
        auth_items = [e for e in packet.retrieved_evidence if e.source_table == "auth_activities"]
        self.assertGreater(len(auth_items), 0)
        self.assertTrue(any(e.value == "Password_Reset_Triggered" for e in auth_items))

    def test_23_scenario_09_account_takeover_sequence(self):
        """Scenario 9: Account takeover sequence (ALT-00001)."""
        packet = evidence_builder.build_for_entity("alert", "ALT-00001")
        self.assertTrue(any("ATO_DRAIN" in str(e.value) or "ATO_DRAIN" in str(e.description) for e in packet.calculated_information))

    def test_24_scenario_10_structuring_like_behaviour(self):
        """Scenario 10: Structuring-like behaviour (ALT-00022 / CUS-00062)."""
        packet = evidence_builder.build_for_entity("alert", "ALT-00022")
        self.assertTrue(any("STRUCTURING_SMURF" in str(e.value) or "STRUCTURING_SMURF" in str(e.description) for e in packet.calculated_information))

    def test_25_scenario_11_behavioural_deviation(self):
        """Scenario 11: Behavioural deviation against baseline profile."""
        packet = evidence_builder.build_for_entity("customer", "CUS-00014")
        baseline_items = [e for e in packet.retrieved_evidence if e.source_table == "behavioural_baselines"]
        self.assertGreater(len(baseline_items), 0)

    def test_26_scenario_12_multi_signal_critical_alert(self):
        """Scenario 12: Multi-signal critical alert (ALT-00001)."""
        packet = evidence_builder.build_for_entity("alert", "ALT-00001")
        signals = [e for e in packet.retrieved_evidence if e.source_table == "fraud_signals"]
        self.assertEqual(len(signals), 4)

    def test_27_scenario_13_false_positive_scenario(self):
        """Scenario 13: False positive corporate payment scenario (ALT-00027)."""
        packet = evidence_builder.build_for_entity("alert", "ALT-00027")
        self.assertGreater(len(packet.counter_evidence), 0)

    def test_28_scenario_14_unknown_customer_id(self):
        """Scenario 14: Unknown customer ID (CUS-99999)."""
        packet = evidence_builder.build_for_entity("customer", "CUS-99999")
        self.assertTrue(any(g.gap_type == "UNKNOWN_ENTITY" for g in packet.evidence_gaps))

    def test_29_scenario_15_unknown_transaction_id(self):
        """Scenario 15: Unknown transaction ID (TXN-99999)."""
        packet = evidence_builder.build_for_entity("transaction", "TXN-99999")
        self.assertTrue(any(g.gap_type == "UNKNOWN_ENTITY" for g in packet.evidence_gaps))

    def test_30_scenario_16_ambiguous_search(self):
        """Scenario 16: Ambiguous search."""
        packet = evidence_builder.build_for_query("customer Jean Mutombo")
        self.assertTrue(any(g.gap_type == "AMBIGUOUS_ENTITY" for g in packet.evidence_gaps))

    def test_31_scenario_17_insufficient_evidence(self):
        """Scenario 17: Insufficient evidence for empty or untargeted query."""
        packet = evidence_builder.build_for_query("some general random question without entities")
        self.assertTrue(any(g.gap_type == "INSUFFICIENT_QUERY_CONTEXT" for g in packet.evidence_gaps))

    # -------------------------------------------------------------------------
    # 6. RETRIEVAL API ENDPOINT TESTS
    # -------------------------------------------------------------------------
    def test_32_api_post_retrieval_query(self):
        """Tests POST /api/retrieval/query endpoint."""
        payload = {
            "query": "Why was customer CUS-00014 flagged?",
            "limit": 10,
            "include_evidence_packet": True
        }
        resp = self.client.post("/api/retrieval/query", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["query"], payload["query"])
        self.assertGreater(data["total_retrieved"], 0)
        self.assertGreater(len(data["results"]), 0)
        self.assertIsNotNone(data["evidence_packet"])
        self.assertEqual(data["evidence_packet"]["target_entity"]["canonical_id"], "CUS-00014")

    def test_33_api_get_entity_evidence(self):
        """Tests GET /api/entities/{entity_type}/{entity_id}/evidence endpoint."""
        resp = self.client.get("/api/entities/customer/CUS-00014/evidence")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["target_entity"]["canonical_id"], "CUS-00014")
        self.assertGreater(len(data["exact_data"]), 0)

        # 404 for nonexistent customer
        resp_404 = self.client.get("/api/entities/customer/CUS-99999/evidence")
        self.assertEqual(resp_404.status_code, 404)

        # 400 for unsupported entity type
        resp_400 = self.client.get("/api/entities/spaceship/SHIP-01/evidence")
        self.assertEqual(resp_400.status_code, 400)

    def test_34_api_get_entity_related(self):
        """Tests GET /api/entities/{entity_type}/{entity_id}/related endpoint."""
        resp = self.client.get("/api/entities/device/DEV-00125/related?max_depth=2&limit=10")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["entity_id"], "DEV-00125")
        self.assertGreaterEqual(data["total_relationships"], 4)
        self.assertIn("summary", data)

    def test_35_api_get_alert_evidence(self):
        """Tests GET /api/alerts/{alert_id}/evidence endpoint."""
        resp = self.client.get("/api/alerts/ALT-00001/evidence")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["target_entity"]["canonical_id"], "ALT-00001")
        self.assertGreater(len(data["calculated_information"]), 0)

        # 404 for nonexistent alert
        resp_404 = self.client.get("/api/alerts/ALT-99999/evidence")
        self.assertEqual(resp_404.status_code, 404)

    def test_36_api_get_search_with_filters(self):
        """Tests GET /api/search with hybrid filtering options."""
        resp = self.client.get("/api/search?q=impossible%20travel&severity=LOW")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["total_results"], 0)
        first = data["results"][0]
        self.assertIn("relevance_score", first)
        self.assertIn("relevance_reasons", first)


if __name__ == "__main__":
    unittest.main()
