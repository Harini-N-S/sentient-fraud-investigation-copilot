"""
Rawbank Sentient Fraud Intelligence Platform
Phase 6 Sentient Fraud Investigation Copilot - Smoke Test Script
-----------------------------------------------------------------------------
Performs live Groq smoke test if GROQ_API_KEY is configured in the environment.
If GROQ_API_KEY is absent, gracefully documents:
"Live Groq smoke test skipped because GROQ_API_KEY was not configured."
And executes end-to-end pipeline verification using mock adapter.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app.config import settings
from backend.app.llm import (
    CopilotInvestigateRequest,
    copilot_service,
    GroqClient
)


def run_smoke_test():
    print("=" * 70)
    print("RAWBANK SENTIENT FRAUD INTELLIGENCE PLATFORM")
    print("Phase 6 Sentient Fraud Investigation Copilot Smoke Test")
    print("=" * 70)

    groq_client = GroqClient()
    is_live_configured = groq_client.is_configured()

    if is_live_configured:
        print("\n[+] GROQ_API_KEY detected in environment.")
        print(f"[+] Configured model: {settings.groq_model}")
        print("[*] Executing LIVE investigation request: 'Why was customer CUS-00014 flagged?'...")
        try:
            req = CopilotInvestigateRequest(
                question="Why was customer CUS-00014 flagged?",
                use_mock=False
            )
            response = copilot_service.investigate(req)
            print("\n[SUCCESS] Live Groq response received and validated:")
            print(f"  Model Used: {response.model_used}")
            print(f"  Deterministic Risk Score: {response.risk_assessment.risk_score} (Severity: {response.risk_assessment.severity})")
            print(f"  Summary: {response.summary[:150]}...")
            print(f"  Supporting Evidence Items: {len(response.supporting_evidence)}")
            print(f"  Counter Evidence Items: {len(response.counter_evidence)}")
            print(f"  Evidence Gaps Documented: {len(response.evidence_gaps)}")
            print(f"  Provenance Validated: {response.provenance_validated}")
            print(f"  Processing Time: {response.processing_time_ms} ms")
        except Exception as e:
            print(f"\n[ERROR] Live Groq call failed: {e}")
            sys.exit(1)
    else:
        print("\n[NOTICE] Live Groq smoke test skipped because GROQ_API_KEY was not configured.")
        print("[*] Executing verified offline end-to-end smoke test using MockLLMAdapter...")
        req = CopilotInvestigateRequest(
            question="Why was customer CUS-00014 flagged?",
            use_mock=True
        )
        response = copilot_service.investigate(req)
        print("\n[SUCCESS] End-to-end investigation pipeline executed successfully:")
        print(f"  Model Used: {response.model_used}")
        print(f"  Deterministic Risk Score: {response.risk_assessment.risk_score} (Severity: {response.risk_assessment.severity})")
        print(f"  Summary: {response.summary[:150]}...")
        print(f"  Supporting Evidence Items: {len(response.supporting_evidence)}")
        print(f"  Counter Evidence Items: {len(response.counter_evidence)}")
        print(f"  Evidence Gaps Documented: {len(response.evidence_gaps)}")
        print(f"  Provenance Validated: {response.provenance_validated}")
        print(f"  Invalid Citations Removed: {len(response.invalid_citations_removed)}")
        print(f"  Processing Time: {response.processing_time_ms} ms")

    print("\n" + "=" * 70)
    print("Phase 6 Smoke Test Completed Successfully")
    print("=" * 70)


if __name__ == "__main__":
    run_smoke_test()
