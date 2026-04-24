"""minion Five: Entropy-Targeted RL Router
Implements Paper 1: Stop training on "easy" parts. Focus compute on high-entropy forks.
"""


class EntropyRouter:
    def __init__(self):
        self.entropy_threshold = 0.7  # Tweak based on validation

    def assess_entropy(self, task_description: str) -> float:
        """Calculates the 'entropy' (uncertainty/complexity) of a task.
        Simple heuristic for MVP:
        - Legal/Contract keywords -> High Entropy
        - Architecture/Pattern keywords -> High Entropy
        - Fix/Typo/Docs -> Low Entropy
        """
        high_entropy_keywords = [
            "contract",
            "liability",
            "architecture",
            "scale",
            "deadlock",
            "race condition",
        ]

        entropy = 0.1
        for word in high_entropy_keywords:
            if word in task_description.lower():
                entropy += 0.3

        return min(entropy, 1.0)

    def route(self, task: str) -> str:
        entropy = self.assess_entropy(task)

        if entropy > self.entropy_threshold:
            return "GEMINI_PRO_1_5_002"  # Deep Thinker for Critical Forks
        return "GEMINI_FLASH_1_5_002"  # Fast Path for Low Entropy


if __name__ == "__main__":
    router = EntropyRouter()
    print(f"Task: 'Fix typo in README' -> Route: {router.route('Fix typo in README')}")
    print(
        f"Task: 'Resolve Postgres Deadlock in billing' -> Route: {router.route('Resolve Postgres Deadlock in billing')}",
    )
