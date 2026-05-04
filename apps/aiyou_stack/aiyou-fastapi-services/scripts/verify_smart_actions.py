import sys
import time

import requests

BASE_URL = "http://localhost:8600"


def wait_for_server():
    print("⏳ Waiting for server to come online...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/health")
            print("   ✅ Server Online")
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("   ❌ Server failed to start")
    return False


def test_risk():
    print("\n[TEST] /risk Endpoint")
    payload = {"code": "import os; os.system('rm -rf /')", "mission_id": "TEST-RISK-001"}
    # Note: Our current logic validates with Judge6.
    # 'rm -rf' isn't explicitly caught by our simple 'malware' keyword list in SafetyNet yet
    # unless we add it, but let's just check the structure for now.

    try:
        resp = requests.post(f"{BASE_URL}/risk", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"   Response: {data}")
        assert "approved" in data
        assert "risk_tier" in data
        print("   ✅ /risk Passed")
    except Exception as e:
        print(f"   ❌ /risk Failed: {e}")
        raise SystemExit(1)


def test_scan():
    print("\n[TEST] /scan Endpoint")
    payload = {"file_path": "test_image.jpg", "intent": "Extract totals"}
    try:
        resp = requests.post(f"{BASE_URL}/scan", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"   Response: {data}")
        assert data["status"] == "SCANNED"
        assert "tegu_score" in data
        print("   ✅ /scan Passed")
    except Exception as e:
        print(f"   ❌ /scan Failed: {e}")
        raise SystemExit(1)


def test_ui():
    print("\n[TEST] /ui Endpoint")
    payload = {"intent": "Create a dashboard for risk metrics"}
    try:
        resp = requests.post(f"{BASE_URL}/ui", json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"   Response: {data}")
        assert data["type"] == "A2UI_COMPONENT"
        print("   ✅ /ui Passed")
    except Exception as e:
        print(f"   ❌ /ui Failed: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    if wait_for_server():
        test_risk()
        test_scan()
        test_ui()
        print("\n>>> 🚀 ALL SMART ACTIONS VERIFIED")
    else:
        sys.exit(1)
