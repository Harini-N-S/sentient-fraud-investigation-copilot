"""
Manual API Verification Script
-----------------------------------------------------------------------------
Executes actual HTTP requests against all 12 key endpoints using TestClient
and prints formatted responses demonstrating live database retrieval.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

endpoints = [
    ("1. Health Endpoint", "GET", "/api/health"),
    ("2. Overview Endpoint", "GET", "/api/overview"),
    ("3. Alert Listing", "GET", "/api/alerts?page=1&page_size=2"),
    ("4. Alert Detail", "GET", "/api/alerts/ALT-00001"),
    ("5. Transaction Detail", "GET", "/api/transactions/TXN-00801"),
    ("6. Customer Detail", "GET", "/api/customers/CUS-00014"),
    ("7. Device Detail", "GET", "/api/devices/DEV-00127"),
    ("8. Beneficiary Detail", "GET", "/api/beneficiaries/BEN-00088"),
    ("9. Entity Relationships", "GET", "/api/entities/customer/CUS-00014/relationships"),
    ("10. Deterministic Evaluation", "POST", "/api/evaluate/transaction/TXN-00801"),
    ("11. Forensic Evidence Packet", "GET", "/api/evidence/TXN-00801"),
    ("12. Unified Search", "GET", "/api/search?q=CUS-00014")
]

for label, method, path in endpoints:
    if method == "POST":
        resp = client.post(path)
    else:
        resp = client.get(path)

    print(f"==================================================")
    print(f"{label} [{method} {path}] -> HTTP {resp.status_code}")
    print(f"==================================================")
    data = resp.json()
    if isinstance(data, dict):
        for k, v in list(data.items())[:6]:
            if isinstance(v, (dict, list)):
                preview = f"{type(v).__name__} (len={len(v)})"
            else:
                preview = str(v)
            print(f"  * {k}: {preview}")
    print()
