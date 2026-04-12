import logging

from ..agents.recursive_rlm import RecursiveAgent


class RoutingAgent:
    def __init__(self):
        self.brain = RecursiveAgent()

    def dispatch(self, user_request: str) -> dict:
        """
        Decides: Do we keep this LOCAL or send to SWARM?
        Uses ECHO PROTOCOL for 97% classification accuracy.
        """

        # 1. CONSTRUCT THE ECHO PROMPT
        # We repeat the classification instruction to force attention.

        classification_prompt = f"""
        ROLE: System Router.
        TASK: Classify the following User Request into 'LOCAL' (Simple edit/question) or 'SWARM' (Complex research/multi-file refactor).

        USER REQUEST: "{user_request}"

        ---

        ROLE: System Router.
        TASK: Classify the following User Request into 'LOCAL' (Simple edit/question) or 'SWARM' (Complex research/multi-file refactor).

        USER REQUEST: "{user_request}"

        OUTPUT FORMAT: Just the word 'LOCAL' or 'SWARM'.
        """

        # 2. CALL THE BRAIN (RecursiveAgent handles the API)
        # Note: RecursiveAgent might also double-echo if configured, which is fine.
        verdict = self.brain.solve(classification_prompt).strip().upper()

        logging.info(f"🚦 ROUTER: Verdict for '{user_request[:20]}...' is {verdict}")

        if "SWARM" in verdict:
            return {"route": "SWARM", "target": "autoresearch", "payload": user_request}
        else:
            return {"route": "LOCAL", "target": "gemini_flash", "payload": user_request}


router = RoutingAgent()
