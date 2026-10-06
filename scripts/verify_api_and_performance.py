"""
Rawbank Sentient Fraud Intelligence Platform
Phase 8 API Contract, Error-Path & Performance Verification Script
-----------------------------------------------------------------------------
Verifies Sections 15, 16, and 20:
- API contract adherence for all required endpoints
- Sanitized error handling and edge cases
- Latency and performance benchmarking
"""

import time
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple

BASE_URL = "http://127.0.0.1:8000"


def http_request(
    endpoint: str,
    method: str = "GET",
    payload: Dict[str, Any] = None,
    expected_status: int = 200
) -> Tuple[int, Dict[str, Any], float]:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    headers = {"Content-Type": "application/json"} if payload else {}

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req) as resp:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body, elapsed_ms
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"error": str(e)}
        return e.code, body, elapsed_ms
    except Exception as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return 500, {"error": str(e)}, elapsed_ms


def run_api_contract_audit():
    print("=" * 80)
    print("SECTION 15: API CONTRACT AUDIT")
    print("=" * 80)

    contracts = [
        ("GET", "/api/health", None, 200, ["status", "version", "environment"]),
        ("GET", "/api/overview", None, 200, ["total_customers", "total_alerts", "critical_alerts", "alerts_by_scenario", "top_mule_beneficiaries"]),
        ("GET", "/api/alerts?page=1&page_size=5", None, 200, ["items", "pagination"]),
        ("GET", "/api/alerts/ALT-00001", None, 200, ["alert", "customer", "account", "transaction", "signals"]),
        ("GET", "/api/alerts/ALT-00001/evidence", None, 200, ["target_entity", "exact_data", "calculated_information"]),
        ("GET", "/api/transactions?page=1&page_size=5", None, 200, ["items", "pagination"]),
        ("GET", "/api/transactions/TXN-00801", None, 200, ["transaction", "customer", "account", "beneficiary", "device"]),
        ("GET", "/api/transactions/TXN-00801/evidence", None, 200, ["transaction_id", "customer_id", "tier_1_exact_data"]),
        ("GET", "/api/customers?page=1&page_size=5", None, 200, ["items", "pagination"]),
        ("GET", "/api/customers/CUS-00014", None, 200, ["customer", "accounts", "activity_summary", "risk"]),
        ("GET", "/api/search?q=Christelle", None, 200, ["query", "total_results", "results"]),
        ("GET", "/api/entities/customer/CUS-00014/relationships", None, 200, ["root_entity", "total_relationships", "relationships"]),
        ("POST", "/api/retrieval/query", {"query": "Why was alert ALT-00001 triggered?"}, 200, ["results", "evidence_packet"]),
        ("POST", "/api/copilot/investigate", {"question": "Why was alert ALT-00001 triggered?", "use_mock": True}, 200, ["summary", "risk_assessment", "supporting_evidence"]),
    ]

    all_passed = True
    for method, endpoint, payload, exp_status, required_fields in contracts:
        status, body, elapsed = http_request(endpoint, method, payload, exp_status)
        passed = status == exp_status and all(k in body for k in required_fields)
        if not passed:
            all_passed = False
        status_str = "PASS" if passed else "FAIL"
        print(f"[{status_str}] {method:<4} {endpoint:<45} -> Status: {status} ({elapsed:.1f}ms)")
        if not passed:
            missing = [k for k in required_fields if k not in body]
            print(f"       Missing fields: {missing}, Response keys: {list(body.keys())}")

    return all_passed


