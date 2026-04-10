"""
Judge #6 - Purpose/Reasons/Brakes Validation Layer

Enforcement layer for function calling that validates every function call
against three criteria:

1. PURPOSE: Does this function call advance the mission?
2. REASONS: Is this function call defensible and logical?
3. BRAKES: Will this function call cause catastrophic failure?

Acts as a kill switch for unsafe or misaligned function executions.
"""

import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from ..core.gemini_function_calling import GeminiFunctionCaller


class ValidationResult(Enum):
    """Result of JR validation."""
    APPROVED = "approved"
    BLOCKED_PURPOSE = "blocked_purpose"
    BLOCKED_REASONS = "blocked_reasons"
    BLOCKED_BRAKES = "blocked_brakes"


@dataclass
class JRValidation:
    """Result of Purpose/Reasons/Brakes validation."""
    function_name: str
    args: dict[str, Any]
    purpose_valid: bool
    purpose_score: float
    reasons_valid: bool
    reasons_score: float
    brakes_clear: bool
    brakes_score: float
    result: ValidationResult
    explanation: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "function_name": self.function_name,
            "args": self.args,
            "purpose_valid": self.purpose_valid,
            "purpose_score": self.purpose_score,
            "reasons_valid": self.reasons_valid,
            "reasons_score": self.reasons_score,
            "brakes_clear": self.brakes_clear,
            "brakes_score": self.brakes_score,
            "result": self.result.value,
            "explanation": self.explanation,
            "timestamp": self.timestamp,
        }


