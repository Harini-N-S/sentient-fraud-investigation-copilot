"""
Rawbank Sentient Fraud Intelligence Platform
Phase 8 Demonstration Scenarios Verification Script (Sections 5-11)
-----------------------------------------------------------------------------
Verifies the exact demonstration paths and expected evidence:
1. Account Takeover (ALT-00001, CUS-00014, TXN-00801, DEV-00127)
2. Shared Device Syndicate (DEV-00125)
3. Mule Beneficiary Aggregator (BEN-00088)
4. Legitimate Corporate Anomaly / False Positive Mitigation (CUS-00046)
5. Unknown Entity Handling (CUS-99999)
6. Ambiguous Entity Disambiguation (Jean Mutombo)
7. Clean Customer Baseline & Absence of Suspicion (CUS-00003)
"""

import json
import urllib.request
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"


def api_get(endpoint: str) -> Dict[str, Any]:
    url = f"{BASE_URL}{endpoint}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_post(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def verify_scenario_1():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 1: ACCOUNT TAKEOVER (ALT-00001)")
    print("=" * 80)
    # 1. Inspect Alert
    alert = api_get("/api/alerts/ALT-00001")
    alt_data = alert["alert"]
    print(f"Alert ID: {alt_data['alert_id']} | Risk Score: {alt_data['composite_risk_score']} | Severity: {alt_data['severity']}")
    print(f"Scenario: {alt_data['scenario_type']} | Customer: {alt_data['customer_id']} | Txn: {alt_data['transaction_id']}")
    
    # 2. Ask Copilot
    resp = api_post("/api/copilot/investigate", {
        "question": "Why was alert ALT-00001 triggered?",
        "entity_type": "alert",
        "entity_id": "ALT-00001",
        "use_mock": True
    })
    
    risk = resp.get("risk_assessment", {})
    supp = resp.get("supporting_evidence", [])
    steps = resp.get("investigation_next_steps", [])
    sources = resp.get("source_references", [])
    
    print(f"Copilot Risk Assessment : {risk.get('risk_score')}/100 ({risk.get('severity')})")
    print(f"Supporting Evidence     : {len(supp)} items (e.g. {supp[0].get('citation')})")
    print(f"Investigation Next Steps: {len(steps)} actions recommended")
    print(f"Source References       : {len(sources)} verified DB sources")
    
    ok = (alt_data['composite_risk_score'] == 96 and
          risk.get('risk_score') == 96 and
          risk.get('severity') == "CRITICAL" and
          len(supp) > 0 and len(sources) > 0)
    print(f"Scenario 1 Verification : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_2():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 2: SHARED DEVICE SYNDICATE (DEV-00125)")
    print("=" * 80)
    # 1. Device relationships
    rel = api_get("/api/entities/device/DEV-00125/relationships")
    print(f"Device: {rel['entity_id']} | Total Direct Relationships: {rel['total_relationships']}")
    linked_customers = [r for r in rel["relationships"] if r["target_type"] == "customer"]
    for c in linked_customers:
        print(f"  -> Connected Customer: {c['target_id']} (Reason: {c.get('relationship', c.get('target_label'))})")
    
    # 2. Ask Copilot
    resp = api_post("/api/copilot/investigate", {
        "question": "Which customers are connected to this device and why is the relationship relevant?",
        "entity_type": "device",
        "entity_id": "DEV-00125",
        "use_mock": True
    })
    
    print(f"Copilot Summary Snippet : {resp.get('summary')[:140]}...")
    print(f"Supporting Evidence Items: {len(resp.get('supporting_evidence', []))}")
    ok = len(linked_customers) >= 2 and len(resp.get('supporting_evidence', [])) > 0
    print(f"Scenario 2 Verification : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_3():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 3: MULE BENEFICIARY AGGREGATOR (BEN-00088)")
    print("=" * 80)
    # 1. Inspect Beneficiary
    ben = api_get("/api/beneficiaries/BEN-00088")
    ben_data = ben["beneficiary"]
    print(f"Beneficiary: {ben_data['beneficiary_id']} - {ben_data['beneficiary_name']}")
    print(f"Institution: {ben_data['institution_name']} | Known Mule Flag: {ben_data['is_known_mule']}")
    customers = ben.get("interacting_customers", [])
    tx_cnt = ben.get("transaction_count", 0)
    vol = ben.get("total_volume_usd", 0.0)
    print(f"Sender Statistics: {len(customers)} distinct senders, {tx_cnt} txns, ${vol:,.2f} USD")
    
    # 2. Ask Copilot
    resp = api_post("/api/copilot/investigate", {
        "question": "Who else sends money to this beneficiary and what pattern should an investigator examine?",
        "entity_type": "beneficiary",
        "entity_id": "BEN-00088",
        "use_mock": True
    })
    print(f"Copilot Summary Snippet : {resp.get('summary')[:140]}...")
    ok = (len(customers) == 9 and
          len(resp.get('supporting_evidence', [])) > 0)
    print(f"Scenario 3 Verification : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_4():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 4: FALSE POSITIVE / CORPORATE ANOMALY (CUS-00046)")
    print("=" * 80)
    # Search for legitimate corporate customer / corporate anomaly
    resp = api_post("/api/copilot/investigate", {
        "question": "What evidence could explain this activity as a legitimate corporate anomaly?",
        "entity_type": "customer",
        "entity_id": "CUS-00046",
        "use_mock": True
    })
    counters = resp.get("counter_evidence", [])
    print(f"Risk Score : {resp.get('risk_assessment', {}).get('risk_score')}/100 ({resp.get('risk_assessment', {}).get('severity')})")
    print(f"Counter-Evidence Mitigations: {len(counters)} items")
    for c in counters[:3]:
        print(f"  -> Mitigation: {c.get('statement')}")
    print(f"Escalation Recommendation: {resp.get('escalation_recommendation')}")
    ok = len(counters) > 0 or "mitigat" in resp.get('summary', '').lower() or "not support fraud" in resp.get('escalation_recommendation', '').lower()
    print(f"Scenario 4 Verification : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_5():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 5: UNKNOWN ENTITY HANDLING (CUS-99999)")
    print("=" * 80)
    resp = api_post("/api/copilot/investigate", {
        "question": "Investigate customer CUS-99999 and explain risk score.",
        "use_mock": True
    })
    print(f"Unknown Entity Detected : {resp.get('unknown_entity_detected')}")
    print(f"Risk Score              : {resp.get('risk_assessment', {}).get('risk_score')}")
    print(f"Summary                 : {resp.get('summary')}")
    ok = (resp.get('unknown_entity_detected') is True and
          resp.get('risk_assessment', {}).get('risk_score') == 0 and
          "not found" in resp.get('summary', '').lower())
    print(f"Scenario 5 Verification : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_6():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 6: AMBIGUOUS ENTITY RESOLUTION (Jean Mutombo)")
    print("=" * 80)
    resp = api_post("/api/copilot/investigate", {
        "question": "Investigate Jean Mutombo for recent transfers.",
        "use_mock": True
    })
    print(f"Ambiguity Detected       : {resp.get('ambiguity_detected')}")
    print(f"Summary                  : {resp.get('summary')}")
    gaps = resp.get("evidence_gaps", [])
    print(f"Evidence Gaps            : {[g.get('gap_type') for g in gaps]}")
    ok = (resp.get('ambiguity_detected') is True and
          any(g.get('gap_type') == "AMBIGUOUS_ENTITY" for g in gaps))
    print(f"Scenario 6 Verification  : {'PASS' if ok else 'FAIL'}")
    return ok


