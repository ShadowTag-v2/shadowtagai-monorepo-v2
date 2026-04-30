import subprocess
import sys
import time


def wait_for_workstation():
    print("⏳ Waiting for Workstation 'antigravity-cockpit' to be RUNNING...")
    for _ in range(20):  # 20 attempts * 5 seconds = 100 seconds
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "workstations",
                    "list",
                    "--cluster=antigravity-cluster-v2",
                    "--config=antigravity-cockpit-config",
                    "--region=us-central1",
                    "--filter=name:antigravity-cockpit",
                    "--format=json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            import json

            data = json.loads(result.stdout)
            if data:
                state = data[0].get("state")
                print(f"   Status: {state}")
                if state == "STATE_RUNNING":  # gcloud usually returns STATE_RUNNING or RUNNING
                    return True
                if state == "RUNNING":
                    return True
        except Exception as e:
            print(f"   Error checking status: {e}")
        time.sleep(5)
    return False


if __name__ == "__main__":
    if wait_for_workstation():
        print("✅ Workstation is Online.")
    else:
        print("❌ Wait timed out. Check console.")
        sys.exit(1)
