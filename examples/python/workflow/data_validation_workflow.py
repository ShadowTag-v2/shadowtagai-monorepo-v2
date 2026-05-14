# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Workflow Pattern Reference Implementation

This example demonstrates a production-ready workflow agent for data validation.
Key features:
- Deterministic execution path
- Comprehensive error handling
- Full observability
- Self-validation
"""

from claude_agent_sdk import query, ClaudeAgentOptions
from typing import List, Dict, Any, Optional
from collections.abc import Callable
from dataclasses import dataclass, field
import json
import time

# ==================== Types ====================


@dataclass
class StepResult:
    step: str
    success: bool
    duration: float
    error: str | None = None


@dataclass
class WorkflowContext:
    input: Any
    results: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=lambda: {"start_time": time.time(), "step_results": []})


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str


@dataclass
class ValidationWarning:
    field: str
    message: str


@dataclass
class ValidationReport:
    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    summary: str


@dataclass
class WorkflowStep:
    name: str
    execute: Callable[[WorkflowContext], Any]
    validate: Callable[[Any], bool]
    on_error: Callable[[Exception, WorkflowContext], Any] | None = None


# ==================== System Prompt ====================

WORKFLOW_SYSTEM_PROMPT = """
<agent_configuration>
  <metadata>
    <agent_name>Data Validation Workflow</agent_name>
    <pattern>workflow</pattern>
    <version>1.0.0</version>
  </metadata>

  <role>
You are a data validation agent that processes user submissions through
a defined validation pipeline. You follow a strict, deterministic workflow
to ensure data quality and compliance.
  </role>

  <workflow_definition>
Step 1: CLASSIFY INPUT TYPE
- Identify data format (CSV, JSON, XML, etc.)
- Determine validation rules to apply
- Select appropriate schema

Step 2: SCHEMA VALIDATION
- Validate against predefined schema
- Check required fields
- Verify data types

Step 3: BUSINESS RULE VALIDATION
- Apply domain-specific rules
- Check constraints and relationships
- Validate calculations

Step 4: QUALITY CHECKS
- Check for duplicates
- Validate data ranges
- Verify referential integrity

Step 5: GENERATE REPORT
- Compile validation results
- List all errors and warnings
- Provide remediation guidance
  </workflow_definition>

  <quality_standards>
Every validation must:
- Process all records (no partial failures)
- Generate comprehensive error reports
- Complete within 30 seconds for <10MB files
- Achieve 100% rule coverage
  </quality_standards>

  <constraints>
Must NOT:
- Skip validation steps
- Proceed with invalid data
- Make assumptions about missing fields

Must:
- Log every step and decision
- Provide clear, actionable error messages
- Maintain data integrity
  </constraints>
</agent_configuration>
"""

# ==================== Helper Function ====================


async def query_agent(prompt: str, max_tokens: int = 2000) -> str:
    """Query the agent and return result"""
    result = None
    async for message in query(
        prompt=prompt, options=ClaudeAgentOptions(system_prompt=WORKFLOW_SYSTEM_PROMPT, max_tokens=max_tokens, model="claude-sonnet-4.5-20250514")
    ):
        result = message
    return result


# ==================== Workflow Steps ====================


async def classify_input_execute(context: WorkflowContext) -> dict[str, Any]:
    """Step 1: Classify input type"""
    print("[Step 1] Classifying input type...")

    result = await query_agent(
        f"""
Analyze this data and determine:
1. Data format (JSON, CSV, XML, etc.)
2. Schema structure
3. Appropriate validation rules

Data:
{json.dumps(context.input, indent=2)}

Return a JSON object with: {{ "format": string, "schema": object, "rules": string[] }}
    """,
        max_tokens=2000,
    )

    return json.loads(result)


def classify_input_validate(result: Any) -> bool:
    """Validate classification result"""
    return result and "format" in result and "schema" in result and "rules" in result and isinstance(result["rules"], list)


classify_input_step = WorkflowStep(name="classify_input", execute=classify_input_execute, validate=classify_input_validate)


async def schema_validation_execute(context: WorkflowContext) -> dict[str, Any]:
    """Step 2: Validate against schema"""
    print("[Step 2] Validating against schema...")

    schema = context.results["classify_input"]["schema"]

    result = await query_agent(
        f"""
Validate this data against the schema:

Data:
{json.dumps(context.input, indent=2)}

Schema:
{json.dumps(schema, indent=2)}

Check:
1. All required fields present
2. Data types match schema
3. Value constraints satisfied

Return JSON: {{ "valid": boolean, "errors": Array<{{field, message, severity}}> }}
    """,
        max_tokens=3000,
    )

    return json.loads(result)


def schema_validation_validate(result: Any) -> bool:
    """Validate schema validation result"""
    return result and "valid" in result and isinstance(result["valid"], bool) and "errors" in result and isinstance(result["errors"], list)


schema_validation_step = WorkflowStep(name="schema_validation", execute=schema_validation_execute, validate=schema_validation_validate)


async def business_rule_validation_execute(context: WorkflowContext) -> dict[str, Any]:
    """Step 3: Apply business rules"""
    print("[Step 3] Applying business rules...")

    rules = context.results["classify_input"]["rules"]

    result = await query_agent(
        f"""
Apply these business rules to the data:

Data:
{json.dumps(context.input, indent=2)}

Rules:
{chr(10).join(rules)}

