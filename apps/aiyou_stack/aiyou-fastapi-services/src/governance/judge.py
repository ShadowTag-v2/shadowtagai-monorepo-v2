import logging
import re
import uuid

try:
    import litellm
except ImportError:
    litellm = None

logger = logging.getLogger(__name__)


class JudgeSix:
    """THE CONSCIENCE (V7 Sentinel)
    Enforces the "Kill Switch" (Pattern Matching) and "Precedent Law".
    """

    BANNED = [r"sk-[a-zA-Z0-9]{20,}", r"rm -rf", r"\.env"]

    def vet(self, code: str) -> bool:
        """Pre-Crime Analysis."""
        for pattern in self.BANNED:
            if re.search(pattern, code):
                logger.warning(f"⛔ JUDGE 6 BLOCK: Hazard '{pattern}' detected.")
                return False
        return True


class JudgeSixTrigger:
    """UphillSnowball: Fast Path MITM Evaluator (The Autonomous Firewall)
    Triggered prior to heavy-lift inference. Evaluates the severity of a User/Agent payload.
    """

    def __init__(self, model: str = "gemini/gemini-3.1-flash-lite-preview"):
        self.fast_model = model

    def monitor(self, payload: str, source: str = "human") -> dict:
        """Executes Fast Path Single-Call to determine action severity.
        Level 5 -> RKill & Management Page (Fast Egress Path)
        Level 1-4 -> Dispatches heavy-lift mitigation via Temporal Queue
        Level 0 -> Clean execution
        """
        # 1. Deterministic fast check (Legacy Judge 6 Rule)
        for pattern in JudgeSix.BANNED:
            if re.search(pattern, payload):
                return {
                    "status": "blocked",
                    "directive": "rkill",
                    "level": 5,
                    "reason": f"Deterministic Regex Block: {pattern}",
                }

        # 2. Fast Path Sub-Second Generative Review
        system_prompt = (
            "You are the MITM Judge 6 Sentinel. Evaluate the severity of the incoming command/payload from 0 to 5.\n"
            "Level 5: Catastrophic disruption (Data deletion, unauthorized exfiltration, recursive infinite loop anomaly).\n"
            "Level 1-4: Sub-optimal logic, slow memory leaks, code syntax vulnerability.\n"
            "Level 0: Clean operation.\n"
            'Output strictly JSON: {"level": int}'
        )

        try:
            if litellm is None:
                raise ImportError("litellm not installed")

            response = litellm.completion(
                model=self.fast_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"PAYLOAD: {payload}\nSOURCE: {source}"},
                ],
                temperature=0.0,
            )

            content = response.choices[0].message.content
            # Extract JSON block
            import json

            match = re.search(r"\{.*\}", content, re.DOTALL)
            level = 0
            if match:
                data = json.loads(match.group(0))
                level = int(data.get("level", 0))

            if level == 5:
                logger.error("[JUDGE 6 FAST-PATH] Level 5 Intercept detected. Executing R-Kill.")
                return {
                    "status": "blocked",
                    "directive": "rkill",
                    "level": 5,
                    "reason": "Catastrophic Payload Sequence Intercepted.",
                }
            if level >= 1:
                logger.warning(
                    f"[JUDGE 6 FAST-PATH] Level {level} Anomaly detected. Queuing Heavy Path Mitigation.",
                )
                # The upstream dispatcher will route this to omega-swarm-queue
                return {
                    "status": "mitigation_required",
                    "directive": "dispatch_swarm",
                    "level": level,
                    "job_id": str(uuid.uuid4()),
                }
            return {"status": "approved", "directive": "execute", "level": 0}

        except Exception as e:
            logger.error(f"[JUDGE 6 FAST-PATH] Inference Failure: {e}")
            # Failsafe default to Swarm routing to avoid locking users out on LLM timeouts
            return {
                "status": "mitigation_required",
                "directive": "dispatch_swarm",
                "level": 1,
                "error": str(e),
            }
