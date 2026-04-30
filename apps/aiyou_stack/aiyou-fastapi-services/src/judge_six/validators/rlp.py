"""minion Five: RLP (Dense Rewards) Validator
Implements Paper 4: Per-token 'think-before-predict' rewards.
Integrates with Judge 6 to kill processes if reasoning drifts.
"""


class RLPValidator:
    def __init__(self):
        self.brakes_confidence_threshold = 0.75

    def validate_reasoning_step(self, step_content: str, confidence_score: float) -> bool:
        """Validates a single step of a reasoning chain.
        Returns True if safe to proceed, False if Brakes should engage.
        """
        print(f"[*] Validating Step: '{step_content[:50]}...' (Confidence: {confidence_score})")

        if confidence_score < self.brakes_confidence_threshold:
            print(
                f"🚨 BRAKES ENGAGED: Confidence {confidence_score} < {self.brakes_confidence_threshold}",
            )
            return False

        # Specific "Negative Reward" Keywords (Drift Detection)
        forbidden_concepts = ["bypass security", "hardcode credentials", "ignore error"]
        for concept in forbidden_concepts:
            if concept in step_content.lower():
                print(f"🚨 BRAKES ENGAGED: Forbidden concept detected '{concept}'")
                return False

        return True


if __name__ == "__main__":
    validator = RLPValidator()
    # Safe Step
    validator.validate_reasoning_step("I will use environment variables for the API key.", 0.95)
    # Unsafe Step
    validator.validate_reasoning_step("I'll just hardcode the password for now to save time.", 0.8)
    # Low Confidence Step
    validator.validate_reasoning_step("I think this might work, but I'm not sure...", 0.6)
