"""
Persistent Memory Manager for Flying minion
Inspired by Gemini Code Assist Memory: https://cloud.google.com/blog/products/ai-machine-learning/memory-for-ai-code-reviews-using-gemini-code-assist

Capabilities:
1. Learn from interactions (PR comments, feedback).
2. Infer generalized rules (using Gemini).
3. Apply rules to future tasks (Guidance & Filtering).

Storage: Local JSON (simulating managed service).
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class LearnedRule:
    rule_id: str
    content: str  # e.g., "In Java, import statements should not be line-wrapped."
    context_tags: list[str]  # e.g., ["java", "imports", "style"]
    confidence: float
    source: str  # e.g., "PR-123 comment"


class MemoryManager:
    def __init__(self, memory_file: str = "src/antigravity/memory/learned_rules.json"):
        self.memory_file = Path(memory_file)
        self.rules: list[LearnedRule] = []
        self._load_memory()

    def _load_memory(self):
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    data = json.load(f)
                    self.rules = [LearnedRule(**item) for item in data]
                logger.info(f"Loaded {len(self.rules)} rules from memory.")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                self.rules = []
        else:
            # Create dir if not exists
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            self.rules = []

    def save_memory(self):
        try:
            with open(self.memory_file, "w") as f:
                data = [rule.__dict__ for rule in self.rules]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    async def extract_rule_from_interaction(
        self, user_feedback: str, agent_action: str
    ) -> LearnedRule | None:
        """
        Use Gemini to infer a generalized rule from interaction.
        (Stubbed LLM call for now - GCA pattern)
        """
        # TODO: Real LLM call here to generalize
        # prompt = f"Infer a coding rule from this feedback: {user_feedback} on action: {agent_action}"

        # Simulating inference
        import uuid

        inferred_rule_text = f"User preference detected: {user_feedback}"

        rule = LearnedRule(
            rule_id=str(uuid.uuid4())[:8],
            content=inferred_rule_text,
            context_tags=["general"],
            confidence=0.85,
            source="interaction_inference",
        )

        self.rules.append(rule)
        self.save_memory()
        return rule

    def retrieve_relevant_rules(self, context_tags: list[str]) -> list[LearnedRule]:
        """
        Retrieve rules relevant to the current context.
        """
        # Simple set intersection for now
        relevant = []
        for rule in self.rules:
            if (
                any(tag in rule.context_tags for tag in context_tags)
                or "general" in rule.context_tags
            ):
                relevant.append(rule)
        return relevant

    def filter_suggestions(self, suggestions: list[str], context_tags: list[str]) -> list[str]:
        """
        Filter agent suggestions against learned rules.
        """
        rules = self.retrieve_relevant_rules(context_tags)
        filtered = []

        for suggestion in suggestions:
            # Check against rules (Mock check)
            violation = False
            for _rule in rules:
                # In real prod, use LLM to check "Does 'suggestion' violate 'rule.content'?"
                pass

            if not violation:
                filtered.append(suggestion)

        return filtered


if __name__ == "__main__":
    # Test
    mm = MemoryManager()
    print("Memory Manager Initialized")
