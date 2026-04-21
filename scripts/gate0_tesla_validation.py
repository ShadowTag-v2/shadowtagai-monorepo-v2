#!/usr/bin/env python3
"""Gate 0: Tesla Fleet API viability test (1Hz for 60s).
---------------------------------------------------
PREREQS (one-time):
  1) Register app at https://developer.tesla.com
     - Redirect URI: http://localhost:8080/callback
     - Scopes: vehicle_device_data vehicle_cmds
     - Note Client ID/Secret and complete OAuth to obtain ACCESS_TOKEN
  2) Retrieve VEHICLE_ID via GET /api/1/vehicles

SECURITY:
  - Do NOT hardcode tokens in the notebook.
  - Provide ACCESS_TOKEN and VEHICLE_ID via environment variables or temporary input.

HOW TO RUN:
  - Option A: Set environment variables before running:
      export ACCESS_TOKEN=YOUR_OAUTH_TOKEN
      export VEHICLE_ID=YOUR_VEHICLE_ID
  - Option B: Manually set the variables below (for quick local testing only).
"""

import json
import os
import statistics
import time
from datetime import datetime

import requests

# ---- Configuration ----
TESLA_API_BASE = os.getenv("TESLA_API_BASE", "https://fleet-api.prd.na.vn.cloud.tesla.com")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "YOUR_OAUTH_TOKEN")
VEHICLE_ID = os.getenv("VEHICLE_ID", "YOUR_VEHICLE_ID")
TIMEOUT_S = float(os.getenv("TESLA_TIMEOUT_S", "5"))
CALLS = int(os.getenv("TESLA_CALLS", "60"))  # number of loop iterations
SLEEP_S = float(os.getenv("TESLA_SLEEP_S", "1"))  # target 1 Hz

# assert ACCESS_TOKEN and ACCESS_TOKEN != "YOUR_OAUTH_TOKEN", "ACCESS_TOKEN not set"
# assert VEHICLE_ID and VEHICLE_ID != "YOUR_VEHICLE_ID", "VEHICLE_ID not set"

if ACCESS_TOKEN == "YOUR_OAUTH_TOKEN" or VEHICLE_ID == "YOUR_VEHICLE_ID":
    pass
    # We might want to exit or just let it fail if the user wants to see the structure

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}


# CELL 2: Execute 60-Call Stress Test
endpoint = f"{TESLA_API_BASE}/api/1/vehicles/{VEHICLE_ID}/vehicle_data"

results = {
    "successful_calls": 0,
    "failed_calls": 0,
    "latencies_ms": [],
    "rate_limit_errors": 0,
    "timestamps": [],
    "http_statuses": [],
    "speeds_mph": [],
}

for _i in range(CALLS):
    start_time = time.time()
    try:
        resp = requests.get(endpoint, headers=headers, timeout=TIMEOUT_S)
        latency_ms = (time.time() - start_time) * 1000.0
        results["latencies_ms"].append(latency_ms)
        results["timestamps"].append(datetime.now().isoformat())
        results["http_statuses"].append(resp.status_code)

        if resp.status_code == 200:
            results["successful_calls"] += 1
            data = resp.json()
            speed = data.get("response", {}).get("drive_state", {}).get("speed", "N/A")
            results["speeds_mph"].append(speed if isinstance(speed, (int, float)) else None)
        elif resp.status_code == 429:
            results["rate_limit_errors"] += 1
            results["failed_calls"] += 1
            results["speeds_mph"].append(None)
        else:
            results["failed_calls"] += 1
            results["speeds_mph"].append(None)
    except Exception:
        results["failed_calls"] += 1
        results["latencies_ms"].append(None)
        results["timestamps"].append(datetime.now().isoformat())
        results["http_statuses"].append("EXC")
        results["speeds_mph"].append(None)

    # maintain approximate 1 Hz pacing
    elapsed = time.time() - start_time
    delay = max(0.0, SLEEP_S - elapsed)
    time.sleep(delay)

# Persist raw results for audit
out_json = {
    "endpoint": endpoint,
    "calls": CALLS,
    "interval_s": SLEEP_S,
    "timestamps": results["timestamps"],
    "http_statuses": results["http_statuses"],
    "latencies_ms": results["latencies_ms"],
    "speeds_mph": results["speeds_mph"],
}
# Changed path to local for script execution
output_file = "gate0_results.json"
with open(output_file, "w") as f:
    json.dump(out_json, f, indent=2)

# CELL 3: Analysis & Decision
total = CALLS
ok = results["successful_calls"]
fail = results["failed_calls"]
rl = results["rate_limit_errors"]
lat_ok = [x for x in results["latencies_ms"] if isinstance(x, (int, float))]

success_rate = (ok / total) * 100 if total else 0.0
avg_latency = statistics.mean(lat_ok) if lat_ok else 0.0
p95_latency = 0.0
if len(lat_ok) >= 20:
    # approximate p95 via quantiles
    p95_latency = statistics.quantiles(lat_ok, n=20)[18]



if (success_rate >= 95 and avg_latency <= 500) or (success_rate >= 90 and rl > 10):
    pass
else:
    pass


# Optional: save a compact summary CSV for quick sharing
import csv

csv_path = "gate0_summary.csv"
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric", "value"])
    w.writerow(["success_rate_pct", f"{success_rate:.2f}"])
    w.writerow(["successful_calls", ok])
    w.writerow(["failed_calls", fail])
    w.writerow(["rate_limit_errors", rl])
    w.writerow(["avg_latency_ms", f"{avg_latency:.0f}"])
    w.writerow(["p95_latency_ms", f"{p95_latency:.0f}"])
    w.writerow(["calls", total])
    w.writerow(["interval_s", SLEEP_S])
    w.writerow(["endpoint", endpoint])
