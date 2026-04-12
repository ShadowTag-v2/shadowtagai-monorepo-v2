import base64
import json
import logging
import os

import functions_framework
from google.cloud import pubsub_v1

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WingCommander")

PROJECT_ID = os.getenv("GCP_PROJECT", "shadowtag-omega-v2")
JUDGMENT_TOPIC = f"projects/{PROJECT_ID}/topics/judgment-call"

publisher = pubsub_v1.PublisherClient()


@functions_framework.cloud_event
def dispatch_swarm(cloud_event):
    """
    Triggered by 'monkey-summons'.
    Dispatches the Swarm (Agents) based on the mission context.
    Orchestrates the loop: Agent -> Judge -> Agent.
    """
    try:
        # 1. Decode Mission
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        mission_data = json.loads(pubsub_message)
        mission_id = mission_data.get("mission_id", "unknown")
        iteration = mission_data.get("iteration", 1)

        logger.info(f"Refuelling Swarm for Mission: {mission_id} | Iteration: {iteration}")

        # 2. Swarm Logic (The "minion")
        # In a full implementation, this calls the Vertex AI / Gemini API.
        # Here we simulate the Agent's thought process.

        # Simulated Agent Action
        agent_proposal = {
            "id": mission_id,
            "iteration": iteration,
            "proposed_action": "deploy_Kafka_consumer",
            "code_snippet": "gcloud run deploy...",  # Just a label for now
            "risk_assessment": "low" if iteration > 2 else "unknown",
        }

        # 3. The Loop Constraint
        if iteration > 4:
            logger.warning("Max iterations reached. Forcing landing.")
            return

        # 4. Send to Judge (The Brake)
        logger.info("Submitting proposal to Judge 6...")
        data_str = json.dumps(agent_proposal)
        data_bytes = data_str.encode("utf-8")
        publisher.publish(JUDGMENT_TOPIC, data_bytes)

        logger.info("Proposal sent to court.")

    except Exception as e:
        logger.error(f"Swarm Disarray: {e}")
        raise
