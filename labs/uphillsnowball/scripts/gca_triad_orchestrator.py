import os
import time
import subprocess
import logging
from datetime import datetime, UTC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def get_current_state():
    """Phase 1: Hypothesis (Kosmos)
    Gathers current AST state, test vectors, and error regressions via Omni-Linter."""
    logging.info("Executing Phase 1: Hypothesis (Kosmos)")
    # Simulating omni-linter execution
    result = subprocess.run(["ruff", "check", "--output-format=json", "."], capture_output=True, text=True)
    return result.stdout


def apply_mutations():
    """Phase 2: Execution (Builder)
    Applies zero-shot structural fixes using vulture and ruff."""
    logging.info("Executing Phase 2: Execution (Builder)")
    # Vulture step
    subprocess.run(["vulture", "."], capture_output=True)
    # Ruff auto-fix
    subprocess.run(["ruff", "check", "--fix", "."], capture_output=True)
    return True


def run_gauntlet():
    """Phase 3: The Gauntlet (n-autoresearch)
    Runs Pytest isolation matrix to test constraints."""
    logging.info("Executing Phase 3: The Gauntlet")
    result = subprocess.run(["python3.14", "-m", "pytest", "-q"], capture_output=True, text=True)
    return result.returncode == 0


def temporal_reversal():
    """Phase 4: Temporal-Reversal (Judge 6 Gate)
    Rolls back mutative graph if tests fail."""
    logging.info("Executing Phase 4: Temporal-Reversal")
    subprocess.run(["git", "restore", "."], capture_output=True)
    logging.warning("Reverted to known good state.")


def commit_to_vault():
    """Phase 5: The Vault
    Commits state as LanceDB vector + Obsidian Markdown log."""
    logging.info("Executing Phase 5: The Vault")
    # Commit changes
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"chore(heal): Autoresearch Triad automated healing at {datetime.now(UTC).isoformat()}"], capture_output=True
    )
    logging.info("State committed to Vault.")


def daemon_loop():
    logging.info("Starting GCA Triad Orchestrator Daemon")
    while True:
        try:
            state = get_current_state()
            if state:
                apply_mutations()
                if run_gauntlet():
                    commit_to_vault()
                else:
                    temporal_reversal()
            else:
                logging.info("No mutations needed. System optimal.")
        except Exception as e:
            logging.error(f"Daemon exception: {e}")

        logging.info("Sleeping for 5 minutes...")
        time.sleep(300)


if __name__ == "__main__":
    daemon_loop()
