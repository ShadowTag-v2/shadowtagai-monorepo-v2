# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Benchmark Harness - Standard Evaluation Suite

Framework for running standard code generation and software engineering
benchmarks to evaluate agent performance.

Supported Benchmarks:
- HumanEval: Python code generation (164 problems)
- BigCodeBench: Real-world coding tasks
- SWE-bench: Software engineering tasks (bug fixing, feature implementation)

Performance Baselines:
- HumanEval pass@1: ≥70% (production target)
- BigCodeBench pass@1: ≥50% (production target)
- SWE-bench pass@1: ≥30% (production target)

References:
- "Evaluating Large Language Models Trained on Code" (Chen et al., 2021)
- "BigCodeBench: Benchmarking Code Generation with Diverse Function Calls"
- "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"

"""

import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BenchmarkType(Enum):
    """Benchmark types."""

    HUMANEVAL = "humaneval"
    BIGCODEBENCH = "bigcodebench"
    SWEBENCH = "swebench"


class DifficultyLevel(Enum):
    """Problem difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class BenchmarkProblem:
    """Single benchmark problem.

    Attributes:
        problem_id: Unique problem identifier
        benchmark: Benchmark type
        difficulty: Problem difficulty
        description: Problem description/prompt
        test_cases: List of test cases
        canonical_solution: Reference solution (if available)
        metadata: Additional metadata

    """

    problem_id: str
    benchmark: BenchmarkType
    difficulty: DifficultyLevel
    description: str
    test_cases: list[dict[str, Any]]
    canonical_solution: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Solution:
    """Agent-generated solution.

    Attributes:
        problem_id: Problem identifier
        solution_code: Generated code
        generation_time_ms: Time to generate solution
        agent_id: Agent identifier
        metadata: Additional metadata

    """

    problem_id: str
    solution_code: str
    generation_time_ms: float
    agent_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """Test execution result.

    Attributes:
        problem_id: Problem identifier
        passed: Whether all tests passed
        num_passed: Number of tests passed
        num_total: Total number of tests
        execution_time_ms: Test execution time
        error_message: Error message (if failed)

    """

    problem_id: str
    passed: bool
    num_passed: int
    num_total: int
    execution_time_ms: float
    error_message: str | None = None


@dataclass
class BenchmarkResult:
    """Complete benchmark result.

    Attributes:
        benchmark: Benchmark type
        agent_id: Agent identifier
        problems_attempted: Number of problems attempted
        problems_passed: Number of problems passed
        pass_at_1: Pass@1 score (0.0-1.0)
        pass_at_k: Pass@k scores for different k values
        avg_generation_time_ms: Average solution generation time
        total_execution_time_ms: Total benchmark execution time
        results_by_difficulty: Results broken down by difficulty
        failed_problems: List of failed problem IDs

    """

    benchmark: BenchmarkType
    agent_id: str
    problems_attempted: int
    problems_passed: int
    pass_at_1: float
    pass_at_k: dict[int, float]
    avg_generation_time_ms: float
    total_execution_time_ms: float
    results_by_difficulty: dict[DifficultyLevel, dict[str, float]]
    failed_problems: list[str]


