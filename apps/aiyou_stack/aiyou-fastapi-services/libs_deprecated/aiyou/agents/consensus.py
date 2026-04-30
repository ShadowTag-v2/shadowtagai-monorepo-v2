import logging

# Stub RecursiveAgent if missing
try:
    from .recursive_rlm import RecursiveAgent
except ImportError:

    class RecursiveAgent:
        def solve(self, p):
            return "Mock Solution"


class ConsensusAgent:
    def __init__(self):
        self.agent = RecursiveAgent()

    def execute_critical(self, prompt: str, rounds: int = 3) -> str:
        logging.info(f"🗳️ CONSENSUS: Initiating {rounds}-Round Voting...")
        results = []
        for _i in range(rounds):
            res = self.agent.solve(prompt)
            results.append(res)

        judge_prompt = f"""
        ROLE: Supreme Court Judge.
        TASK: Review drafts, pick best.
        DRAFTS: {results}
        """
        return self.agent.solve(judge_prompt)
