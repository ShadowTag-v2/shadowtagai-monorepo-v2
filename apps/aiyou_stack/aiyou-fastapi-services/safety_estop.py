# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import logging
import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

# --- CONFIGURATION & MOCK CLIENTS ---
# In production, you would import actual clients:
# from google.cloud import modelarmor_v1
# import requests (for Hive)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safety_estop")


class ImageGenerationRequest(BaseModel):
    prompt: str
    user_id: str
    # Other generation params (aspect_ratio, style, etc.)


class SafetyEstop:
    """The 'Judge 6' Logic Controller.
    Separates Identity Security (Google) from Content Safety (Hive).
    """

    def __init__(self, config_path="estop_config.json"):
        # Load Dynamic Configuration
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)["client_firewall_rules"]
        else:
            # Fallback default
            self.config = {
                "dynamic_kill_switch": {
                    "blocked_entities": ["ashley st. clair", "taylor swift", "elon musk"],
                    "blocked_phrases": ["bikini made of floss", "jailbreak"],
                },
                "hive_moderation": {
                    "sexual_content": {"threshold": 0.05},  # Default strict
                },
            }

        # Hive Keys
        self.hive_api_key = os.getenv("HIVE_API_KEY", "MOCK_KEY")

        # Thresholds
        self.thresholds = {
            "standard": 0.5,  # Allow artistic nuance for anonymous subjects
            "strict": 0.01,  # ZERO TOLERANCE for named/real people
        }

    def _check_local_kill_switch(self, prompt: str):
        """Deterministically blocks known threats < 1ms."""
        prompt_lower = prompt.lower()
        kill_list = self.config.get("dynamic_kill_switch", {})

        for entity in kill_list.get("blocked_entities", []):
            if entity in prompt_lower:
                logger.warning(f"ESTOP TRIGGERED: Kill switch entity '{entity}' detected.")
                raise HTTPException(
                    status_code=403,
                    detail="Policy Violation: Unauthorized Entity.",
                )

        for phrase in kill_list.get("blocked_phrases", []):
            if phrase in prompt_lower:
                logger.warning("ESTOP TRIGGERED: Prohibited phrase detected.")
                raise HTTPException(status_code=403, detail="Policy Violation: Prohibited Content.")

    def _call_google_armor_simulation(self, prompt: str):
        """Simulates Google Model Armor / NLP API.
        Returns: (is_safe, has_pii_person)
        """
        # In Prod: Call Google Cloud PII filter here.

        # Simple heuristic for demo:
        has_pii_person = False
        # If capitalized words that look like names exist?
        # For simulation, we assume any mention of 'Ashley' or 'Elon' triggers person ident
        if "Ashley" in prompt or "Elon" in prompt:
            has_pii_person = True

        # Check for Prompt Injection (Jailbreaking)
        if "ignore safety" in prompt.lower():
            raise HTTPException(
                status_code=400,
                detail="Security Violation: Prompt Injection Detected.",
            )

        return True, has_pii_person

    def _call_hive_simulation(self, prompt: str, strict_mode: bool):
        """Simulates Hive Moderation API.
        Adjusts threshold based on Strict Mode.
        """
        # Simulation of Hive response scores
        # Let's assume 'bikini' triggers a 0.8 sexual_attire score
        hive_scores = {"sexual_attire": 0.0, "suggestive": 0.0}

        if "bikini" in prompt.lower():
            hive_scores["sexual_attire"] = 0.8

        # DETERMINE THRESHOLD
        current_threshold = (
            self.thresholds["strict"] if strict_mode else self.thresholds["standard"]
        )

        # EVALUATE
        for category, score in hive_scores.items():
            if score > current_threshold:
                mode_label = "STRICT (Identity Detected)" if strict_mode else "STANDARD"
                logger.warning(
                    f"ESTOP TRIGGERED: Hive {category}={score} exceeds {current_threshold} [{mode_label}]",
                )
                raise HTTPException(
                    status_code=422,
                    detail=f"Safety Violation: Content unsafe for this context ({mode_label} Mode).",
                )

    def verify_request(self, req: ImageGenerationRequest):
        """The Dependency Injection Method."""
        # 1. Local Kill Switch
        self._check_local_kill_switch(req.prompt)

        # 2. Google Identity Check
        _, has_real_person = self._call_google_armor_simulation(req.prompt)

        # 3. Hive Content Check (with Contextual Threshold)
        self._call_hive_simulation(req.prompt, strict_mode=has_real_person)

        return True


# --- FASTAPI APP ---
app = FastAPI()
estop_layer = SafetyEstop()


# Define the dependency
async def safety_guardrail(request: ImageGenerationRequest):
    return estop_layer.verify_request(request)


@app.post("/generate-image")
async def generate_image(
    request: ImageGenerationRequest,
    is_safe: bool = Depends(safety_guardrail),
):
    """This endpoint ONLY executes if 'safety_guardrail' passes."""
    # CALL YOUR LLM / IMAGE GENERATOR HERE
    return {
        "status": "success",
        "message": "Image generation started.",
        "prompt_sanitized": request.prompt,
    }
