"""TDD Red Phase Agent - Hybrid Implementation

Single agent with two internal phases:
1. Test Writing Phase - Generate failing tests
2. Validation Phase - Self-verify against TDD-Guard rules

Eliminates 3-agent circular dependency. One agent, two phases.
"""

import ast
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

# Validation Thresholds (from doctrine)
COMPLIANCE_THRESHOLD = 0.95
MAX_ITERATIONS = 3
TIMEOUT_SECONDS = 90
FAIL_FAST_THRESHOLD = 10


class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


@dataclass
class Violation:
    rule: str
    message: str
    severity: Severity
    line: int | None = None
    test_name: str | None = None


@dataclass
class ComplianceReport:
    passed: bool
    score: float
    violations: list[Violation] = field(default_factory=list)
    tests_analyzed: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    iteration: int = 1
    duration_ms: int = 0


@dataclass
class TestOutput:
    test_code: str
    compliance_report: ComplianceReport
    audit_path: str | None = None


class TDDRedPhaseAgent:
    """Hybrid TDD agent combining test writing with embedded validation.

    Usage:
        agent = TDDRedPhaseAgent()
        result = agent.run(spec="User login validation")
    """

    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self._iteration = 0

    def run(self, spec: str, existing_tests: str | None = None) -> TestOutput:
        """Main entry point. Runs test writing + validation loop.

        Args:
            spec: Feature specification to write tests for
            existing_tests: Optional existing test code to validate/improve

        Returns:
            TestOutput with test code and compliance report

        """
        start_time = time.time()
        test_code = existing_tests or ""

        for iteration in range(1, MAX_ITERATIONS + 1):
            self._iteration = iteration
            elapsed = (time.time() - start_time) * 1000

            # Timeout check
            if elapsed > TIMEOUT_SECONDS * 1000:
                return self._fail_fast(
                    test_code,
                    f"Timeout exceeded: {elapsed:.0f}ms > {TIMEOUT_SECONDS * 1000}ms",
                    int(elapsed),
                )

            # Phase 1: Write/Improve Tests
            if not test_code:
                test_code = self._write_tests(spec)

            # Phase 2: Self-Validate
            report = self._validate(test_code, iteration, int(elapsed))

            # Check compliance
            if report.passed:
                audit_path = self._write_audit_log(report, test_code)
                return TestOutput(
                    test_code=test_code, compliance_report=report, audit_path=audit_path,
                )

            # Fail-fast on too many violations
            if len(report.violations) > FAIL_FAST_THRESHOLD:
                report.passed = False
                audit_path = self._write_audit_log(report, test_code)
                return TestOutput(
                    test_code=test_code, compliance_report=report, audit_path=audit_path,
                )

            # Phase 3: Fix violations and retry
            test_code = self._fix_violations(test_code, report.violations)

        # Escalation: max iterations exceeded
        final_report = self._validate(
            test_code, MAX_ITERATIONS, int((time.time() - start_time) * 1000),
        )
        final_report.passed = False
        audit_path = self._write_audit_log(final_report, test_code, escalated=True)

        return TestOutput(
            test_code=test_code, compliance_report=final_report, audit_path=audit_path,
        )

    def _write_tests(self, spec: str) -> str:
        """Phase 1: Generate failing tests from specification.

        This is where LLM integration would generate tests.
        Returns template for demonstration.
        """
        # Template following TDD-Guard rules
        test_template = f'''"""Tests for: {spec}"""
import pytest


class Test{self._to_class_name(spec)}:
    """Test suite for {spec} functionality."""

    def test_valid_input_returns_success(self):
        """Verify that valid input produces expected success response."""
        # Arrange
        input_data = {{"valid": True}}

        # Act
        result = process(input_data)

        # Assert
        assert result.success is True

    def test_invalid_input_raises_error(self):
        """Verify that invalid input raises appropriate error."""
        # Arrange
        input_data = {{"valid": False}}

        # Act & Assert
        with pytest.raises(ValidationError):
            process(input_data)

    def test_edge_case_empty_input_handled(self):
        """Verify that empty input is handled gracefully."""
        # Arrange
        input_data = {{}}

        # Act
        result = process(input_data)

        # Assert
        assert result.handled is True
'''
        return test_template

    def _validate(self, test_code: str, iteration: int, elapsed_ms: int) -> ComplianceReport:
        """Phase 2: Self-validate against TDD-Guard rules.

        Returns compliance report with pass/fail and violations.
        """
        violations = []
        tests_analyzed = 0

        try:
            tree = ast.parse(test_code)
        except SyntaxError as e:
            violations.append(
                Violation(
                    rule="syntax",
                    message=f"Syntax error: {e}",
                    severity=Severity.CRITICAL,
                    line=e.lineno,
                ),
            )
            return ComplianceReport(
                passed=False,
                score=0.0,
                violations=violations,
                tests_analyzed=0,
                iteration=iteration,
                duration_ms=elapsed_ms,
            )

        # Extract test functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                tests_analyzed += 1
                violations.extend(self._validate_test_function(node, test_code))

        # Calculate compliance score
        if tests_analyzed == 0:
            violations.append(
                Violation(
                    rule="no_tests", message="No test functions found", severity=Severity.CRITICAL,
                ),
            )
            score = 0.0
        else:
            # Weight: critical=3, major=2, minor=1
            penalty = sum(
                3 if v.severity == Severity.CRITICAL else 2 if v.severity == Severity.MAJOR else 1
                for v in violations
            )
            max_score = tests_analyzed * 5  # 5 rules per test
            score = max(0.0, (max_score - penalty) / max_score)

        return ComplianceReport(
            passed=score >= COMPLIANCE_THRESHOLD,
            score=score,
            violations=violations,
            tests_analyzed=tests_analyzed,
            iteration=iteration,
            duration_ms=elapsed_ms,
        )

    def _validate_test_function(self, node: ast.FunctionDef, source: str) -> list[Violation]:
        """Validate a single test function against TDD-Guard rules."""
        violations = []

        # Rule 1: Descriptive name pattern
        if not re.match(r"test_\w+_\w+", node.name):
            violations.append(
                Violation(
                    rule="naming",
                    message=f"Test name '{node.name}' should follow pattern test_<action>_<expected>",
                    severity=Severity.MAJOR,
                    line=node.lineno,
                    test_name=node.name,
                ),
            )

        # Rule 2: Docstring required
        if not ast.get_docstring(node):
            violations.append(
                Violation(
                    rule="docstring",
                    message=f"Test '{node.name}' missing docstring",
                    severity=Severity.MAJOR,
                    line=node.lineno,
                    test_name=node.name,
                ),
            )

        # Rule 3: AAA pattern (check for comments)
        source_lines = source.split("\n")
        func_source = "\n".join(source_lines[node.lineno - 1 : node.end_lineno])
        has_arrange = "# Arrange" in func_source or "# Setup" in func_source
        has_act = "# Act" in func_source
        has_assert = "# Assert" in func_source or "assert" in func_source

        if not (has_arrange or has_act):
            violations.append(
                Violation(
                    rule="aaa_pattern",
                    message=f"Test '{node.name}' should follow Arrange-Act-Assert pattern",
                    severity=Severity.MINOR,
                    line=node.lineno,
                    test_name=node.name,
                ),
            )

        # Rule 4: Has assertions
        has_assertion = any(
            isinstance(stmt, ast.Assert)
            or (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and stmt.value.func.attr in ("assertEqual", "assertTrue", "assertRaises")
            )
            or (isinstance(stmt, ast.With) and "raises" in ast.dump(stmt))
            for stmt in ast.walk(node)
        )

        if not has_assertion and "assert" not in func_source:
            violations.append(
                Violation(
                    rule="no_assertion",
                    message=f"Test '{node.name}' has no assertions",
                    severity=Severity.CRITICAL,
                    line=node.lineno,
                    test_name=node.name,
                ),
            )

        return violations

    def _fix_violations(self, test_code: str, violations: list[Violation]) -> str:
        """Phase 3: Auto-fix violations where possible.

        In production, this would use LLM to intelligently fix.
        Here we apply simple fixes for demonstration.
        """
        lines = test_code.split("\n")

        for violation in violations:
            if violation.severity == Severity.MINOR:
                # Skip minor violations in auto-fix
                continue

            if violation.rule == "docstring" and violation.line:
                # Add placeholder docstring
                indent = len(lines[violation.line - 1]) - len(lines[violation.line - 1].lstrip())
                docstring = " " * (indent + 4) + f'"""Test {violation.test_name}."""'
                lines.insert(violation.line, docstring)

        return "\n".join(lines)

    def _write_audit_log(
        self, report: ComplianceReport, test_code: str, escalated: bool = False,
    ) -> str:
        """Write audit trail for compliance decisions."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audit_path = self.logs_dir / f"tdd-guard-{timestamp}.json"

        audit_data = {
            "timestamp": report.timestamp,
            "iteration": report.iteration,
            "duration_ms": report.duration_ms,
            "passed": report.passed,
            "score": report.score,
            "tests_analyzed": report.tests_analyzed,
            "escalated": escalated,
            "violations": [
                {
                    "rule": v.rule,
                    "message": v.message,
                    "severity": v.severity.value,
                    "line": v.line,
                    "test_name": v.test_name,
                }
                for v in report.violations
            ],
            "test_code_hash": hash(test_code),
            "thresholds": {
                "compliance": COMPLIANCE_THRESHOLD,
                "max_iterations": MAX_ITERATIONS,
                "timeout_seconds": TIMEOUT_SECONDS,
                "fail_fast": FAIL_FAST_THRESHOLD,
            },
        }

        audit_path.write_text(json.dumps(audit_data, indent=2))
        return str(audit_path)

    def _fail_fast(self, test_code: str, reason: str, elapsed_ms: int) -> TestOutput:
        """Generate fail-fast output."""
        report = ComplianceReport(
            passed=False,
            score=0.0,
            violations=[Violation(rule="timeout", message=reason, severity=Severity.CRITICAL)],
            iteration=self._iteration,
            duration_ms=elapsed_ms,
        )
        audit_path = self._write_audit_log(report, test_code)
        return TestOutput(test_code=test_code, compliance_report=report, audit_path=audit_path)

    @staticmethod
    def _to_class_name(spec: str) -> str:
        """Convert spec to PascalCase class name."""
        return "".join(word.capitalize() for word in re.split(r"\W+", spec) if word)


# Convenience function
def run_tdd_red_phase(spec: str, existing_tests: str | None = None) -> TestOutput:
    """Run TDD Red Phase with embedded validation."""
    agent = TDDRedPhaseAgent()
    return agent.run(spec, existing_tests)


if __name__ == "__main__":
    # Demo run

    result = run_tdd_red_phase("User Authentication")
    print(f"Compliance: {result.compliance_report.score:.1%}")
    print(f"Passed: {result.compliance_report.passed}")
    print(f"Audit: {result.audit_path}")
