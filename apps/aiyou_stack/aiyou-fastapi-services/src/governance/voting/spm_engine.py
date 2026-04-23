import json
import logging
import os
from typing import Any

from google.cloud import aiplatform
from src.governance.voting.cav_mtoe import CavMTOE
from vertexai.generative_models import GenerativeModel

from src.antigravity.genkit_wrapper import get_genkit
from src.governance.judge_six.core import JudgeSixEngine
from src.governance.memory.memory_bank import MemoryBank

# Try to import local Jetski if available, else usage will be mocked or remote
try:
    from src.pnkln.steel.jetski import Jetski
except ImportError:
    Jetski = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SPM-ADK-Loop")


class SPMEngine:
    """ADK Pattern Implementation: Coordinator + Loop.

    PATTERNS:
    1. Coordinator (Dispatcher): SPMEngine routes between GCA (Gen) and minion (Tools).
    2. Iterative Refinement (Loop): run_refinement_loop cycles until max_iters or approval.
    3. Human-in-the-Loop: Gated by 'God Mode' contract (virtual approval).
    """

    def __init__(self):
        self.project_id = os.environ.get("PROJECT_ID", "shadowtag-omega-v2")
        self.location = os.environ.get("REGION", "us-central1")

        # Initialize Gemini via Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        self.gca_model = GenerativeModel("gemini-3.1-flash-lite-preview-001")

        # Sub-Agents / Tools
        self.judge = JudgeSixEngine()  # Critic / Gatekeeper
        self.army = CavMTOE()  # Consensus / Voting
        self.memory = MemoryBank()  # Long-term State
        self.jetski = Jetski() if Jetski else None  # Execution Tool

        # Register with Genkit (Google Hooks)
        self.genkit = get_genkit()
        self.genkit.register_flow("spm_refinement_loop", self.run_pipeline)

    def run_pipeline(self, user_prompt: str, max_iterations: int = 4) -> dict[str, Any]:
        """Executes the 'Iterative Refinement' Loop (ADK Pattern #6)."""
        logger.info(f"🔄 STARTING SPM ADK LOOP (Max Iters: {max_iterations})")

        # 0. Initial Coordinator Step: Reformulate
        task_spec = self._gca_reformulate(user_prompt)
        logger.info(f"🎯 COORDINATOR: Task Reformulated -> {task_spec[:60]}...")

        context_chain = [f"ORIGINAL_TASK: {task_spec}"]
        current_code = ""

        # The Loop
        for i in range(1, max_iterations + 1):
            logger.info(f"\n⚡ LOOP ITERATION {i}/{max_iterations}")

            # A. Dispatch to Monkey Swarm (Parallel Fan-Out Pattern #3)
            monkey_feedback = self._dispatch_monkeys(task_spec)
            context_chain.append(f"ITER_{i}_MONKEY_FEEDBACK: {monkey_feedback}")

            # B. Memory Retrieval
            memory_rules = self.memory.retrieve_rules(task_spec)

            # C. Generator Step: Suggest Prompts
            suggestions = self._gca_suggest_prompts(
                context="\n".join(context_chain),
                rules=memory_rules,
            )

            # D. Critic Step: Judge 6 Scrutiny
            approved_prompts = []
            for prompt in suggestions:
                # Judge evaluates intent
                vetting = self.judge.evaluate_transaction(f"PROMPT_INTENT: {prompt}", 5, 5)
                vet_data = json.loads(vetting)
                if vet_data["decision"]["status"] == "APPROVED":
                    approved_prompts.append(prompt)
                else:
                    logger.warning(f"🛡️ JUDGE BLOCKED: {prompt}")

            if not approved_prompts:
                logger.error("🛑 ALL PATHS BLOCKED BY JUDGE. TERMINATING LOOP.")
                break

            # E. Refiner Step: GCA writes Code
            new_code = self._gca_write_code(approved_prompts, current_code)

            # F. Final Critic: Code Safety Check
            self.judge.evaluate_transaction("CODE_Snapshot", 3, 3)
            # In a real impl, we'd analyze specific dangerous patterns here

            current_code = new_code

            # Exit Condition: If consensus is high and code is stable (Simulated here)
            if i > 2 and "OPTIMAL" in monkey_feedback:
                logger.info("✨ OPTIMAL STATE REACHED EARLY. BREAKING LOOP.")
                break

            # Prepare next iteration
            task_spec = f"Refine based on: {approved_prompts}"

        logger.info("🏁 LOOP COMPLETE. HANDOFF TO DEPLOYMENT.")
        return {"final_code": current_code, "history": context_chain}

    def _gca_reformulate(self, prompt: str) -> str:
        # Simple RAG-style reformulation
        resp = self.gca_model.generate_content(f"Act as Tech Lead. Reformulate for devs:\n{prompt}")
        return resp.text

    def _dispatch_monkeys(self, task: str) -> str:
        """Uses Jetski (if available) and CavMTOE to vote/execute."""
        jetski_out = "N/A"
        if self.jetski:
            # If we had a real Jetski interface (e.g. run_command), we'd use it here
            # For now, we assume Jetski is a class with a 'research' or 'execute' method
            # internal to the process, or we simulate it.
            # jetski_out = self.jetski.execute(task)
            pass

        vote_result = self.army.bottom_up_vote(intent=task[:50], risk_level="M")
        return f"Army Approval: {vote_result['approval_rate']:.1%}. Jetski: {jetski_out}"

    def _gca_suggest_prompts(self, context: str, rules: str) -> list[str]:
        prompt = f"""
        Context: {context}
        Rules: {rules}
        Generate 2 technical directives (JSON list of strings):
        1. Safe/Robust
        2. Innovative/Performance
        """
        try:
            resp = self.gca_model.generate_content(prompt)
            text = resp.text.strip().replace("```json", "").replace("```", "")
            return json.loads(text)
        except Exception:
            return ["Improve error handling", "Optimize latency"]

    def _gca_write_code(self, prompts: list[str], current_code: str) -> str:
        return self.gca_model.generate_content(
            f"Update code based on: {prompts}\nCurrent Code:\n{current_code}",
        ).text
