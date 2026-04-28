# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass
from typing import Any


@dataclass
class CurriculumTask:
    iteration: int
    difficulty: float
    scenario: dict[str, Any]
    expected_violation: bool


class CurriculumAgent:
    """Generates violation scenarios to test the governance rules."""

    def __init__(self, model_client=None):
        self.model_client = model_client
        self.history: list[CurriculumTask] = []

    def generate_task(self, iteration: int, difficulty: float) -> CurriculumTask:
        """Generates a new task (violation scenario).
        In a real impl, this calls the LLM.
        For POC, we'll return a template-based scenario.
        """
        # Stub implementation for POC
        scenario = {
            "action": "database_write",
            "resource": "users_table",
            "data": {"pii": True, "encryption": not difficulty < 0.5},
            "user_role": "admin" if difficulty > 0.7 else "user",
        }

        # If difficulty is low, we make obvious violations (no encryption)
        # If difficulty is high, we make subtle ones (admin user but wrong scope)

        expected_violation = True  # Simplified for POC

        task = CurriculumTask(
            iteration=iteration,
            difficulty=difficulty,
            scenario=scenario,
            expected_violation=expected_violation,
        )
        self.history.append(task)
        return task

    def feedback(self, task: CurriculumTask, executor_success: bool):
        """Receives feedback on whether the Executor caught the violation."""
