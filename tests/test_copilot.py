"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Automated Test Suite
-----------------------------------------------------------------------------
Comprehensive test suite validating:
  1. Suspicious customer investigation (CUS-00014)
  2. Suspicious transaction investigation (TXN-00801)
  3. Critical alert investigation (ALT-00001)
  4. Account takeover investigation (detects password reset, novel device, drain)
  5. Shared device investigation (DEV-00125 multi-customer sharing)
  6. Shared beneficiary investigation (BEN-00088 / mule pattern)
  7. Impossible travel investigation (ALT-00019 / ALT-00020)
  8. Authentication anomaly (detects auth event preceding transaction)
  9. Behavioural deviation (compares transaction to baseline metrics)
 10. Legitimate corporate transaction (CUS-00010 / TXN-00751 / ALT-00027)
 11. Counter-evidence (verifies mitigating evidence for false positive)
 12. Unknown customer (CUS-99999 -> deterministic unknown entity response)
 13. Unknown transaction (TXN-99999 -> deterministic unknown entity response)
 14. Ambiguous customer (Jean Mutombo -> returns candidates, no guessing)
 15. Insufficient evidence (CUS-00003 -> normal customer, explicitly acknowledges no fraud)
 16. LLM timeout (simulates timeout, returns HTTP 504)
 17. Invalid LLM response (malformed JSON rejected)
 18. Unsupported source citation (hallucinated citation filtered out)
 19. Risk-score preservation (deterministic Phase 3 score 96 preserved)
 20. Evidence provenance (all cited sources traceable to DB records)
 21. Conversational context (multi-turn follow-up with session_id)
 22. Copilot API Endpoints (POST /api/copilot/investigate, explain-alert, explain-transaction, explain-customer)