def run_error_path_audit():
    print("\n" + "=" * 80)
    print("SECTION 16: ERROR-PATH & SANITIZATION AUDIT")
    print("=" * 80)

    error_cases = [
        ("Invalid alert ID", "GET", "/api/alerts/ALT-99999", None, 404),
        ("Invalid transaction ID", "GET", "/api/transactions/TXN-99999", None, 404),
        ("Invalid customer ID", "GET", "/api/customers/CUS-99999", None, 404),
        ("Invalid entity type in relationships", "GET", "/api/entities/invalid_type/ID-01/relationships", None, 400),
        ("Invalid pagination page 0", "GET", "/api/alerts?page=0", None, 422),
        ("Excessive page size 500", "GET", "/api/alerts?page_size=500", None, 422),
        ("Invalid severity filter", "GET", "/api/alerts?severity=INVALID_SEVERITY", None, 400),
        ("Unknown entity investigation", "POST", "/api/copilot/investigate", {"question": "Investigate CUS-99999", "use_mock": True}, 200),
        ("Ambiguous entity investigation", "POST", "/api/copilot/investigate", {"question": "Investigate Jean Mutombo", "use_mock": True}, 200),
        ("Empty question copilot", "POST", "/api/copilot/investigate", {"question": "   ", "use_mock": True}, 200),
    ]

    all_passed = True
    for title, method, endpoint, payload, exp_status in error_cases:
        status, body, elapsed = http_request(endpoint, method, payload, exp_status)
        passed = status == exp_status

        # Verify response does NOT leak stack traces, filesystem paths, or env vars
        body_text = json.dumps(body)
        leaks = []
        for leak_word in ["traceback", "file \"c:", "c:\\users", "environ[", "exception:"]:
            if leak_word in body_text.lower():
                leaks.append(leak_word)

        if leaks:
            passed = False
            print(f"[FAIL-LEAK] {title}: Leaked internal debug info: {leaks}")
        elif passed:
            print(f"[PASS] {title:<35} -> HTTP {status} (Sanitized, {elapsed:.1f}ms)")
        else:
            print(f"[FAIL] {title:<35} -> Expected {exp_status}, Got {status}")
            all_passed = False

    return all_passed


def run_performance_benchmarks():
    print("\n" + "=" * 80)
    print("SECTION 20: PERFORMANCE BENCHMARK & LATENCY MEASUREMENTS")
    print("=" * 80)

    benchmarks = [
        ("Overview Endpoint", "GET", "/api/overview", None),
        ("Alerts List (page_size=20)", "GET", "/api/alerts?page=1&page_size=20", None),
        ("Alert ALT-00001 Detail", "GET", "/api/alerts/ALT-00001", None),
        ("Customer CUS-00014 Detail", "GET", "/api/customers/CUS-00014", None),
        ("Transaction TXN-00801 Detail", "GET", "/api/transactions/TXN-00801", None),
        ("Relationship Network (CUS-00014)", "GET", "/api/entities/customer/CUS-00014/relationships", None),
        ("Hybrid Retrieval Query", "POST", "/api/retrieval/query", {"query": "Why was alert ALT-00001 triggered?"}),
        ("Copilot Investigation (Mock)", "POST", "/api/copilot/investigate", {"question": "Why was alert ALT-00001 triggered?", "use_mock": True}),
    ]

    for title, method, endpoint, payload in benchmarks:
        latencies = []
        for _ in range(5):
            _, _, elapsed = http_request(endpoint, method, payload)
            latencies.append(elapsed)
        avg_ms = sum(latencies) / len(latencies)
        min_ms = min(latencies)
        max_ms = max(latencies)
        status_eval = "EXCELLENT" if avg_ms < 50.0 else ("GOOD" if avg_ms < 200.0 else "FAIR")
        print(f"{title:<35} : Avg: {avg_ms:6.1f}ms | Min: {min_ms:5.1f}ms | Max: {max_ms:5.1f}ms [{status_eval}]")


if __name__ == "__main__":
    c_ok = run_api_contract_audit()
    e_ok = run_error_path_audit()
    run_performance_benchmarks()
    print("=" * 80)
    print(f"Overall Contract & Error Audit: {'PASS' if (c_ok and e_ok) else 'FAIL'}")
    print("=" * 80)