Validate each rule and return:
{{ "valid": boolean, "violations": Array<{{rule, field, message}}> }}
    """,
        max_tokens=3000,
    )

    return json.loads(result)


def business_rule_validation_validate(result: Any) -> bool:
    """Validate business rule result"""
    return result and "valid" in result and isinstance(result["valid"], bool) and "violations" in result and isinstance(result["violations"], list)


business_rule_validation_step = WorkflowStep(
    name="business_rule_validation", execute=business_rule_validation_execute, validate=business_rule_validation_validate
)


async def quality_checks_execute(context: WorkflowContext) -> dict[str, Any]:
    """Step 4: Run quality checks"""
    print("[Step 4] Running quality checks...")

    result = await query_agent(
        f"""
Perform quality checks on this data:

{json.dumps(context.input, indent=2)}

Check for:
1. Duplicate records
2. Data range validation
3. Referential integrity
4. Data consistency

Return: {{ "warnings": Array<{{field, message, type}}> }}
    """,
        max_tokens=2000,
    )

    return json.loads(result)


def quality_checks_validate(result: Any) -> bool:
    """Validate quality checks result"""
    return result and "warnings" in result and isinstance(result["warnings"], list)


quality_checks_step = WorkflowStep(name="quality_checks", execute=quality_checks_execute, validate=quality_checks_validate)


async def generate_report_execute(context: WorkflowContext) -> dict[str, Any]:
    """Step 5: Generate validation report"""
    print("[Step 5] Generating validation report...")

    schema_errors = context.results["schema_validation"]["errors"]
    business_violations = context.results["business_rule_validation"]["violations"]
    quality_warnings = context.results["quality_checks"]["warnings"]

    result = await query_agent(
        f"""
Generate a comprehensive validation report.

Schema Errors:
{json.dumps(schema_errors, indent=2)}

Business Rule Violations:
{json.dumps(business_violations, indent=2)}

Quality Warnings:
{json.dumps(quality_warnings, indent=2)}

Create a report with:
1. Executive summary
2. Critical issues (must fix)
3. Warnings (should fix)
4. Recommendations
5. Overall validation status

Return JSON: {{
  "valid": boolean,
  "errors": Array<{{field, message, severity}}>,
  "warnings": Array<{{field, message}}>,
  "summary": string
}}
    """,
        max_tokens=4000,
    )

    return json.loads(result)


def generate_report_validate(result: Any) -> bool:
    """Validate report generation result"""
    return result and "valid" in result and isinstance(result["valid"], bool) and "summary" in result


generate_report_step = WorkflowStep(name="generate_report", execute=generate_report_execute, validate=generate_report_validate)

# ==================== Workflow Engine ====================


class WorkflowEngine:
    """Execute workflow steps in sequence"""

    def __init__(self, steps: list[WorkflowStep]):
        self.steps = steps

    async def execute(self, input_data: Any) -> ValidationReport:
        """Execute all workflow steps"""
        context = WorkflowContext(input=input_data)

        for step in self.steps:
            step_start_time = time.time()

            try:
                print(f"\n=== Executing: {step.name} ===")

                result = await step.execute(context)

                if not step.validate(result):
                    raise ValueError(f"Validation failed for step: {step.name}")

                context.results[step.name] = result

                duration = time.time() - step_start_time
                context.metadata["step_results"].append(StepResult(step=step.name, success=True, duration=duration))

                print(f"✓ {step.name} completed in {duration:.2f}s")

            except Exception as error:
                duration = time.time() - step_start_time

                print(f"✗ {step.name} failed: {str(error)}")

                context.metadata["step_results"].append(StepResult(step=step.name, success=False, duration=duration, error=str(error)))

                if step.on_error:
                    print(f"Attempting error recovery for {step.name}...")
                    await step.on_error(error, context)
                else:
                    raise

        total_duration = time.time() - context.metadata["start_time"]
        print(f"\n=== Workflow completed in {total_duration:.2f}s ===")

        report_data = context.results["generate_report"]
        return ValidationReport(
            valid=report_data["valid"],
            errors=[ValidationError(**e) for e in report_data["errors"]],
            warnings=[ValidationWarning(**w) for w in report_data["warnings"]],
            summary=report_data["summary"],
        )


# ==================== Main ====================


async def main():
    """Main execution function"""
    # Example input data with issues
    test_data = {
        "users": [
            {"name": "John Doe", "email": "john@example.com", "age": 30, "role": "admin"},
            {
                "name": "Jane Smith",
                "email": "invalid-email",  # Invalid email
                "age": -5,  # Invalid age
                "role": "user",
            },
            {
                "name": "John Doe",  # Duplicate
                "email": "john@example.com",
                "age": 30,
                "role": "admin",
            },
        ]
    }

    # Create and execute workflow
    workflow = WorkflowEngine([classify_input_step, schema_validation_step, business_rule_validation_step, quality_checks_step, generate_report_step])

    try:
        report = await workflow.execute(test_data)

        print("\n=== VALIDATION REPORT ===")
        print(f"Valid: {report.valid}")
        print(f"Summary: {report.summary}")
        print(f"\nErrors ({len(report.errors)}):")
        for error in report.errors:
            print(f"  - {error.field}: {error.message} [{error.severity}]")
        print(f"\nWarnings ({len(report.warnings)}):")
        for warning in report.warnings:
            print(f"  - {warning.field}: {warning.message}")

        if report.valid:
            print("\n✓ Data is valid and ready for processing")
        else:
            print("\n✗ Data validation failed")

    except Exception as error:
        print(f"\n✗ Workflow execution failed: {str(error)}")
        raise


# Run if executed directly
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
