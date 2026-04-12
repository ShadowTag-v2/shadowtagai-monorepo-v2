import base64
import json
import logging
import os

import functions_framework
import yaml
from google.cloud import pubsub_v1

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JudgeV6")

PROJECT_ID = os.getenv("GCP_PROJECT", "shadowtag-omega-v2")
LEDGER_TOPIC = f"projects/{PROJECT_ID}/topics/compliance-ledger"
MONKEY_TOPIC = f"projects/{PROJECT_ID}/topics/monkey-summons"

publisher = pubsub_v1.PublisherClient()


def load_constitution():
    # In production, load from GCS or Secret Manager.
    # For now, we assume the file is deployed with the function.
    try:
        with open("policy.yaml") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Constitution (policy.yaml) not found!")
        return {}


CONSTITUTION = load_constitution()


@functions_framework.cloud_event
def session(cloud_event):
    """
    Triggered by 'judgment-call'.
    Evaluates the 'Agent Proposal' against the Constitution.
    """
    try:
        # 1. Decode Evidence
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        evidence = json.loads(pubsub_message)
        case_id = evidence.get("id", "unknown")
        iteration = evidence.get("iteration", 0)

        logger.info(f"Court in Session. Case: {case_id} | Iteration: {iteration}")

        # 2. Deliberate (Policy Match)
        verdict = "PASSED"
        violations = []

        # Simple Simulation of Checks
        if "curl | sh" in str(evidence):
            verdict = "BLOCKED"
            violations.append("DoD blocked pattern detection")

        # Iteration Gate
        if iteration < 3 and verdict == "PASSED":
            verdict = "MITIGATE"  # Force refinement loops
            violations.append("Mandatory refinement loop (Iteration < 3)")

        # 3. Issue Ruling (Ledger)
        scorecard = {
            "case_id": case_id,
            "verdict": verdict,
            "violations": violations,
            "timestamp": "2026-01-29T00:00:00Z",  # Mock
        }

        logger.info(f"Ruling: {verdict}")

        # Publish to Ledger for Audit
        ledger_bytes = json.dumps(scorecard).encode("utf-8")
        publisher.publish(LEDGER_TOPIC, ledger_bytes)

        # 4. Feedback Loop (Return to Swarm)
        if verdict == "MITIGATE":
            # Send back to minion for refinement
            next_mission = evidence
            next_mission["iteration"] = iteration + 1
            next_mission["feedback"] = violations

            logger.info("Remanding case to Swarm for refinement.")
            monkey_bytes = json.dumps(next_mission).encode("utf-8")
            publisher.publish(MONKEY_TOPIC, monkey_bytes)

        elif verdict == "PASSED":
            logger.info("Action Approved. Execution allowed.")
            # Trigger Execution Function (e.g. Cloud Build)

        else:
            logger.warning("Action BLOCKED. Security Halt.")

    except Exception as e:
        logger.error(f"Mistrial: {e}")
        raise