def verify_scenario_7():
    print("\n" + "=" * 80)
    print("DEMO SCENARIO 7: CLEAN CUSTOMER / INSUFFICIENT EVIDENCE (CUS-00003)")
    print("=" * 80)
    resp = api_post("/api/copilot/investigate", {
        "question": "Is there sufficient evidence to establish suspicious activity for this customer?",
        "entity_type": "customer",
        "entity_id": "CUS-00003",
        "use_mock": True
    })
    print(f"Insufficient Evidence Detected: {resp.get('insufficient_evidence_detected')}")
    print(f"Risk Score                    : {resp.get('risk_assessment', {}).get('risk_score')}/100")
    print(f"Summary                       : {resp.get('summary')}")
    print(f"Escalation Recommendation     : {resp.get('escalation_recommendation')}")
    ok = (resp.get('insufficient_evidence_detected') is True and
          resp.get('risk_assessment', {}).get('risk_score') == 0 and
          "insufficient evidence" in resp.get('summary', '').lower())
    print(f"Scenario 7 Verification       : {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    results = [
        verify_scenario_1(),
        verify_scenario_2(),
        verify_scenario_3(),
        verify_scenario_4(),
        verify_scenario_5(),
        verify_scenario_6(),
        verify_scenario_7(),
    ]
    print("\n" + "=" * 80)
    print(f"DEMO SCENARIOS VERIFICATION SUMMARY: {sum(results)}/7 SCENARIOS PASSED")
    print("=" * 80)
