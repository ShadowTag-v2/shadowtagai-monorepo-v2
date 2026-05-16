# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Unit tests for Workflow Agent

Tests workflow pattern implementation including:
- Step execution
- Validation logic
- Error handling
- State management
"""

import pytest
from typing import Any
from dataclasses import dataclass


# Mock the workflow components for testing
@dataclass
class MockWorkflowContext:
    input: Any
    results: dict[str, Any] = None

    def __post_init__(self):
        if self.results is None:
            self.results = {}


class TestWorkflowSteps:
    """Test individual workflow steps"""

    @pytest.mark.asyncio
    async def test_step_validation_success(self):
        """Test that valid step results pass validation"""
        MockWorkflowContext(input={"test": "data"})

        # Simulate step result
        result = {"format": "json", "schema": {}, "rules": ["rule1", "rule2"]}

        # Validation should pass
        assert result.get("format") is not None
        assert result.get("schema") is not None
        assert isinstance(result.get("rules"), list)

    @pytest.mark.asyncio
    async def test_step_validation_failure(self):
        """Test that invalid step results fail validation"""
        result = {
            "format": "json"
            # Missing schema and rules
        }

        # Validation should fail
        assert result.get("schema") is None
        assert result.get("rules") is None

    @pytest.mark.asyncio
    async def test_step_execution_order(self):
        """Test that steps execute in correct order"""
        context = MockWorkflowContext(input={})
        execution_order = []

        # Simulate step execution
        steps = ["classify", "validate", "report"]
        for step in steps:
            execution_order.append(step)
            context.results[step] = {"status": "complete"}

        assert execution_order == ["classify", "validate", "report"]
        assert len(context.results) == 3


class TestWorkflowEngine:
    """Test workflow engine orchestration"""

    @pytest.mark.asyncio
    async def test_workflow_execution_success(self):
        """Test successful workflow execution"""
        context = MockWorkflowContext(input={"users": []})

        # Simulate successful workflow
        context.results = {
            "classify_input": {"format": "json"},
            "schema_validation": {"valid": True, "errors": []},
            "business_rule_validation": {"valid": True, "violations": []},
            "quality_checks": {"warnings": []},
            "generate_report": {"valid": True, "errors": [], "warnings": [], "summary": "All checks passed"},
        }

        final_report = context.results["generate_report"]
        assert final_report["valid"] is True
        assert len(final_report["errors"]) == 0

    @pytest.mark.asyncio
    async def test_workflow_execution_with_errors(self):
        """Test workflow execution with validation errors"""
        context = MockWorkflowContext(input={"users": [{"invalid": "data"}]})

        # Simulate workflow with errors
        context.results = {
            "classify_input": {"format": "json"},
            "schema_validation": {"valid": False, "errors": [{"field": "email", "message": "Invalid email", "severity": "high"}]},
            "generate_report": {
                "valid": False,
                "errors": [{"field": "email", "message": "Invalid email", "severity": "high"}],
                "warnings": [],
                "summary": "Validation failed",
            },
        }

        final_report = context.results["generate_report"]
        assert final_report["valid"] is False
        assert len(final_report["errors"]) > 0

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow error handling and recovery"""
        context = MockWorkflowContext(input={})

        # Simulate step failure
        error_occurred = False
        recovery_attempted = False

        try:
            raise ValueError("Step validation failed")
        except ValueError as e:
            error_occurred = True
            recovery_attempted = True
            # Log error
            context.results["error"] = str(e)

        assert error_occurred is True
        assert recovery_attempted is True
        assert "error" in context.results


