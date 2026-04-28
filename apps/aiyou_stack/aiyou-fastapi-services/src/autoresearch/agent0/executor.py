# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
from typing import Any


class ExecutorAgent:
    """Generates ATP_519_scan detection patterns (Rules) to catch violations."""

    def __init__(self, model_client=None):
        self.model_client = model_client

    def generate_rule(self, task_scenario: dict[str, Any]) -> str:
        """Generates a JSON rule to detect the given scenario.
        In a real impl, this calls the LLM.
        For POC, we'll generate a simple keyword-based rule.
        """
        # Stub implementation for POC
        # It tries to look at the scenario and create a rule that catches it.

        keywords = []
        if task_scenario.get("action"):
            keywords.append(task_scenario["action"])

        data = task_scenario.get("data", {})
        if data.get("pii"):
            keywords.append("pii")
        if data.get("encryption") is False:
            keywords.append("encryption")

        rule = {
            "rule_id": f"rule_{len(keywords)}",
            "keywords": keywords,
            "logic": "OR",  # Simple logic
        }

        return json.dumps(rule)
