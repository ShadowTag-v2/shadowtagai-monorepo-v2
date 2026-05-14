#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Corrected Vertex AI Orchestrator with Safety Improvements

CRITICAL FIXES APPLIED:
1. Fixed Vertex AI SDK usage to match actual API
2. Changed from code execution to structured JSON plan generation
3. Removed unsafe execute_sandboxed (was stub with pass)
4. Added proper error handling and validation
5. Fixed CustomTrainingJob parameters
6. Added sandboxing guidance (do NOT execute untrusted code)

SECURITY NOTE:
- This orchestrator generates PLANS (JSON), not executable code
- If you need to execute model-generated logic, use a separate sandboxed environment
- Recommended: Use gVisor, Firejail, or containerized sandbox with:
  - Read-only filesystem
  - No network access
  - Resource limits (CPU, memory, time)
  - Syscall filtering (seccomp)
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Vertex AI imports
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, GenerationConfig
    from google.cloud import aiplatform
except ImportError:
    print("ERROR: Missing required packages. Install with:")
    print("pip install google-cloud-aiplatform")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class OrchestrationPlan:
    """Structured orchestration plan from Gemini"""

    steps: list[dict[str, Any]]
    validation_rules: list[str]
    estimated_duration_seconds: int
    resource_requirements: dict[str, Any]


class COROrchestrator:
    """
    Cascade Orchestration & Reasoning (COR) Orchestrator

    Uses Gemini to generate structured orchestration plans for multi-layer
    inference systems. Returns JSON plans that are validated and executed
    through pre-approved code paths.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-001",
    ):
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Initialize Vertex AI
        logger.info(f"Initializing Vertex AI: project={project_id}, location={location}")
        vertexai.init(project=project_id, location=location)

        # Initialize Gemini model
        self.model = GenerativeModel(model_name)
        logger.info(f"Initialized Gemini model: {model_name}")

    def generate_orchestration_plan(self, task_description: str, context: dict[str, Any] | None = None) -> OrchestrationPlan:
        """
        Generate a structured orchestration plan (NOT executable code)

        Args:
            task_description: Description of the orchestration task
            context: Optional context (current state, metrics, etc.)

        Returns:
            OrchestrationPlan with validated structure
        """
        # Build prompt for structured plan generation
        prompt = self._build_plan_prompt(task_description, context)

        # Configure generation parameters
        generation_config = GenerationConfig(
            temperature=0.1,  # Low temperature for deterministic plans
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
            response_mime_type="application/json",  # Request JSON response
        )

        try:
            logger.info("Requesting orchestration plan from Gemini...")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            # Parse JSON response
            plan_data = json.loads(response.text)
            logger.info("Received plan from Gemini")

            # Validate and structure the plan
            plan = self._validate_plan(plan_data)
            return plan

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            raise ValueError(f"Invalid JSON in model response: {e}")
        except Exception as e:
            logger.error(f"Failed to generate orchestration plan: {e}")
            raise

    def _build_plan_prompt(self, task_description: str, context: dict[str, Any] | None) -> str:
        """Build prompt for plan generation"""

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"

        return f"""You are an orchestration planner for a multi-layer AI inference system.
Generate a structured orchestration plan in JSON format.

Task: {task_description}{context_str}

Return ONLY a JSON object with this exact structure:
{{
  "steps": [
    {{
      "action": "call_service",
      "service": "judge6-layer1",
      "method": "POST",
      "endpoint": "/infer",
      "payload": {{"key": "value"}},
      "timeout_ms": 100,
      "retry_policy": {{"max_attempts": 3, "backoff_ms": 100}}
    }},
    {{
      "action": "wait_for",
      "metric": "p99_latency",
      "threshold": 50,
      "duration_seconds": 10
    }},
    {{
      "action": "aggregate",
      "sources": ["layer1_result", "layer2_result"],
      "strategy": "consensus"
    }}
  ],
  "validation_rules": [
    "p99_latency < 50ms",
    "error_rate < 0.01",
    "all_layers_healthy"
  ],
  "estimated_duration_seconds": 30,
  "resource_requirements": {{
    "cpu_cores": 4,
    "memory_gb": 8,
    "gpu_count": 1
  }}
}}

