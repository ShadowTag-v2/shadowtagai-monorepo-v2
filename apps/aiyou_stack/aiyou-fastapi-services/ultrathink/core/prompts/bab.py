"""
BAB: Before-After-Bridge

The transformation framework. Perfect for planning, strategy, roadmaps.

Philosophy: Show the gap, paint the vision, build the path.
Borrowed from copywriting, adapted for AI reasoning.
"""

from ultrathink.core.prompts.base import BasePrompt


class BAB(BasePrompt):
    """
    Before-After-Bridge prompting.

    Usage:
        >>> bab = BAB(
        ...     before="SEO ranking: page 8, 200 visitors/month",
        ...     after="Top 3 ranking, 10k+ visitors/month, 5% conversion",
        ...     bridge="12-week content strategy with backlink building"
        ... )
        >>> result = bab.execute("Current site: example.com")

    Why it works:
        - Before: Establishes current pain/state
        - After: Creates compelling vision of success
        - Bridge: Forces concrete, actionable plan
        - Used in marketing, but brilliantly effective for AI planning
    """

    def __init__(
        self,
        before: str,
        after: str,
        bridge: str,
        timeline: str | None = None,
    ) -> None:
        """
        Initialize BAB prompt.

        Args:
            before: Current state or problem
            after: Desired end state or vision
            bridge: How to get from before → after
            timeline: Optional time constraints
        """
        super().__init__(before=before, after=after, bridge=bridge, timeline=timeline)
        self.before = before
        self.after = after
        self.bridge = bridge
        self.timeline = timeline

    def format(self, user_input: str) -> str:
        """Generate BAB-structured prompt."""
        prompt = f"""BEFORE (Current State):
{self.before}

AFTER (Desired Outcome):
{self.after}

BRIDGE (How to Get There):
{self.bridge}"""

        if self.timeline:
            prompt += f"\n\nTimeline: {self.timeline}"

        prompt += f"""

Context:
{user_input}

Based on the above, provide a detailed transformation plan."""

        return prompt.strip()
