"""Framework-based Reasoning Skill

Apply structured frameworks to problems (SWOT, 5 Whys, First Principles, etc.)

Example (5 Whys):
  Problem: Website is slow
    Why? Server response time is high
    Why? Database queries are slow
    Why? No indexes on frequently queried columns
    Why? Schema wasn't optimized initially
    Why? Launched MVP without performance testing
  Root cause: Need performance testing in development cycle

Frameworks supported:
- SWOT (Strengths, Weaknesses, Opportunities, Threats)
- 5 Whys (Root cause analysis)
- First Principles (Break down to fundamental truths)
- STAR (Situation, Task, Action, Result)
- Eisenhower Matrix (Urgent/Important prioritization)
"""

import time
from enum import Enum
from typing import Any

from .base import Skill, SkillResult


class Framework(Enum):
    """Available reasoning frameworks"""

    SWOT = "swot"  # Strengths, Weaknesses, Opportunities, Threats
    FIVE_WHYS = "5whys"  # Root cause analysis
    FIRST_PRINCIPLES = "first_principles"  # Fundamental truths
    STAR = "star"  # Situation, Task, Action, Result
    EISENHOWER = "eisenhower"  # Urgent/Important matrix


class FrameworkReasoning(Skill):
    """Framework-based reasoning skill

    Apply structured thinking frameworks to problems
    """

    def __init__(
        self,
        name: str = "FrameworkReasoning",
        description: str = "Apply structured frameworks (SWOT, 5 Whys, etc.)",
        initial_rating: float = 1550.0,
        model: str = "gemini-3.1-flash-lite-preview",
        default_framework: Framework = Framework.FIRST_PRINCIPLES,
    ):
        # CheatSheet for Framework reasoning
        cheatsheet = """
# Framework Reasoning CheatSheet

## Available Frameworks

### SWOT Analysis
**Structure:**
- Strengths: Internal advantages
- Weaknesses: Internal disadvantages
- Opportunities: External factors to exploit
- Threats: External risks

### 5 Whys
**Structure:**
1. Problem statement
2. Why? (First cause)
3. Why? (Deeper cause)
4. Why? (Deeper still)
5. Why? (Root cause)

### First Principles
**Structure:**
1. Identify assumptions
2. Break down to fundamental truths
3. Rebuild from scratch

### STAR
**Structure:**
- Situation: Context
- Task: What needed to be done
- Action: What you did
- Result: Outcome

### Eisenhower Matrix
**Structure:**
- Urgent + Important: Do first
- Important, Not Urgent: Schedule
- Urgent, Not Important: Delegate
- Neither: Eliminate

## Selection Guide
- **Strategic planning** → SWOT
- **Problem diagnosis** → 5 Whys
- **Innovation** → First Principles
- **Storytelling** → STAR
- **Prioritization** → Eisenhower
"""

        super().__init__(
            name=name,
            description=description,
            initial_rating=initial_rating,
            cheatsheet=cheatsheet,
        )

        self.model = model
        self.default_framework = default_framework

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> SkillResult:
        """Execute framework-based reasoning

        Args:
            task: Problem to solve
            context: Must include 'framework' (Framework enum)

        Returns:
            SkillResult with framework-structured reasoning

        """
        start_time = time.time()

        # Get framework from context
        framework = (
            context.get("framework", self.default_framework) if context else self.default_framework
        )

        if isinstance(framework, str):
            framework = Framework(framework)

        # Apply framework
        if framework == Framework.SWOT:
            result = await self._apply_swot(task)
        elif framework == Framework.FIVE_WHYS:
            result = await self._apply_5whys(task)
        elif framework == Framework.FIRST_PRINCIPLES:
            result = await self._apply_first_principles(task)
        elif framework == Framework.STAR:
            result = await self._apply_star(task)
        elif framework == Framework.EISENHOWER:
            result = await self._apply_eisenhower(task)
        else:
            raise ValueError(f"Unknown framework: {framework}")

        latency_ms = (time.time() - start_time) * 1000

        return SkillResult(
            output=result["output"],
            reasoning_trace=result["trace"],
            confidence=result["confidence"],
            tokens_used=self._estimate_tokens(task, framework),
            latency_ms=latency_ms,
            metadata={"skill": "FrameworkReasoning", "framework": framework.value},
        )

    async def _apply_swot(self, task: str) -> dict[str, Any]:
        """Apply SWOT analysis"""
        # Mock implementation
        return {
            "output": "SWOT Analysis complete",
            "trace": [
                "Strengths: [Identified internal advantages]",
                "Weaknesses: [Identified internal disadvantages]",
                "Opportunities: [Identified external opportunities]",
                "Threats: [Identified external threats]",
            ],
            "confidence": 0.85,
        }

    async def _apply_5whys(self, task: str) -> dict[str, Any]:
        """Apply 5 Whys root cause analysis"""
        return {
            "output": "Root cause identified",
            "trace": [
                "Problem: [Initial problem statement]",
                "Why 1: [First cause]",
                "Why 2: [Second cause]",
                "Why 3: [Third cause]",
                "Why 4: [Fourth cause]",
                "Why 5 (Root): [Root cause identified]",
            ],
            "confidence": 0.80,
        }

    async def _apply_first_principles(self, task: str) -> dict[str, Any]:
        """Apply First Principles thinking"""
        return {
            "output": "First principles solution",
            "trace": [
                "Step 1: Identify assumptions in current approach",
                "Step 2: Break down to fundamental truths",
                "Step 3: Question each assumption",
                "Step 4: Rebuild from fundamentals",
                "Step 5: Novel solution derived",
            ],
            "confidence": 0.90,
        }

    async def _apply_star(self, task: str) -> dict[str, Any]:
        """Apply STAR storytelling"""
        return {
            "output": "STAR narrative complete",
            "trace": [
                "Situation: [Context and background]",
                "Task: [What needed to be accomplished]",
                "Action: [Specific actions taken]",
                "Result: [Measurable outcomes]",
            ],
            "confidence": 0.85,
        }

    async def _apply_eisenhower(self, task: str) -> dict[str, Any]:
        """Apply Eisenhower Matrix prioritization"""
        return {
            "output": "Prioritization complete",
            "trace": [
                "Quadrant 1 (Urgent + Important): [Do immediately]",
                "Quadrant 2 (Important, Not Urgent): [Schedule]",
                "Quadrant 3 (Urgent, Not Important): [Delegate]",
                "Quadrant 4 (Neither): [Eliminate]",
            ],
            "confidence": 0.75,
        }

    def _estimate_tokens(self, task: str, framework: Framework) -> int:
        """Estimate tokens based on framework complexity"""
        base_tokens = len(task) // 4

        framework_tokens = {
            Framework.SWOT: 800,
            Framework.FIVE_WHYS: 600,
            Framework.FIRST_PRINCIPLES: 1000,
            Framework.STAR: 700,
            Framework.EISENHOWER: 750,
        }

        return base_tokens + framework_tokens.get(framework, 800)


# Example usage
async def example():
    """Example: Apply First Principles to a problem"""
    framework_skill = FrameworkReasoning(default_framework=Framework.FIRST_PRINCIPLES)

    result = await framework_skill.execute(
        "How can we reduce cloud costs by 50% without affecting performance?",
        context={"framework": Framework.FIRST_PRINCIPLES},
    )

    print(f"Solution:\n{result.output}\n")
    print("Framework reasoning:")
    for step in result.reasoning_trace:
        print(f"  • {step}")
    print(f"\nFramework: {result.metadata['framework']}")
    print(f"Confidence: {result.confidence:.1%}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example())
