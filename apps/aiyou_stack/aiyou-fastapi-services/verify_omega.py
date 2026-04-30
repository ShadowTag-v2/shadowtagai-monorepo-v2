import os
import sys
import time

import requests

SERVICES = [
    {
        "name": "SeatJudge MCP",
        "url": os.getenv("SEATJUDGE_MCP_URL", "http://localhost:8081/health"),
    },
    {"name": "Jetski Sidecar", "url": os.getenv("JETSKI_URL", "http://localhost:8082/health")},
    {"name": "Judge 6 Omega", "url": os.getenv("JUDGE6_URL", "http://localhost:8083/health")},
]


def check_services():
    print("🔍 Verifying ShadowTag Omega Stack...")
    all_green = True

    for service in SERVICES:
        print(f"   Testing {service['name']}...", end=" ")
        try:
            # MCP might not have /health if it's stdio based, but we mapped 8081.
            # If it's a raw TCP socket, requests might hang or fail.
            # But SeatJudge.Inventory.Mcp is a console app unless it uses FastMCP over HTTP.
            # Let's assume HTTP for now based on Dockerfile exposing 8080.

            response = requests.get(service["url"], timeout=2)
            if response.status_code == 200:
                print("✅ OK")
            else:
                print(f"❌ FAIL ({response.status_code})")
                all_green = False
        except requests.ConnectionError:
            print("❌ DOWN (Connection Refused)")
            all_green = False
        except Exception as e:
            print(f"❌ ERROR ({e})")
            all_green = False

    if all_green:
        print("\n🚀 All Systems Nominal. Engaging Omega Protocol.")
        sys.exit(0)
    else:
        print("\n⚠️  System Degraded.")
        sys.exit(1)


if __name__ == "__main__":
    # Wait a bit for startup
    startup_delay = int(os.getenv("STARTUP_DELAY_SECONDS", "5"))
    time.sleep(startup_delay)
    check_services()
