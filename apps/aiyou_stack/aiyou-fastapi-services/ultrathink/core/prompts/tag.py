# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""TAG: Task-Action-Goal

Perfect for performance-oriented objectives.
When you need measurable outcomes.

Philosophy: Start with the end in mind. Define success metrics upfront.
"""

from ultrathink.core.prompts.base import BasePrompt


class TAG(BasePrompt):
    """Task-Action-Goal prompting.

    Usage:
        >>> tag = TAG(
        ...     task="Improve API response time",
        ...     action="Analyze bottlenecks and propose caching strategy",
        ...     goal="Reduce p99 latency from 800ms to <200ms"
        ... )
        >>> result = tag.execute("Current metrics: [...]")

    Why it works:
        - Task: Clear problem definition
        - Action: Specific steps expected
        - Goal: Measurable success criteria (prevents vague outputs)
    """

    def __init__(
        self,
        task: str,
        action: str,
        goal: str,
        constraints: str | None = None,
    ) -> None:
        """Initialize TAG prompt.

        Args:
            task: The problem or objective
            action: Specific actions to take
            goal: Measurable outcome or success metric
            constraints: Optional limitations (budget, time, resources)

        """
        super().__init__(task=task, action=action, goal=goal, constraints=constraints)
        self.task = task
        self.action = action
        self.goal = goal
        self.constraints = constraints

    def format(self, user_input: str) -> str:
        """Generate TAG-structured prompt."""
        prompt = f"""Task: {self.task}

Action Required:
{self.action}

Goal:
{self.goal}"""

        if self.constraints:
            prompt += f"\n\nConstraints:\n{self.constraints}"

        prompt += f"\n\nContext:\n{user_input}"

        return prompt.strip()
