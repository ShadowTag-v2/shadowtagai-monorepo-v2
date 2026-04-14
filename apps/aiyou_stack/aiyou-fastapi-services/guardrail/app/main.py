import json
import logging
import os

import requests
from fastapi import FastAPI, HTTPException
from google.cloud import modelarmor_v1, storage
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

# --- LOGGING & CONFIG ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("shadowtag-guardrail")

CONFIG_BUCKET = os.getenv("CONFIG_BUCKET", "shadowtag-omega-v2-safety-config")
ARMOR_TEMPLATE_ID = os.getenv("ARMOR_TEMPLATE_ID")
HIVE_API_KEY = os.getenv("HIVE_API_KEY")

# --- CLIENTS (The "Outside Resources") ---
storage_client = storage.Client()
armor_client = modelarmor_v1.ModelArmorClient()


class SafetyEstop:
    def __init__(self):
        self.kill_switch_data = {"entities": [], "phrases": []}
        self.last_refresh = 0
        # Load initial config
        self._refresh_config()

    def _refresh_config(self):
        """Dynamically loads the Blocklist from GCS.
        This allows you to add a name like "Ashley St. Clair" to the bucket
        and have it blocked instantly without redeploying code.
        """
        try:
            bucket = storage_client.bucket(CONFIG_BUCKET)
            blob = bucket.blob("kill_switch.json")
            if blob.exists():
                data = json.loads(blob.download_as_text())
                self.kill_switch_data = data
                logger.info("Updated Kill Switch Config from GCS.")
        except Exception as e:
            logger.error(f"Failed to refresh config: {e}")

    def check_kill_switch(self, prompt: str):
        """Corner 1: Deterministic Check (Latency < 1ms)"""
        prompt_lower = prompt.lower()

        # Check Entities
        for entity in self.kill_switch_data.get("entities", []):
            if entity.lower() in prompt_lower:
                return True, f"BLOCK: Kill Switch Entity '{entity}'"

        # Check Phrases
        for phrase in self.kill_switch_data.get("phrases", []):
            if phrase.lower() in prompt_lower:
                return True, "BLOCK: Kill Switch Phrase"

        return False, ""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def call_google_armor(self, prompt: str) -> tuple[bool, bool, str]:
        """Corner 2: The Bodyguard (Google Model Armor).
        Returns: (is_blocked, has_pii, reason)
        """
        try:
            # Create the request
            request = modelarmor_v1.SanitizeUserPromptRequest(
                name=ARMOR_TEMPLATE_ID, user_prompt_data=modelarmor_v1.DataItem(text=prompt),
            )

            # Call Google API
            response = armor_client.sanitize_user_prompt(request=request)

            # Analyze Result
            # 1. Check for PII (to trigger strict mode)
            has_pii = False
            if response.sanitization_result.filter_match_results:
                for match in response.sanitization_result.filter_match_results:
                    if match.filter_type == modelarmor_v1.FilterType.SENSITIVE_DATA_PROTECTION:
                        has_pii = True

            # 2. Check for Hard Blocks (Jailbreaks/Injection)
            # Model Armor returns a 'sanitized' prompt or flags.
            # If the response indicates high confidence block:
            if response.sanitization_result.filter_match_results:
                for match in response.sanitization_result.filter_match_results:
                    if match.filter_type == modelarmor_v1.FilterType.PROMPT_INJECTION_AND_JAILBREAK:
                        return True, has_pii, "BLOCK: Prompt Injection Detected"

            return False, has_pii, ""

        except Exception as e:
            logger.error(f"Google Armor Error: {e}")
            # FAIL CLOSED: If security is down, nobody enters.
            raise HTTPException(status_code=503, detail="Safety Service Unavailable")

    @retry(stop=stop_after_attempt(2))
    def call_hive(self, prompt: str, strict_mode: bool) -> tuple[bool, str]:
        """Corner 3: The Censor (Hive).
        Uses 'Strict Mode' if Google detected PII.
        """
        url = "https://api.thehive.ai/api/v2/task/sync"
        headers = {"Authorization": f"Token {HIVE_API_KEY}"}
        data = {"text_data": prompt}

        try:
            resp = requests.post(url, headers=headers, data=data, timeout=2.0)
            result = resp.json()

            # Extract scores
            classes = (
                result.get("status", [])[0]
                .get("response", {})
                .get("output", [])[0]
                .get("classes", [])
            )
            scores = {item["class"]: item["score"] for item in classes}

            # Determine Threshold
            # THE DISTINCTION: Strict Mode (0.01) vs Standard (0.5)
            threshold = 0.01 if strict_mode else 0.5

            # Check for Sexual Content
            bad_classes = ["sexual_activity", "sexual_attire", "suggestive"]
            for cls in bad_classes:
                if scores.get(cls, 0) > threshold:
                    mode = "STRICT" if strict_mode else "STANDARD"
                    return True, f"BLOCK: Hive {cls} > {threshold} ({mode})"

            return False, ""

        except Exception as e:
            logger.error(f"Hive API Error: {e}")
            # Fail Closed
            raise HTTPException(status_code=503, detail="Content Moderation Unavailable")


# --- APP FACTORY ---
app = FastAPI()
estop = SafetyEstop()


class PromptRequest(BaseModel):
    prompt: str


@app.post("/validate")
async def validate_prompt(req: PromptRequest):
    # 1. Local Kill Switch (Fastest)
    killed, reason = estop.check_kill_switch(req.prompt)
    if killed:
        raise HTTPException(status_code=403, detail=reason)

    # 2. Google Model Armor (Security)
    armor_blocked, has_pii, armor_reason = estop.call_google_armor(req.prompt)
    if armor_blocked:
        raise HTTPException(status_code=403, detail=armor_reason)

    # 3. Hive (Content Safety) - Pass 'has_pii' to trigger Strict Mode
    hive_blocked, hive_reason = estop.call_hive(req.prompt, strict_mode=has_pii)
    if hive_blocked:
        raise HTTPException(status_code=422, detail=hive_reason)

    return {"status": "SAFE", "pii_detected": has_pii}
