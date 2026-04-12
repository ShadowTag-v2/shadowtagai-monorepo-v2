import time

import psutil

# Configuration
MAX_CPU_PERCENT = 90.0
MAX_MEMORY_PERCENT = 85.0
SUSTAINED_THRESHOLD_SEC = 300  # 5 Minutes


def log(msg):
    print(f"[QUOTA GUARD] {msg}")


def monitor():
    log("🛡️ Quota Guard Active. Watching for runaway Agents...")
    high_usage_start = None

    while True:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent

        if cpu > MAX_CPU_PERCENT or mem > MAX_MEMORY_PERCENT:
            if high_usage_start is None:
                high_usage_start = time.time()

            duration = time.time() - high_usage_start
            if duration > SUSTAINED_THRESHOLD_SEC:
                log(f"🚨 CRITICAL: Agent exceeded limits for {duration}s. TERMINATING.")
                # Kill the heaviest process (likely the Agent or a runaway build)
                # In production, this would be more surgical.
                # WARNING: In this environment, pkill might not work or might key important things.
                # Proceed with caution.
                # os.system("pkill -f node") # Kill VS Code Agent processes
                # os.system("pkill -f python")
                high_usage_start = None
        else:
            high_usage_start = None

        time.sleep(5)


if __name__ == "__main__":
    monitor()