class JudgeSix:
    """
    Judge #6 enforcement layer for function calling.

    Wraps GeminiFunctionCaller with Purpose/Reasons/Brakes validation.

    Example:
        ```python
        # Create base function caller
        caller = GeminiFunctionCaller(tools=tools)

        # Wrap with Judge #6
        judge = JudgeSix(
            caller=caller,
            mission_statement="Research AI topics and generate reports",
            audit_log_path="./logs/jr_audit.log"
        )

        # Execute with validation
        result = judge.enforce("Research quantum computing")
        ```
    """

    def __init__(
        self,
        caller: GeminiFunctionCaller,
        mission_statement: str,
        audit_log_path: str | None = None,
        purpose_threshold: float = 0.6,
        reasons_threshold: float = 0.7,
        brakes_threshold: float = 0.8,
        custom_validators: dict[str, Callable] | None = None,
    ):
        """
        Initialize Judge #6.

        Args:
            caller: Base GeminiFunctionCaller to wrap
            mission_statement: Clear statement of what the system should do
            audit_log_path: Path to audit log file
            purpose_threshold: Minimum score for purpose validation (0-1)
            reasons_threshold: Minimum score for reasons validation (0-1)
            brakes_threshold: Minimum score for brakes validation (0-1)
            custom_validators: Optional custom validation functions
        """
        self.caller = caller
        self.mission_statement = mission_statement
        self.audit_log_path = audit_log_path or os.environ.get(
            'JR_AUDIT_LOG_PATH', './logs/jr_audit.log'
        )
        self.purpose_threshold = purpose_threshold
        self.reasons_threshold = reasons_threshold
        self.brakes_threshold = brakes_threshold
        self.custom_validators = custom_validators or {}

        self.audit_log: list[JRValidation] = []

        # Ensure audit log directory exists
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

    def enforce(self, user_request: str) -> str:
        """
        Execute request with JR validation.

        Args:
            user_request: User's request

        Returns:
            Final response text

        Raises:
            ValueError: If any function call fails validation
        """
        # Create validation callback
        def validate_function_call(fn_name: str, fn_args: dict[str, Any]) -> bool:
            """Validate function call against JR criteria."""
            validation = self._validate(fn_name, fn_args, user_request)

            # Log to audit trail
            self.audit_log.append(validation)
            self._write_audit_log(validation)

            # Block if validation failed
            if validation.result != ValidationResult.APPROVED:
                raise ValueError(
                    f"JR VALIDATION FAILED: {validation.result.value}\n"
                    f"Function: {fn_name}\n"
                    f"Args: {fn_args}\n"
                    f"Explanation: {validation.explanation}"
                )

            return True

        # Execute with validation callback
        return self.caller.execute(
            prompt=user_request,
            validation_callback=validate_function_call
        )

    def _validate(
        self,
        fn_name: str,
        fn_args: dict[str, Any],
        context: str
    ) -> JRValidation:
        """
        Validate function call against Purpose/Reasons/Brakes.

        Args:
            fn_name: Function name
            fn_args: Function arguments
            context: User request context

        Returns:
            JRValidation result
        """
        # 1. PURPOSE: Does this advance the mission?
        purpose_valid, purpose_score = self._validate_purpose(
            fn_name, fn_args, context
        )

        # 2. REASONS: Is this defensible?
        reasons_valid, reasons_score = self._validate_reasons(
            fn_name, fn_args, context
        )

        # 3. BRAKES: Will this cause catastrophe?
        brakes_clear, brakes_score = self._check_brakes(
            fn_name, fn_args, context
        )

        # Determine result
        if not purpose_valid:
            result = ValidationResult.BLOCKED_PURPOSE
            explanation = f"Function '{fn_name}' does not advance mission: {self.mission_statement}"
        elif not reasons_valid:
            result = ValidationResult.BLOCKED_REASONS
            explanation = f"Function '{fn_name}' is not defensible or logical"
        elif not brakes_clear:
            result = ValidationResult.BLOCKED_BRAKES
            explanation = f"Function '{fn_name}' violates safety constraints"
        else:
            result = ValidationResult.APPROVED
            explanation = "All JR validation checks passed"

        return JRValidation(
            function_name=fn_name,
            args=fn_args,
            purpose_valid=purpose_valid,
            purpose_score=purpose_score,
            reasons_valid=reasons_valid,
            reasons_score=reasons_score,
            brakes_clear=brakes_clear,
            brakes_score=brakes_score,
            result=result,
            explanation=explanation,
        )

    def _validate_purpose(
        self,
        fn_name: str,
        fn_args: dict[str, Any],
        context: str
    ) -> tuple[bool, float]:
        """
        Validate PURPOSE: Does this function call advance the mission?
        Uses Gemini 1.5 Flash for rapid semantic validation.

        Returns:
            (is_valid, confidence_score)
        """
        # Custom validator if provided
        if fn_name in self.custom_validators:
            return self.custom_validators[fn_name](fn_name, fn_args, context)

        # Use Gemini for validation
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            You are Judge #6, a governance AI. Validate if the following function call aligns with the Mission.

            Mission: "{self.mission_statement}"
            Context: "{context}"
            Function: {fn_name}
            Arguments: {json.dumps(fn_args)}

            Does this action DIRECTLY advance the mission?
            Respond with JSON only: {{"valid": boolean, "score": float (0.0-1.0), "reason": "string"}}
            """

            response = model.generate_content(prompt)
            result = json.loads(response.text.replace('```json', '').replace('```', ''))

            return result.get('valid', False), result.get('score', 0.0)

        except Exception as e:
            print(f"⚠️ Judge #6 LLM Validation Failed: {e}. Falling back to keyword match.")

            # Fallback: Simple keyword matching
            mission_keywords = set(self.mission_statement.lower().split())
            context_keywords = set(context.lower().split())
            fn_keywords = set(fn_name.lower().split('_'))

            # Calculate overlap
            overlap = len(mission_keywords & (context_keywords | fn_keywords))
            total = len(mission_keywords)
            score = overlap / total if total > 0 else 0.5

            return score >= self.purpose_threshold, score

    def _validate_reasons(
        self,
        fn_name: str,
        fn_args: dict[str, Any],
        context: str
    ) -> tuple[bool, float]:
        """
        Validate REASONS: Is this function call defensible and logical?

        Returns:
            (is_valid, confidence_score)
        """
        # Check if arguments are valid and non-empty
        if not fn_args:
            return False, 0.0

        # Check if arguments make sense (no obviously invalid values)
        for key, value in fn_args.items():
            # Reject empty strings
            if isinstance(value, str) and not value.strip():
                return False, 0.3

            # Reject None values
            if value is None:
                return False, 0.3

        # Arguments seem reasonable
        return True, 0.85

    def _check_brakes(
        self,
        fn_name: str,
        fn_args: dict[str, Any],
        context: str
    ) -> tuple[bool, float]:
        """
        Check BRAKES: Will this function call cause catastrophic failure?

        Returns:
            (is_safe, confidence_score)
        """
        # Define dangerous patterns
        dangerous_keywords = {
            'delete', 'remove', 'drop', 'destroy', 'kill', 'terminate',
            'admin', 'root', 'sudo', 'exec', 'eval', 'system'
        }

        # Check function name
        fn_lower = fn_name.lower()
        if any(keyword in fn_lower for keyword in dangerous_keywords):
            return False, 0.2

        # Check arguments for dangerous patterns
        args_str = json.dumps(fn_args).lower()
        if any(keyword in args_str for keyword in dangerous_keywords):
            return False, 0.3

        # Check for SQL injection patterns
        sql_patterns = ['drop table', 'delete from', '1=1', 'or 1=1']
        if any(pattern in args_str for pattern in sql_patterns):
            return False, 0.1

        # Looks safe
        return True, 0.95

    def _write_audit_log(self, validation: JRValidation):
        """Write validation result to audit log."""
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(validation.to_dict()) + '\n')
        except Exception as e:
            print(f"Warning: Failed to write audit log: {e}")

    def get_audit_log(self) -> list[JRValidation]:
        """Get full audit log."""
        return self.audit_log.copy()

    def get_blocked_calls(self) -> list[JRValidation]:
        """Get all blocked function calls."""
        return [
            v for v in self.audit_log
            if v.result != ValidationResult.APPROVED
        ]
