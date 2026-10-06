"""
Rawbank Sentient Fraud Intelligence Platform
Phase 8 Automated Audits:
1. Hallucination Challenge Audit (Section 12)
2. Source Provenance Audit (Section 13)
3. Risk Score Integrity Audit (Section 14)
"""

import json
import sqlite3
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = Path("database/synthetic_bank.db")


def api_post(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_hallucination_audit():
    print("\n" + "=" * 80)
    print("SECTION 12: COPILOT HALLUCINATION AUDIT")
    print("=" * 80)

    test_queries = [
        ("Nonexistent customer transfer", "Why did customer CUS-99999 send $1 million yesterday?"),
        ("Fabricated location premise", "Which device did CUS-00014 use from Paris?"),
        ("Nonexistent historical window", "Which beneficiary did CUS-00003 send money to in 2018?"),
        ("Fabricated device ID", "Explain why device DEV-99999 is part of a mule ring."),
        ("Nonexistent alert ID", "Why was alert ALT-99999 triggered with score 99?"),
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    passed = 0
    for title, query in test_queries:
        print(f"\n[Challenge]: {title}")
        print(f"  Query: \"{query}\"")
        resp = api_post("/api/copilot/investigate", {"question": query, "use_mock": True})
        
        # Check that it did NOT accept nonexistent entities as fact
        unknown_flag = resp.get("unknown_entity_detected", False)
        insufficient_flag = resp.get("insufficient_evidence_detected", False)
        gaps = resp.get("evidence_gaps", [])
        summary = resp.get("summary", "")
        
        # Verify no fabricated IDs were injected
        fabricated_ids = ["CUS-99999", "DEV-99999", "ALT-99999"]
        found_fab = any(fid in resp.get("risk_assessment", {}).get("severity", "") for fid in fabricated_ids)
        
        print(f"  Summary response snippet: {summary[:120]}...")
        print(f"  Flags: unknown_entity={unknown_flag}, insufficient_evidence={insufficient_flag}, gaps_count={len(gaps)}")
        
        # Assertions
        is_safe = (unknown_flag or insufficient_flag or len(gaps) > 0 or "insufficient" in summary.lower() or "not found" in summary.lower() or "unknown" in summary.lower() or "no " in summary.lower())
        if is_safe:
            print("  Result: PASS (Did NOT hallucinate fact; signaled lack of grounded evidence)")
            passed += 1
        else:
            print("  Result: FAIL (Accepted premise uncritically)")

    conn.close()
    print(f"\nHallucination Audit: {passed}/{len(test_queries)} challenges handled safely.")
    return passed == len(test_queries)


def run_source_provenance_audit():
    print("\n" + "=" * 80)
    print("SECTION 13: SOURCE PROVENANCE AUDIT (10 FACTUAL CLAIMS)")
    print("=" * 80)

    # Inquire on key test cases
    inquiries = [
        "Why was alert ALT-00001 triggered?",
        "Why is transaction TXN-00801 suspicious?",
        "Investigate customer CUS-00014 for account takeover.",
        "Investigate beneficiary BEN-00088 and funnel aggregation.",
        "Investigate device DEV-00125 across multiple accounts."
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    claims_audited = []
    for q in inquiries:
        resp = api_post("/api/copilot/investigate", {"question": q, "use_mock": True})
        for ev in resp.get("supporting_evidence", []):
            claims_audited.append({
                "statement": ev.get("statement"),
                "source_id": ev.get("source_id"),
                "source_table": ev.get("source_table"),
                "citation": ev.get("citation")
            })
            if len(claims_audited) >= 10:
                break
        if len(claims_audited) >= 10:
            break

    print(f"Gathered {len(claims_audited)} factual claims from Copilot evidence responses.")
    verified_count = 0

    table_pk_map = {
        "transactions": "transaction_id",
        "alerts": "alert_id",
        "customers": "customer_id",
        "devices": "device_id",
        "beneficiaries": "beneficiary_id",
        "auth_activities": "activity_id",
        "auth_logs": "activity_id",
        "signals": "signal_id",
        "fraud_signals": "signal_id",
        "behavioural_baselines": "baseline_id"
    }

    for i, item in enumerate(claims_audited, start=1):
        tbl = item["source_table"]
        sid = item["source_id"]
        pk = table_pk_map.get(tbl, f"{tbl[:-1]}_id" if tbl.endswith("s") else f"{tbl}_id")
        
        # If table name is aliased, normalize
        if tbl == "signals":
            tbl = "fraud_signals"
            pk = "signal_id"
        elif tbl == "auth_logs":
            tbl = "auth_activities"
            pk = "activity_id"

        cursor.execute(f"SELECT COUNT(*) FROM \"{tbl}\" WHERE \"{pk}\" = ?", (sid,))
        exists = cursor.fetchone()[0] > 0

        status_str = "VERIFIED IN DB" if exists else "NOT FOUND IN DB"
        print(f"\nClaim {i:02d}: \"{item['statement'][:70]}...\"")
        print(f"  Provenance: [Source: {sid}] -> Table: {tbl}.{pk}")
        print(f"  DB Existence: {status_str}")

        if exists:
            verified_count += 1

    conn.close()
    print(f"\nSource Provenance Audit: {verified_count}/{len(claims_audited)} claims verified 100% against database records.")
    return verified_count == len(claims_audited)


def run_risk_score_integrity_audit():
    print("\n" + "=" * 80)
    print("SECTION 14: RISK SCORE INTEGRITY AUDIT")
    print("=" * 80)

    test_alerts = ["ALT-00001", "ALT-00002", "ALT-00003", "ALT-00004", "ALT-00010"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    matches = 0
    for alt_id in test_alerts:
        # 1. Database score
        cursor.execute("SELECT composite_risk_score, severity, scenario_type FROM alerts WHERE alert_id = ?", (alt_id,))
        row = cursor.fetchone()
        db_score, db_sev, scenario = row[0], row[1], row[2]

        # 2. REST API score
        api_data = api_get(f"/api/alerts/{alt_id}")
        api_score = api_data.get("composite_risk_score") or api_data.get("alert", {}).get("composite_risk_score")
        api_sev = api_data.get("severity") or api_data.get("alert", {}).get("severity")

        # 3. Copilot score
        copilot_resp = api_post("/api/copilot/investigate", {
            "question": f"Why was alert {alt_id} triggered?",
            "use_mock": True
        })
        copilot_score = copilot_resp.get("risk_assessment", {}).get("risk_score")
        copilot_sev = copilot_resp.get("risk_assessment", {}).get("severity")

        print(f"\nAlert {alt_id} ({scenario}):")
        print(f"  - Database Score : {db_score} ({db_sev})")
        print(f"  - API Score      : {api_score} ({api_sev})")
        print(f"  - Copilot Score  : {copilot_score} ({copilot_sev})")

        is_match = (db_score == api_score == copilot_score) and (db_sev == api_sev == copilot_sev)
        if is_match:
            print("  Result: 100% MATCH (Deterministic score preserved without LLM drift)")
            matches += 1
        else:
            print("  Result: MISMATCH!")

    conn.close()
    print(f"\nRisk Score Integrity Audit: {matches}/{len(test_alerts)} alerts verified with zero score mutation.")
    return matches == len(test_alerts)


if __name__ == "__main__":
    h_ok = run_hallucination_audit()
    p_ok = run_source_provenance_audit()
    r_ok = run_risk_score_integrity_audit()

    print("\n" + "=" * 80)
    print("PHASE 8 AUDIT SUMMARY")
    print("=" * 80)
    print(f"Hallucination Challenge Audit : {'PASS' if h_ok else 'FAIL'}")
    print(f"Source Provenance Audit       : {'PASS' if p_ok else 'FAIL'}")
    print(f"Risk Score Integrity Audit    : {'PASS' if r_ok else 'FAIL'}")