class BenchmarkHarness:
    """Standard evaluation suite for code generation.

    Performance baselines:
    - HumanEval pass@1: ≥70%
    - BigCodeBench pass@1: ≥50%
    - SWE-bench pass@1: ≥30%
    """

    def __init__(self):
        """Initialize benchmark harness."""
        # Problem sets (would load from files in production)
        self.problems: dict[BenchmarkType, list[BenchmarkProblem]] = {
            BenchmarkType.HUMANEVAL: [],
            BenchmarkType.BIGCODEBENCH: [],
            BenchmarkType.SWEBENCH: [],
        }

        # Baseline scores for comparison
        self.baselines = {
            BenchmarkType.HUMANEVAL: 0.70,  # 70% pass@1
            BenchmarkType.BIGCODEBENCH: 0.50,  # 50% pass@1
            BenchmarkType.SWEBENCH: 0.30,  # 30% pass@1
        }

    def load_humaneval(self) -> list[BenchmarkProblem]:
        """Load HumanEval benchmark problems.

        In production, would load from HumanEval dataset.
        Here we create sample problems for demonstration.

        Returns:
            List of HumanEval problems

        """
        problems = [
            BenchmarkProblem(
                problem_id="HumanEval/0",
                benchmark=BenchmarkType.HUMANEVAL,
                difficulty=DifficultyLevel.EASY,
                description=(
                    "Write a function that returns True if a given number is prime.\n\n"
                    "def is_prime(n: int) -> bool:\n"
                    "    '''Returns True if n is prime, False otherwise.'''\n"
                ),
                test_cases=[
                    {"input": 2, "expected": True},
                    {"input": 3, "expected": True},
                    {"input": 4, "expected": False},
                    {"input": 17, "expected": True},
                    {"input": 1, "expected": False},
                ],
                canonical_solution=(
                    "def is_prime(n: int) -> bool:\n"
                    "    if n < 2:\n"
                    "        return False\n"
                    "    for i in range(2, int(n ** 0.5) + 1):\n"
                    "        if n % i == 0:\n"
                    "            return False\n"
                    "    return True\n"
                ),
            ),
            BenchmarkProblem(
                problem_id="HumanEval/1",
                benchmark=BenchmarkType.HUMANEVAL,
                difficulty=DifficultyLevel.MEDIUM,
                description=(
                    "Write a function that returns the nth Fibonacci number.\n\n"
                    "def fibonacci(n: int) -> int:\n"
                    "    '''Returns the nth Fibonacci number (0-indexed).'''\n"
                ),
                test_cases=[
                    {"input": 0, "expected": 0},
                    {"input": 1, "expected": 1},
                    {"input": 5, "expected": 5},
                    {"input": 10, "expected": 55},
                ],
                canonical_solution=(
                    "def fibonacci(n: int) -> int:\n"
                    "    if n <= 1:\n"
                    "        return n\n"
                    "    a, b = 0, 1\n"
                    "    for _ in range(n - 1):\n"
                    "        a, b = b, a + b\n"
                    "    return b\n"
                ),
            ),
        ]

        self.problems[BenchmarkType.HUMANEVAL] = problems
        return problems

    def load_bigcodebench(self) -> list[BenchmarkProblem]:
        """Load BigCodeBench problems (sample)."""
        problems = [
            BenchmarkProblem(
                problem_id="BigCodeBench/0",
                benchmark=BenchmarkType.BIGCODEBENCH,
                difficulty=DifficultyLevel.MEDIUM,
                description=(
                    "Implement a function to parse JSON and extract all email addresses.\n"
                    "Return a list of unique email addresses."
                ),
                test_cases=[
                    {
                        "input": '{"user": "redacted@shadowtag-v4.local", "admin": "redacted@shadowtag-v4.local"}',
                        "expected": ["redacted@shadowtag-v4.local", "redacted@shadowtag-v4.local"],
                    },
                ],
            ),
        ]

        self.problems[BenchmarkType.BIGCODEBENCH] = problems
        return problems

    def load_swebench(self) -> list[BenchmarkProblem]:
        """Load SWE-bench problems (sample)."""
        problems = [
            BenchmarkProblem(
                problem_id="SWE-bench/0",
                benchmark=BenchmarkType.SWEBENCH,
                difficulty=DifficultyLevel.HARD,
                description=(
                    "Fix the bug in the following code that causes incorrect sorting:\n"
                    "def sort_list(items):\n"
                    "    return sorted(items, reverse=False)\n\n"
                    "The function should sort in descending order by default."
                ),
                test_cases=[{"input": [3, 1, 4, 1, 5], "expected": [5, 4, 3, 1, 1]}],
                canonical_solution=(
                    "def sort_list(items):\n    return sorted(items, reverse=True)\n"
                ),
            ),
        ]

        self.problems[BenchmarkType.SWEBENCH] = problems
        return problems

    async def _execute_tests(self, solution: Solution, problem: BenchmarkProblem) -> TestResult:
        """Execute tests for a solution.

        In production, would use proper sandboxed execution.

        Args:
            solution: Generated solution
            problem: Problem specification

        Returns:
            Test execution result

        """
        start_time = time.time()

        passed_count = 0
        total_count = len(problem.test_cases)
        error_msg = None

        try:
            # In production, would execute solution code safely
            # Here we simulate test execution
            for _test_case in problem.test_cases:
                # Simulate test execution (90% pass rate for demo)
                import random

                if random.random() < 0.9:
                    passed_count += 1

        except Exception as e:
            error_msg = str(e)

        execution_time_ms = (time.time() - start_time) * 1000
        passed = passed_count == total_count

        return TestResult(
            problem_id=problem.problem_id,
            passed=passed,
            num_passed=passed_count,
            num_total=total_count,
            execution_time_ms=execution_time_ms,
            error_message=error_msg,
        )

    async def evaluate(
        self,
        benchmark: BenchmarkType,
        agent_id: str,
        solution_generator: Callable[[BenchmarkProblem], str],
        max_problems: int | None = None,
    ) -> BenchmarkResult:
        """Evaluate agent on benchmark.

        Args:
            benchmark: Benchmark to run
            agent_id: Agent identifier
            solution_generator: Function to generate solutions
            max_problems: Maximum problems to evaluate (None = all)

        Returns:
            Benchmark result

        """
        start_time = time.time()

        # Load problems
        if benchmark == BenchmarkType.HUMANEVAL:
            problems = self.load_humaneval()
        elif benchmark == BenchmarkType.BIGCODEBENCH:
            problems = self.load_bigcodebench()
        else:  # SWEBENCH
            problems = self.load_swebench()

        if max_problems:
            problems = problems[:max_problems]

        # Generate and test solutions
        solutions = []
        test_results = []

        for problem in problems:
            # Generate solution
            gen_start = time.time()
            solution_code = await solution_generator(problem)
            gen_time_ms = (time.time() - gen_start) * 1000

            solution = Solution(
                problem_id=problem.problem_id,
                solution_code=solution_code,
                generation_time_ms=gen_time_ms,
                agent_id=agent_id,
            )
            solutions.append(solution)

            # Execute tests
            test_result = await self._execute_tests(solution, problem)
            test_results.append(test_result)

        # Compute metrics
        problems_attempted = len(problems)
        problems_passed = sum(1 for r in test_results if r.passed)
        pass_at_1 = problems_passed / problems_attempted if problems_attempted > 0 else 0.0

        # Pass@k metrics (k=1,5,10)
        pass_at_k = {
            1: pass_at_1,
            5: min(pass_at_1 * 1.15, 1.0),  # Simulated pass@5
            10: min(pass_at_1 * 1.25, 1.0),  # Simulated pass@10
        }

        # By difficulty
        results_by_difficulty = {}
        for difficulty in DifficultyLevel:
            difficulty_problems = [p for p in problems if p.difficulty == difficulty]
            if difficulty_problems:
                difficulty_results = [
                    r
                    for r in test_results
                    if any(p.problem_id == r.problem_id for p in difficulty_problems)
                ]
                passed = sum(1 for r in difficulty_results if r.passed)
                total = len(difficulty_results)

                results_by_difficulty[difficulty] = {
                    "attempted": total,
                    "passed": passed,
                    "pass_rate": passed / total if total > 0 else 0.0,
                }

        # Failed problems
        failed_problems = [r.problem_id for r in test_results if not r.passed]

        # Average generation time
        avg_gen_time = statistics.mean(s.generation_time_ms for s in solutions)

        total_time_ms = (time.time() - start_time) * 1000

        return BenchmarkResult(
            benchmark=benchmark,
            agent_id=agent_id,
            problems_attempted=problems_attempted,
            problems_passed=problems_passed,
            pass_at_1=pass_at_1,
            pass_at_k=pass_at_k,
            avg_generation_time_ms=avg_gen_time,
            total_execution_time_ms=total_time_ms,
            results_by_difficulty=results_by_difficulty,
            failed_problems=failed_problems,
        )

    def compare_to_baseline(self, result: BenchmarkResult) -> dict[str, Any]:
        """Compare result to baseline.

        Args:
            result: Benchmark result

        Returns:
            Comparison statistics

        """
        baseline = self.baselines.get(result.benchmark, 0.5)

        delta = result.pass_at_1 - baseline
        delta_pct = (delta / baseline * 100) if baseline > 0 else 0.0

        meets_baseline = result.pass_at_1 >= baseline

        return {
            "pass_at_1": result.pass_at_1,
            "baseline": baseline,
            "delta": delta,
            "delta_pct": delta_pct,
            "meets_baseline": meets_baseline,
            "rank": "EXCELLENT"
            if result.pass_at_1 > baseline * 1.2
            else "GOOD"
            if result.pass_at_1 > baseline
            else "BELOW_BASELINE",
        }

    def get_statistics(self) -> dict[str, Any]:
        """Get harness statistics.

        Returns:
            Dictionary with statistics

        """
        return {
            "benchmarks_available": len(self.problems),
            "total_problems": sum(len(probs) for probs in self.problems.values()),
            "humaneval_problems": len(self.problems[BenchmarkType.HUMANEVAL]),
            "bigcodebench_problems": len(self.problems[BenchmarkType.BIGCODEBENCH]),
            "swebench_problems": len(self.problems[BenchmarkType.SWEBENCH]),
            "baselines": {b.value: score for b, score in self.baselines.items()},
        }
