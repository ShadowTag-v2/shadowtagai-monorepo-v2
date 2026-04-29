# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""BarExamProtocol - "Cor.Claude_Code_6" Gatekeeper.
Prevents dumb agents from polluting memory.
"""

import json

from src.shadowtag_v4.services.gemini_core import GeminiAntigravity

from agents.legal_whiteboard import LegalWhiteboard

LEVEL_CRITERIA = {
    0: "Basic Execution: Can the agent complete a defined task without syntax errors?",
    1: "Pattern Recognition: Can the agent identify recurring errors?",
    2: "Optimization: Can the agent refactor code to reduce token usage by >10%?",
}


class BarExamProtocol:
    def __init__(self, project_id: str):
        self.whiteboard = LegalWhiteboard()
        self.judge = GeminiAntigravity(project_id=project_id)

    def administer_exam(self, candidate_id: str, current_level: int, proof_of_work: dict) -> tuple:
        target_level = current_level + 1
        criteria = LEVEL_CRITERIA.get(target_level, "Unknown Level")

        print(f"///▞ EXAM START :: Candidate {candidate_id} -> Level {target_level}")
        prompt = f"""
        ACT AS: Cor.Claude_Code_6.
        TASK: Evaluate Proof of Work against Criteria.
        CRITERIA: {criteria}
        PROOF: {json.dumps(proof_of_work, default=str)}
        OUTPUT JSON ONLY: {{"verdict": "PASS" or "FAIL", "reasoning": "..."}}
        """

        try:
            # Use Gemini 3 high thinking for complex evaluation
            response = self.judge.model.generate_content(
                prompt,
                generation_config=self.judge._get_generation_config(
                    thinking_level="high",
                    json_output=True,
                ),
            )
            raw = response.text.replace("```json", "").replace("```", "")
            result = json.loads(raw)

            if result.get("verdict") == "PASS":
                self.whiteboard.record_learning(
                    candidate_id,
                    f"Passed Level {target_level}",
                    result,
                )
                return True, result.get("reasoning")
            return False, result.get("reasoning")
        except Exception as e:
            return False, f"System Error: {e!s}"

    @staticmethod
    def spawn_first_child():
        print("///▞ SPAWN :: First Child Agent Created")

    @staticmethod
    def activate_swarm_mode():
        print("///▞ SWARM :: Swarm Mode Activated")
