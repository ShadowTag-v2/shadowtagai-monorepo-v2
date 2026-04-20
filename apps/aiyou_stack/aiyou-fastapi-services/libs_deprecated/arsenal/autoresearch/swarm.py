import asyncio
import json
import logging

from google import genai
from google.genai import types


class CavMTOE:
    """The Digital Council (Swarm)."""

    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-lite-preview"
        self.personas = [
            {"role": "Security", "bias": "Paranoid", "prompt": "Block if any secrets exposed."},
            {"role": "Product", "bias": "Optimistic", "prompt": "Approve if UX improves."},
            {"role": "Legal", "bias": "Strict", "prompt": "Block if IP/License unclear."},
            {"role": "Ops", "bias": "Stable", "prompt": "Block if it breaks CI."},
            {"role": "Chaos", "bias": "Wild", "prompt": "Approve if it's interesting."},
        ]

    async def _consult_persona(self, persona, intent):
        prompt = f"""
        Role: {persona["role"]} | Bias: {persona["bias"]}
        Intent: "{intent}"
        Instructions: {persona["prompt"]}
        Vote YES or NO. Reason in 1 sentence. JSON.
        """
        try:
            res = await self.client.models.generate_content_async(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            return json.loads(res.text)
        except:
            return {"vote": "NO", "reason": "Timeout"}

    async def deploy_bravo(self, intent: str):
        logging.info(f"🐝 SWARM: Convening Council for '{intent}'...")
        tasks = [self._consult_persona(p, intent) for p in self.personas]
        results = await asyncio.gather(*tasks)

        yes_votes = sum(1 for r in results if r.get("vote") == "YES")
        status = "APPROVED" if yes_votes >= 3 else "REJECTED"

        return {"status": status, "score": f"{yes_votes}/5", "details": results}


def vote(intent):
    return asyncio.run(CavMTOE().deploy_bravo(intent))