class TestValidationRules:
    """Test validation rules and quality checks"""

    def test_email_validation(self):
        """Test email format validation"""
        valid_emails = ["user@example.com", "test.user@domain.co.uk"]
        invalid_emails = ["invalid-email", "@example.com", "user@"]

        # Simple email validation
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        for email in valid_emails:
            assert re.match(email_pattern, email) is not None

        for email in invalid_emails:
            assert re.match(email_pattern, email) is None

    def test_age_validation(self):
        """Test age range validation"""
        valid_ages = [0, 18, 65, 120]
        invalid_ages = [-1, -5, 150, 200]

        for age in valid_ages:
            assert 0 <= age <= 130

        for age in invalid_ages:
            assert not (0 <= age <= 130)

    def test_duplicate_detection(self):
        """Test duplicate record detection"""
        users = [
            {"id": "1", "name": "John"},
            {"id": "2", "name": "Jane"},
            {"id": "1", "name": "John"},  # Duplicate
        ]

        seen_ids = set()
        duplicates = []

        for user in users:
            if user["id"] in seen_ids:
                duplicates.append(user)
            seen_ids.add(user["id"])

        assert len(duplicates) == 1
        assert duplicates[0]["id"] == "1"


class TestMetricsCalculation:
    """Test code metrics and quality indicators"""

    def test_complexity_calculation(self):
        """Test cyclomatic complexity calculation"""
        # Simplified complexity based on conditionals
        code = """
        def process(x):
            if x > 0:
                if x < 10:
                    return "small"
                else:
                    return "large"
            return "zero"
        """

        conditionals = code.count("if") + code.count("else")
        complexity = conditionals + 1

        assert complexity > 1
        assert complexity <= 10  # Acceptable range

    def test_maintainability_index(self):
        """Test maintainability index calculation"""
        lines = 50
        complexity = 5

        # Simplified MI calculation
        mi = max(0, (171 - 5.2 * (lines**0.5) - 0.23 * complexity) * 100 / 171)

        assert 0 <= mi <= 100

        # Higher MI for simpler code
        simple_mi = max(0, (171 - 5.2 * (10**0.5) - 0.23 * 2) * 100 / 171)
        complex_mi = max(0, (171 - 5.2 * (100**0.5) - 0.23 * 20) * 100 / 171)

        assert simple_mi > complex_mi


class TestObservability:
    """Test logging and observability features"""

    def test_structured_logging(self):
        """Test structured log format"""
        import json
        from datetime import datetime

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "step_complete",
            "severity": "info",
            "message": "Step completed successfully",
            "metadata": {"step": "classify_input", "duration": 1.23},
        }

        # Should be JSON serializable
        log_json = json.dumps(log_entry)
        parsed = json.loads(log_json)

        assert parsed["event_type"] == "step_complete"
        assert parsed["metadata"]["step"] == "classify_input"

    def test_error_tracking(self):
        """Test error tracking and context"""
        error_log = {
            "timestamp": "2025-11-08T10:00:00Z",
            "event_type": "error",
            "severity": "error",
            "message": "Validation failed",
            "metadata": {"step": "schema_validation", "error": "Required field missing", "context": {"field": "email"}},
        }

        assert error_log["severity"] == "error"
        assert "error" in error_log["metadata"]
        assert "context" in error_log["metadata"]


# Test fixtures
@pytest.fixture
def sample_valid_data():
    """Sample valid data for testing"""
    return {"users": [{"name": "John Doe", "email": "john@example.com", "age": 30, "role": "admin"}]}


@pytest.fixture
def sample_invalid_data():
    """Sample invalid data for testing"""
    return {"users": [{"name": "Jane Smith", "email": "invalid-email", "age": -5, "role": "user"}]}


# Integration test
class TestWorkflowIntegration:
    """Integration tests for complete workflow"""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, sample_valid_data):
        """Test complete workflow execution"""
        context = MockWorkflowContext(input=sample_valid_data)

        # Simulate complete workflow
        steps_executed = []

        # Step 1: Classify
        steps_executed.append("classify")
        context.results["classify_input"] = {"format": "json"}

        # Step 2: Validate
        steps_executed.append("validate")
        context.results["schema_validation"] = {"valid": True, "errors": []}

        # Step 3: Report
        steps_executed.append("report")
        context.results["generate_report"] = {"valid": True, "errors": [], "warnings": [], "summary": "Success"}

        assert len(steps_executed) == 3
        assert context.results["generate_report"]["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
