#!/usr/bin/env python3
"""
Automated Endpoint & Health Tester for JTV Pro Engine
Developer: Kobir Shah
"""

import sys
import json
import urllib.request

BASE_URL = "http://127.0.0.1:8080"
ENDPOINTS = [
    ("/cookies", "Cookies Master API"),
    ("/cookie/1104", "Star Movies HD Probe"),
    ("/cookie/1341", "Nick Bangla Probe"),
    ("/cookie/362", "Star Sports 1 Hindi Probe"),
    ("/extend", "10-Days VIP Extend Status"),
    ("/channels", "Channels Database"),
    ("/status", "System Status")
]

def main():
    if "--dry-run" in sys.argv:
        print("✅ Dry-run syntax test passed successfully!")
        sys.exit(0)

    print("🔍 Testing JTV Pro API Endpoints...")
    all_passed = True

    for path, desc in ENDPOINTS:
        url = f"{BASE_URL}{path}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                dev = data.get("developer", "N/A")
                print(f"  ✓ [{resp.status}] {desc} ({path}) -> Dev: {dev}")
        except Exception as e:
            print(f"  ✗ Failed {desc} ({path}) -> {e}")
            all_passed = False

    if all_passed:
        print("\n🎉 All JTV Pro endpoints are 100% HEALTHY & FUNCTIONAL!")
    else:
        print("\n⚠️ Some endpoints failed. Make sure app.py is running on port 8080.")

if __name__ == "__main__":
    main()
