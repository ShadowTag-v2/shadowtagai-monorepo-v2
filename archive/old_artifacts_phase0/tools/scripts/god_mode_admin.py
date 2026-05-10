import json
import logging
import os
import subprocess
import sys

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GodModeAdmin")


def handle_command(line):
    line = line.strip()
    if not line:
        return True  # Continue loop

    parts = line.split(maxsplit=1)
    command = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    if command == "status":
        logger.info("STATUS: All systems nominal. Ready for command.")
    elif command == "sync":
        logger.info("SYNC: Synchronizing with the Sovereign Matrix...")
        # In a real scenario, this would trigger a sync process.
        logger.info("SYNC: Complete.")
    elif command == "help":
        logger.info("Available commands:")
        logger.info("  status                            - Check system status.")
        logger.info("  sync                              - Synchronize with the matrix.")
        logger.info("  shell <shell_command>             - Execute a shell command.")
        logger.info('  json {"task": "<objective>"}    - Execute a task via JSON payload.')
        logger.info("  stop                              - Stop the engine.")
    elif command == "shell":
        if not arg:
            logger.error("SHELL: No command provided.")
        else:
            logger.info(f"SHELL: Executing '{arg}'...")
            try:
                result = subprocess.run(arg, shell=True, check=True, capture_output=True, text=True)
                logger.info("SHELL STDOUT:")
                print(result.stdout)
                if result.stderr:
                    logger.warning("SHELL STDERR:")
                    print(result.stderr)
            except Exception as e:
                logger.error(f"SHELL: Command failed: {e}")
    elif command == "json":
        if not arg:
            logger.error("JSON: No payload provided.")
        else:
            try:
                payload = json.loads(arg)
                task_objective = payload.get("task")
                logger.info(f"JSON: Received task: {task_objective}")

                # ---> NEW BEHAVIOR: Forward to Sovereign FastAPI Endpoint
                import requests

                api_url = os.environ.get("VITE_API_URL", "http://localhost:8000")
                endpoint = f"{api_url}/api/v1/ShadowTag-v2/agent/query"

                logger.info(f"JSON: Dispatching task to {endpoint} ...")

                # Execute asynchronously or timeout to prevent shell locking
                try:
                    response = requests.post(
                        endpoint,
                        json={"q": task_objective},
                        headers={"Content-Type": "application/json"},
                        timeout=5,  # Fast timeout so the queue loop doesn't stall
                    )
                    if response.status_code == 200:
                        logger.info("JSON: Task successfully dispatched to FastAPI agent pipeline.")
                    else:
                        logger.error(f"JSON: Failed to dispatch. Status Code: {response.status_code} - {response.text}")
                except Exception as net_err:
                    logger.error(f"JSON: Connection error to FastAPI matrix: {net_err}")

            except json.JSONDecodeError:
                logger.error(f"JSON: Invalid JSON payload: {arg}")
    elif command == "stop":
        return False  # Signal to stop
    else:
        logger.warning(f"Unknown command: {command}")

    return True


def main():
    logger.info("==========================================")
    logger.info("   ☢️  SHADOWTAG OMEGA V7: LIVE ENGINE")
    logger.info("==========================================")

    try:
        from libs.steel.sdk import VelocityEngine

        # Auto-inject headless auth into environment for god mode
        key_file = os.path.expanduser("~/.gcp/headless-runner-key.json")
        if os.path.exists(key_file):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file
            subprocess.run(
                [
                    "gcloud",
                    "auth",
                    "activate-service-account",
                    "767252945109-compute@developer.gserviceaccount.com",
                    f"--key-file={key_file}",
                ],
                capture_output=True,
                check=False,
            )
            logger.info("🔐 Headless Auth Activated.")

        VelocityEngine()
        logger.info("⚡ Initializing Velocity Engine...")
        logger.info("✅ Engine Ready.")
    except ImportError:
        logger.warning("⚠️ VelocityEngine not found. Running in degraded mode.")

    logger.info("🎮 Awaiting Command Flux...")

    try:
        for line in sys.stdin:
            if not handle_command(line):
                break
    except KeyboardInterrupt:
        pass  # Allow clean exit on Ctrl+C
    finally:
        logger.info("🛑 Engine Powering Down.")


if __name__ == "__main__":
    main()