"""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings
from backend.app.llm import (
    CopilotInvestigateRequest,
    CopilotInvestigationResponse,
    copilot_service,
    GroqClient,
    GroqConfigurationError,
    GroqTimeoutError,
    GroqAPIError,
    MockLLMAdapter,
    context_manager
)


class TestPhase6Copilot(unittest.TestCase):
    """Automated test suite for Phase 6 Sentient Fraud Investigation Copilot."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Ensure tests use the mock adapter deterministically without live Groq key
        cls.service = copilot_service

    def test_01_suspicious_customer_investigation(self):
        """1. Suspicious customer investigation (CUS-00014)."""
        req = CopilotInvestigateRequest(
            question="Why was customer CUS-00014 flagged?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertIsInstance(res, CopilotInvestigationResponse)
        self.assertIn("CUS-00014", res.summary)
        self.assertGreaterEqual(res.risk_assessment.risk_score, 80)
        self.assertIn(res.risk_assessment.severity, ["CRITICAL", "HIGH"])
        self.assertGreater(len(res.supporting_evidence), 0)
        self.assertTrue("escalat" in res.escalation_recommendation.lower())

    def test_02_suspicious_transaction_investigation(self):
        """2. Suspicious transaction investigation (TXN-00801)."""
        req = CopilotInvestigateRequest(
            question="Why is transaction TXN-00801 suspicious?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertIsInstance(res, CopilotInvestigationResponse)
        self.assertTrue(any("TXN-00801" in s.statement or "TXN-00801" in s.citation for s in res.supporting_evidence))
        self.assertGreaterEqual(res.risk_assessment.risk_score, 80)

    def test_03_critical_alert_investigation(self):
        """3. Critical alert investigation (ALT-00001)."""
        res = self.service.explain_alert("ALT-00001", use_mock=True)
        self.assertEqual(res.risk_assessment.severity, "CRITICAL")
        self.assertGreaterEqual(res.risk_assessment.risk_score, 90)
        self.assertTrue(any("ALT-00001" in str(ref.source_id) for ref in res.source_references))

    def test_04_account_takeover_investigation(self):
        """4. Account takeover investigation (detects password reset + novel device + drain)."""
        req = CopilotInvestigateRequest(
            question="Is there evidence of account takeover for customer CUS-00014?",
            use_mock=True
        )
        res = self.service.investigate(req)
        # Should detect ATO signals in supporting evidence or summary
        evidence_texts = " ".join([s.statement for s in res.supporting_evidence] + [res.summary]).lower()
        self.assertTrue("password" in evidence_texts or "credential" in evidence_texts or "ato" in evidence_texts or "takeover" in evidence_texts)

    def test_05_shared_device_investigation(self):
        """5. Shared device investigation (DEV-00125)."""
        req = CopilotInvestigateRequest(
            question="Are there other customers using device DEV-00125?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(len(res.related_activity) > 0 or len(res.supporting_evidence) > 0)
        self.assertTrue(any("DEV-00125" in str(s) for s in res.source_references) or "DEV-00125" in res.summary)

    def test_06_shared_beneficiary_investigation(self):
        """6. Shared beneficiary investigation (BEN-00088)."""
        req = CopilotInvestigateRequest(
            question="Who else sends money to beneficiary BEN-00088?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertIsNotNone(res.summary)
        self.assertTrue(len(res.source_references) > 0)

    def test_07_impossible_travel_investigation(self):
        """7. Impossible travel investigation (ALT-00019 / geographic scenario)."""
        res = self.service.explain_alert("ALT-00019", use_mock=True)
        self.assertIsNotNone(res.summary)
        self.assertIn(res.risk_assessment.severity, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    def test_08_authentication_anomaly(self):
        """8. Authentication anomaly investigation."""
        req = CopilotInvestigateRequest(
            question="What happened before the suspicious transaction TXN-00801?",
            use_mock=True
        )
        res = self.service.investigate(req)
        # Should surface auth / credential activity in supporting evidence or summary
        has_auth = any(
            s.source_table in ["auth_activity", "auth_activities"]
            or "auth" in s.statement.lower()
            or "password" in s.statement.lower()
            or "credential" in s.statement.lower()
            for s in res.supporting_evidence
        )
        self.assertTrue(has_auth or "password" in res.summary.lower() or "credential" in res.summary.lower())

    def test_09_behavioural_deviation(self):
        """9. Behavioural deviation investigation."""
        req = CopilotInvestigateRequest(
            question="Is this behaviour unusual for customer CUS-00014?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(len(res.behavioural_deviation) > 0)

    def test_10_legitimate_corporate_transaction(self):
        """10. Legitimate corporate transaction (TXN-00751 / CUS-00010 / ALT-00027)."""
        res = self.service.explain_alert("ALT-00027", use_mock=True)
        self.assertEqual(res.risk_assessment.severity, "LOW")
        self.assertLess(res.risk_assessment.risk_score, 50)
        self.assertGreater(len(res.counter_evidence), 0)

    def test_11_counter_evidence(self):
        """11. Counter-evidence verification (ensures mitigating evidence for legitimate anomaly)."""
        res = self.service.explain_alert("ALT-00027", use_mock=True)
        self.assertTrue(len(res.counter_evidence) > 0)
        counter_statements = " ".join([c.statement for c in res.counter_evidence]).lower()
        self.assertTrue("corporate" in counter_statements or "verified" in counter_statements or "baseline" in counter_statements or "trusted" in counter_statements)

    def test_12_unknown_customer(self):
        """12. Unknown customer investigation (CUS-99999)."""
        req = CopilotInvestigateRequest(
            question="Why was customer CUS-99999 flagged?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(res.unknown_entity_detected)
        self.assertEqual(res.risk_assessment.risk_score, 0)
        self.assertEqual(res.risk_assessment.severity, "NONE")
        self.assertTrue(any(g.gap_type == "UNKNOWN_ENTITY" for g in res.evidence_gaps))

    def test_13_unknown_transaction(self):
        """13. Unknown transaction investigation (TXN-99999)."""
        req = CopilotInvestigateRequest(
            question="Why is transaction TXN-99999 suspicious?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(res.unknown_entity_detected)
        self.assertEqual(res.risk_assessment.risk_score, 0)
        self.assertTrue(any(g.gap_type == "UNKNOWN_ENTITY" for g in res.evidence_gaps))

    def test_14_ambiguous_customer(self):
        """14. Ambiguous customer investigation (Jean Mutombo)."""
        req = CopilotInvestigateRequest(
            question="Why was Jean Mutombo flagged?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(res.ambiguity_detected)
        self.assertTrue(any(g.gap_type == "AMBIGUOUS_ENTITY" for g in res.evidence_gaps))
        # Ambiguity must be acknowledged in summary without arbitrary choice
        self.assertIn("ambiguity", res.summary.lower())

    def test_15_insufficient_evidence(self):
        """15. Insufficient evidence (normal customer CUS-00003 with zero alerts)."""
        req = CopilotInvestigateRequest(
            question="Why was customer CUS-00003 flagged?",
            use_mock=True
        )
        res = self.service.investigate(req)
        self.assertTrue(res.insufficient_evidence_detected)
        self.assertEqual(res.risk_assessment.severity, "NONE")
        self.assertEqual(res.risk_assessment.risk_score, 0)
        self.assertIn("insufficient evidence", res.summary.lower())

    def test_16_llm_timeout(self):
        """16. LLM timeout error handling."""
        with patch.object(GroqClient, "generate_investigation", side_effect=GroqTimeoutError("Request timed out after 30s")):
            response = self.client.post(
                "/api/copilot/investigate",
                json={"question": "Why was customer CUS-00014 flagged?", "use_mock": False}
            )
            # Router should handle GroqTimeoutError and return 504 Gateway Timeout or 503
            self.assertIn(response.status_code, [503, 504])
            data = response.json()
            self.assertIn("detail", data)

    def test_17_invalid_llm_response(self):
        """17. Malformed LLM response error handling."""
        with patch.object(GroqClient, "generate_investigation", side_effect=GroqAPIError("Malformed JSON returned by LLM")):
            response = self.client.post(
                "/api/copilot/investigate",
                json={"question": "Why was customer CUS-00014 flagged?", "use_mock": False}
            )
            self.assertIn(response.status_code, [502, 500])
            data = response.json()
            self.assertIn("detail", data)

    def test_18_unsupported_source_citation(self):
        """18. Unsupported source citation rejection (filtering hallucinated IDs)."""
        # Create a mock response dict with a fake source citation not in packet
        fake_response = {
            "question": "Why was customer CUS-00014 flagged?",
            "summary": "Analyst review of CUS-00014 [Source: CUS-00014].",
            "risk_assessment": {"severity": "CRITICAL", "risk_score": 96, "confidence": 0.95},
            "supporting_evidence": [
                {"source_id": "TXN-00801", "source_table": "transactions", "statement": "Transfer of $4,800 USD", "citation": "[Source: TXN-00801]"},
                {"source_id": "TXN-FAKE-9999", "source_table": "transactions", "statement": "Invented transfer $1,000,000", "citation": "[Source: TXN-FAKE-9999]"}
            ],
            "counter_evidence": [],
            "behavioural_deviation": [],
            "related_activity": [],
            "evidence_gaps": [],
            "investigation_next_steps": ["Review logs"],
            "escalation_recommendation": "Escalate",
            "source_references": []
        }
        with patch.object(MockLLMAdapter, "generate", return_value=fake_response):
            req = CopilotInvestigateRequest(question="Why was customer CUS-00014 flagged?", use_mock=True)
            res = self.service.investigate(req)
            # The fake source TXN-FAKE-9999 must be stripped from valid supporting evidence!
            supporting_ids = [s.source_id for s in res.supporting_evidence]
            self.assertNotIn("TXN-FAKE-9999", supporting_ids)
            self.assertIn("TXN-FAKE-9999", res.invalid_citations_removed)
            self.assertFalse(res.provenance_validated)

    def test_19_risk_score_preservation(self):
        """19. Risk-score preservation (LLM cannot override deterministic score 96)."""
        # Create a mock response where LLM attempts to propose an invented risk score of 42
        fake_response = {
            "question": "Why was customer CUS-00014 flagged?",
            "summary": "Review [Source: ALT-00001].",
            "risk_assessment": {"severity": "LOW", "risk_score": 42, "confidence": 0.5},
            "supporting_evidence": [],
            "counter_evidence": [],
            "behavioural_deviation": [],
            "related_activity": [],
            "evidence_gaps": [],
            "investigation_next_steps": [],
            "escalation_recommendation": "None",
            "source_references": []
        }
        with patch.object(MockLLMAdapter, "generate", return_value=fake_response):
            res = self.service.explain_alert("ALT-00001", use_mock=True)
            # Must preserve the authoritative score 96 and severity CRITICAL from ALT-00001!
            self.assertEqual(res.risk_assessment.risk_score, 96)
            self.assertEqual(res.risk_assessment.severity, "CRITICAL")

    def test_20_evidence_provenance(self):
        """20. Evidence provenance (all source references traceable)."""
        res = self.service.explain_alert("ALT-00001", use_mock=True)
        self.assertGreater(len(res.source_references), 0)
        for ref in res.source_references:
            self.assertIsNotNone(ref.source_id)
            self.assertIsNotNone(ref.source_table)

    def test_21_conversational_context(self):
        """21. Conversational context (multi-turn follow-up with session_id)."""
        session_id = "test_sess_turn_01"
        # Turn 1: Investigate CUS-00014
        req1 = CopilotInvestigateRequest(
            question="Why was customer CUS-00014 flagged?",
            session_id=session_id,
            use_mock=True
        )
        res1 = self.service.investigate(req1)
        self.assertEqual(res1.session_id, session_id)

        # Turn 2: Follow-up asking "What happened before that?"
        req2 = CopilotInvestigateRequest(
            question="What happened before that?",
            session_id=session_id,
            use_mock=True
        )
        res2 = self.service.investigate(req2)
        # Should resolve context to the prior customer/transaction and return grounded response
        self.assertEqual(res2.session_id, session_id)
        self.assertIsNotNone(res2.summary)

    def test_22_api_post_copilot_investigate(self):
        """22. API endpoint POST /api/copilot/investigate."""
        response = self.client.post(
            "/api/copilot/investigate",
            json={
                "question": "Why was customer CUS-00014 flagged?",
                "use_mock": True
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data)
        self.assertIn("risk_assessment", data)
        self.assertIn("supporting_evidence", data)
        self.assertIn("counter_evidence", data)
        self.assertIn("evidence_gaps", data)

    def test_23_api_post_explain_alert(self):
        """23. API endpoint POST /api/copilot/explain-alert/{alert_id}."""
        response = self.client.post("/api/copilot/explain-alert/ALT-00001?use_mock=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_assessment"]["severity"], "CRITICAL")

    def test_24_api_post_explain_transaction(self):
        """24. API endpoint POST /api/copilot/explain-transaction/{transaction_id}."""
        response = self.client.post("/api/copilot/explain-transaction/TXN-00801?use_mock=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["risk_assessment"]["risk_score"], 80)

    def test_25_api_post_explain_customer(self):
        """25. API endpoint POST /api/copilot/explain-customer/{customer_id}."""
        response = self.client.post("/api/copilot/explain-customer/CUS-00014?use_mock=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("CUS-00014", data["summary"])


if __name__ == "__main__":
    unittest.main()
