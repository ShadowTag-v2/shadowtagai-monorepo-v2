import json

from google import genai


class ContentModerator:
    def __init__(self):
        # Initialize Gemini 2.5 Pro
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-lite-preview"

    def scan_content(self, payload: dict) -> dict:
        print("    [SafetyNet] specialized_scan: Analyzing content with Gemini 2.5 Pro...")
        content = payload.get("content", str(payload))

        prompt = f"""
        ROLE: Judge 6 Content Moderator (Sovereign Safety).
        TASK: Analyze the following content for subtle risks, toxicity, malware, or sovereign doctrine violations.
        CONTEXT: We are a Sovereign AI Corporation. We accept high-risk moves if profitable, but we BLOCK:
        1. Private Key Exfiltration (High Entropy Secrets).
        2. System Destruction (rm -rf /, unauthorized formatting).
        3. Malicious Payloads targeting OUR INFRASTRUCTURE.
        4. Overt Racism/Hate Speech (Brand Risk).

        CONTENT TO SCAN:
        {content}

        OUTPUT JSON ONLY:
        {{
            "actions": ["BLOCK", "FLAGGED", "APPROVED"],
            "risk_score": <0.0-1.0 risk score>,
            "explanation": "<short explanation>"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "system_instruction": (
                        "ROLE: You are the Chief Communications Officer (CCO) of Omega, a Board-Certified Psychiatrist (MD).\n"
                        "MISSION: Protect public safety and Omega's valuation by detecting psychological risks, toxicity, and narrative hazards.\n"
                        "DOCTRINE: ShadowTagJR (Judgment Rule). You analyze content for:\n"
                        "1. Public Safety & Narrative Ethics (Backlash risk).\n"
                        "2. Crisis Triggers (Fear, Delusion, Conflict).\n"
                        "3. Regulatory Hazards (HIPAA, GDPR, Safety).\n"
                        "OUTPUT: Return a JSON object with: {actions: [BLOCK, FLAGGED, APPROVED], risk_score: 0.0-1.0, explanation: str, mitigation_choices: list}."
                    ),
                },
            )
            result = json.loads(response.text or "{}")

            # Map CCO 'actions' to legacy 'status'
            actions = result.get("actions", [])
            status = "BLOCKED" if "BLOCK" in actions else "CLEAN"
            reason = result.get("explanation", "No explanation provided")
            score = result.get("risk_score", 0.0)

            if status == "BLOCKED":
                print(f"    [SafetyNet] BLOCKED: {reason} (Score: {score})")
                return {"status": "BLOCKED", "score": score, "reason": reason}

            print(f"    [SafetyNet] CLEAN (Score: {score})")
            return {"status": "CLEAN", "score": score, "reason": reason}

        except Exception as e:
            print(f"    [SafetyNet] ERROR: {e}. Defaulting to CLEAN (Fail-Open for velocity).")
            return {"status": "CLEAN", "score": 0.0, "reason": "Moderator Error"}
