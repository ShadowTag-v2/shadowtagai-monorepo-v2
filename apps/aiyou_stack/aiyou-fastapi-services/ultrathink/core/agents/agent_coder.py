"""
AgentCoder: Producer-Tester-Optimizer for code generation.

Three specialized agents collaborate:
- Producer: Writes code
- Tester: Creates & runs tests
- Optimizer: Refines for performance/quality

Philosophy: Separation of concerns > single-pass generation.
"""

from typing import Literal

from pydantic import BaseModel, Field


class CodeIteration(BaseModel):
    """Single iteration of code generation/refinement."""

    iteration: int
    code: str
    tests: list[str]
    test_results: dict[str, bool] = Field(description="test_name -> passed")
    optimizations: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(
        default_factory=dict, description="Coverage, complexity, etc."
    )


class AgentCoderResult(BaseModel):
    """Result of AgentCoder process."""

    iterations: list[CodeIteration]
    final_code: str
    final_tests: list[str]
    pass_rate: float = Field(ge=0.0, le=1.0)
    total_iterations: int
    metadata: dict = Field(default_factory=dict)


class AgentCoder:
    """
    AgentCoder: Multi-agent code generation.

    Usage:
        >>> coder = AgentCoder(max_iterations=5, test_coverage_target=0.9)
        >>> result = coder.generate(
        ...     "Write a function to calculate Fibonacci sequence efficiently"
        ... )
        >>> print(result.final_code)
        >>> print(f"Pass rate: {result.pass_rate:.1%}")

    Research results (HumanEval benchmark):
        - 96.3% pass@1 (vs. ~85% for single-agent GPT-4)
        - Lower token cost than iterative refinement
        - Specialization > generalization for code tasks

    Best for:
        - Functions with clear test criteria
        - Performance-critical code
        - When you need high reliability
    """

    def __init__(
        self,
        max_iterations: int = 5,
        test_coverage_target: float = 0.9,
        optimization_focus: Literal["speed", "memory", "readability"] = "readability",
    ) -> None:
        """
        Initialize AgentCoder.

        Args:
            max_iterations: Max refinement cycles
            test_coverage_target: Stop when coverage >= this (0-1)
            optimization_focus: What to optimize for
        """
        self.max_iterations = max_iterations
        self.test_coverage_target = test_coverage_target
        self.optimization_focus = optimization_focus

    def format_producer_prompt(self, task: str, feedback: str | None = None) -> str:
        """Generate prompt for code producer agent."""
        prompt = f"""You are the Producer agent in AgentCoder.
Your job: Write clean, correct code.

Task:
{task}"""

        if feedback:
            prompt += f"""

Test feedback from Tester:
{feedback}

Optimizer suggestions:
{feedback}

Refine the code to address the issues above."""

        else:
            prompt += "\n\nWrite the initial implementation using Chain-of-Thought reasoning."

        return prompt.strip()

    def format_tester_prompt(self, task: str, code: str) -> str:
        """Generate prompt for test designer agent."""
        prompt = f"""You are the Tester agent in AgentCoder.
Your job: Create comprehensive tests.

Original task:
{task}

Code to test:
```python
{code}
```

Create tests covering:
1. Basic functionality (happy path)
2. Edge cases (empty inputs, boundaries, etc.)
3. Large-scale stress tests

Target coverage: {self.test_coverage_target:.0%}

Output format: List of pytest test functions."""

        return prompt.strip()

    def format_optimizer_prompt(self, code: str, test_results: dict) -> str:
        """Generate prompt for optimizer agent."""
        prompt = f"""You are the Optimizer agent in AgentCoder.
Your job: Improve code quality.

Code:
```python
{code}
```

Test results: {test_results}

Optimization focus: {self.optimization_focus}

Analyze:
- Time complexity
- Space complexity
- Code readability
- Potential bugs

Suggest specific improvements."""

        return prompt.strip()

    def generate(
        self,
        task: str,
        model: any | None = None,
        temperature: float = 0.3,
    ) -> AgentCoderResult:
        """
        Generate code using multi-agent collaboration.

        Args:
            task: Code generation task
            model: Optional model instance
            temperature: Lower for code generation

        Returns:
            AgentCoderResult with iterations and final code
        """
        # Placeholder implementation
        # In production:
        # 1. Producer generates initial code
        # 2. Tester creates tests and runs them
        # 3. If tests fail or coverage < target:
        #    a. Optimizer suggests improvements
        #    b. Producer refines code
        #    c. Repeat
        # 4. Return final code + tests

        result = AgentCoderResult(
            iterations=[
                CodeIteration(
                    iteration=1,
                    code="def fibonacci(n): pass  # Placeholder",
                    tests=["test_basic", "test_edge_cases"],
                    test_results={"test_basic": False, "test_edge_cases": False},
                    optimizations=[],
                    metrics={"coverage": 0.0, "complexity": 0},
                )
            ],
            final_code="# Final code placeholder",
            final_tests=[],
            pass_rate=0.0,
            total_iterations=1,
            metadata={
                "technique": "AgentCoder",
                "max_iterations": self.max_iterations,
                "optimization_focus": self.optimization_focus,
            },
        )

        return result

    def __repr__(self) -> str:
        return (
            f"AgentCoder(max_iterations={self.max_iterations}, "
            f"test_coverage_target={self.test_coverage_target}, "
            f"optimization_focus={self.optimization_focus!r})"
        )
