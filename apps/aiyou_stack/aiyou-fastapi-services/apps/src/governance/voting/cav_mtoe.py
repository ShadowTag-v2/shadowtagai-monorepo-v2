import random


class CavMTOE:
    """
    The 650-Unit Digital Battalion.
    Implements 'Bottom-Up' Consensus Voting for Risk Acceptance.
    """

    def __init__(self, num_soldiers: int = 650):
        self.num_soldiers = num_soldiers
        # Simulate Glicko scores (reliability metric)
        self.agents = [{"id": i, "glicko": random.randint(1200, 1800)} for i in range(num_soldiers)]

    def bottom_up_vote(self, intent: str, risk_level: str) -> dict:
        """Polls the army. Higher risk requires higher consensus."""
        thresholds = {"L": 0.50, "M": 0.66, "H": 0.90, "EH": 1.00}
        required_approval = thresholds.get(risk_level, 0.90)

        # Poll 5% for speed, or full battalion for High Risk
        sample_size = 20 if risk_level in ["L", "M"] else self.num_soldiers
        sample = random.sample(self.agents, sample_size)

        votes_for = 0
        for agent in sample:
            # Bias logic: Higher Glicko agents are more conservative
            bias = (agent["glicko"] / 2000) if risk_level != "L" else 0.8
            if random.random() < bias:
                votes_for += 1

        approval_rate = votes_for / sample_size
        verdict = "A" if approval_rate >= required_approval else "B"

        return {
            "final_action": verdict,
            "approval_rate": approval_rate,
            "threshold": required_approval,
            "troops_count": sample_size,
        }