Valid action types: call_service, wait_for, aggregate, validate, branch
Do not include any explanatory text, only the JSON object.
"""

    def _validate_plan(self, plan_data: dict[str, Any]) -> OrchestrationPlan:
        """Validate plan structure and return typed object"""

        # Validate required fields
        required_fields = ["steps", "validation_rules", "estimated_duration_seconds", "resource_requirements"]
        for field in required_fields:
            if field not in plan_data:
                raise ValueError(f"Missing required field in plan: {field}")

        # Validate steps
        if not isinstance(plan_data["steps"], list) or len(plan_data["steps"]) == 0:
            raise ValueError("Plan must contain at least one step")

        # Validate each step has required fields
        valid_actions = {"call_service", "wait_for", "aggregate", "validate", "branch"}
        for i, step in enumerate(plan_data["steps"]):
            if "action" not in step:
                raise ValueError(f"Step {i} missing 'action' field")
            if step["action"] not in valid_actions:
                raise ValueError(f"Step {i} has invalid action: {step['action']}")

        return OrchestrationPlan(
            steps=plan_data["steps"],
            validation_rules=plan_data["validation_rules"],
            estimated_duration_seconds=plan_data["estimated_duration_seconds"],
            resource_requirements=plan_data["resource_requirements"],
        )

    def execute_plan(self, plan: OrchestrationPlan) -> dict[str, Any]:
        """
        Execute a validated orchestration plan

        IMPORTANT: This executes plans through PRE-APPROVED code paths only.
        Never execute arbitrary code generated by the model.
        """
        logger.info(f"Executing orchestration plan with {len(plan.steps)} steps")
        results = []

        for i, step in enumerate(plan.steps):
            logger.info(f"Executing step {i + 1}/{len(plan.steps)}: {step['action']}")

            try:
                # Execute through pre-approved handlers
                result = self._execute_step(step)
                results.append({"step": i, "action": step["action"], "status": "success", "result": result})
            except Exception as e:
                logger.error(f"Step {i} failed: {e}")
                results.append({"step": i, "action": step["action"], "status": "error", "error": str(e)})
                # Decide whether to continue or abort
                # For now, abort on first error
                break

        return {"plan_id": id(plan), "total_steps": len(plan.steps), "executed_steps": len(results), "results": results}

    def _execute_step(self, step: dict[str, Any]) -> Any:
        """Execute a single step through pre-approved handlers"""

        action = step["action"]

        if action == "call_service":
            return self._call_service(step)
        elif action == "wait_for":
            return self._wait_for_metric(step)
        elif action == "aggregate":
            return self._aggregate_results(step)
        elif action == "validate":
            return self._validate_condition(step)
        else:
            raise ValueError(f"Unsupported action: {action}")

    def _call_service(self, step: dict[str, Any]) -> dict[str, Any]:
        """Call a service (stub - implement with actual HTTP client)"""
        logger.info(f"Calling service: {step.get('service')}")
        # TODO: Implement with requests/httpx with proper timeouts
        return {"status": "called", "service": step.get("service")}

    def _wait_for_metric(self, step: dict[str, Any]) -> dict[str, Any]:
        """Wait for a metric to reach threshold (stub)"""
        logger.info(f"Waiting for metric: {step.get('metric')}")
        # TODO: Implement with actual metrics monitoring
        return {"status": "metric_ready", "metric": step.get("metric")}

    def _aggregate_results(self, step: dict[str, Any]) -> dict[str, Any]:
        """Aggregate results from multiple sources (stub)"""
        logger.info(f"Aggregating results: {step.get('sources')}")
        # TODO: Implement aggregation logic
        return {"status": "aggregated", "strategy": step.get("strategy")}

    def _validate_condition(self, step: dict[str, Any]) -> dict[str, Any]:
        """Validate a condition (stub)"""
        logger.info(f"Validating condition: {step.get('condition')}")
        # TODO: Implement validation logic
        return {"status": "validated", "condition": step.get("condition")}


def deploy_to_vertex_training(
    project_id: str,
    location: str,
    display_name: str,
    container_image_uri: str,
    machine_type: str = "n1-standard-4",
    accelerator_type: str | None = None,
    accelerator_count: int = 0,
) -> str:
    """
    Deploy orchestrator as a Vertex AI Custom Training Job

    FIXED: Corrected parameters to match actual API
    """

    logger.info("Initializing Vertex AI Platform...")
    aiplatform.init(project=project_id, location=location)

    # Build worker pool specs
    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": machine_type,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": container_image_uri,
                "command": ["python", "/app/orchestrator.py"],
                "args": ["--mode=production"],
            },
        }
    ]

    # Add accelerator if specified
    if accelerator_type and accelerator_count > 0:
        worker_pool_specs[0]["machine_spec"]["accelerator_type"] = accelerator_type
        worker_pool_specs[0]["machine_spec"]["accelerator_count"] = accelerator_count

    logger.info(f"Creating CustomJob: {display_name}")

    # Create custom job
    job = aiplatform.CustomJob(
        display_name=display_name,
        worker_pool_specs=worker_pool_specs,
        base_output_dir=f"gs://{project_id}-training-output/orchestrator",
    )

    logger.info("Submitting job to Vertex AI...")
    job.run(
        sync=False,  # Run asynchronously
        service_account=f"judge6@{project_id}.iam.gserviceaccount.com",
    )

    logger.info(f"Job submitted: {job.resource_name}")
    return job.resource_name


def main():
    """Main execution"""

    # Get configuration from environment
    project_id = os.getenv("PROJECT_ID", "pnkln-core-stack")
    location = os.getenv("VERTEX_LOCATION", "us-central1")

    logger.info("=== COR Orchestrator Demo ===")

    # Example 1: Generate orchestration plan
    orchestrator = COROrchestrator(project_id=project_id, location=location)

    task = """
    Create an orchestration plan for a 3-layer inference cascade:
    1. Layer 1: Gemini model for initial classification (p99 < 30ms)
    2. Layer 2: Aggregate results and apply ATP519 rules
    3. Layer 3: Final enforcement and response formatting

    Ensure p99 end-to-end latency stays under 50ms.
    """

    context = {"current_p99": 45, "error_rate": 0.005, "available_gpu": True}

    try:
        plan = orchestrator.generate_orchestration_plan(task, context)
        logger.info(f"Generated plan with {len(plan.steps)} steps")
        logger.info(f"Estimated duration: {plan.estimated_duration_seconds}s")

        # Print plan
        print("\n=== Generated Orchestration Plan ===")
        print(
            json.dumps(
                {
                    "steps": plan.steps,
                    "validation_rules": plan.validation_rules,
                    "estimated_duration_seconds": plan.estimated_duration_seconds,
                    "resource_requirements": plan.resource_requirements,
                },
                indent=2,
            )
        )

        # Execute plan (with stubs for now)
        logger.info("\n=== Executing Plan ===")
        results = orchestrator.execute_plan(plan)
        print(json.dumps(results, indent=2))

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        sys.exit(1)

    # Example 2: Deploy to Vertex AI Training (commented out)
    # Uncomment to deploy as a training job
    """
    job_name = deploy_to_vertex_training(
        project_id=project_id,
        location=location,
        display_name="judge6-orchestrator-v1",
        container_image_uri=f"gcr.io/{project_id}/judge6-orchestrator:latest",
        machine_type="n1-standard-4",
        accelerator_type="NVIDIA_TESLA_T4",
        accelerator_count=1,
    )
    logger.info(f"Deployed to Vertex AI: {job_name}")
    """

    logger.info("\n✓ Orchestration complete")


if __name__ == "__main__":
    main()
