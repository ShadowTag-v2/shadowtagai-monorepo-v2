import logging

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

JUDGE6_URL = "http://localhost:8080/validate"


def check_with_judge6(operation: str, confidence: float, vertical: str) -> bool:
    """
    Consults Judge#6 before execution.
    Returns True if PROCEED, False if FREEZE.
    """
    try:
        payload = {"operation": operation, "confidence": confidence, "vertical": vertical}
        response = requests.post(JUDGE6_URL, json=payload)
        response.raise_for_status()

        verdict = response.json()
        if verdict["verdict"] == "PROCEED":
            logging.info(f"✅ Judge#6 APPROVED: {operation} (Reason: {verdict['reason']})")
            return True
        else:
            logging.warning(f"⛔ Judge#6 BLOCKED: {operation} (Reason: {verdict['reason']})")
            return False

    except Exception as e:
        logging.error(f"⚠️ Judge#6 Connection Failed: {e}")
        return False  # Fail safe (closed)
