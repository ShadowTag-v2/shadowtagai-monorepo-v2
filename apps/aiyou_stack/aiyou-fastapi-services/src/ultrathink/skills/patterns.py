from abc import ABC, abstractmethod


class ReasoningPattern(ABC):
    """Abstract base class for reasoning patterns."""

    @abstractmethod
    def apply(self, input_text: str) -> str:
        """Apply the reasoning pattern to the input."""
        pass


class ChainOfThought(ReasoningPattern):
    """
    Standard Chain of Thought (CoT) pattern.
    Appends a reasoning trigger to the prompt to encourage step-by-step thinking.
    """

    def __init__(self, trigger_phrase: str = "Let's think step by step."):
        self.trigger_phrase = trigger_phrase

    def apply(self, input_text: str) -> str:
        return f"{input_text}\n\n{self.trigger_phrase}"


class TreeOfThoughts(ReasoningPattern):
    """
    Tree of Thoughts (ToT) pattern.
    Simulates branching reasoning by exploring multiple potential next steps.
    """

    def __init__(self, branches: int = 3):
        self.branches = branches

    def apply(self, input_text: str) -> str:
        # In a real LLM implementation, this would trigger N parallel completions.
        # For the framework scaffold, we structure the prompt to request multiple options.
        return (
            f"{input_text}\n\n"
            f"Please generate {self.branches} distinct alternative approaches or 'thoughts' "
            "to address the above, then evaluate which is best."
        )


class RecursiveCriticism(ReasoningPattern):
    """
    Recursive Criticism and Regulation (RCR) pattern.
    Encourages the model to critique and refine its own output.
    """

    def __init__(self, iterations: int = 2):
        self.iterations = iterations

    def apply(self, input_text: str) -> str:
        # Constructs a prompt chain template for recursive criticism.
        prompt = f"Initial Request: {input_text}\n\n"
        for i in range(self.iterations):
            prompt += (
                f"--- Iteration {i + 1} ---\n"
                "Draft a response. Then, critique it identifying 3 potential flaws. "
                "Finally, rewrite the response addressing those flaws.\n\n"
            )
        return prompt
