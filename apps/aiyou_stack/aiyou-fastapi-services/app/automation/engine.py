"""Workflow execution engine for running automation workflows."""

import asyncio
import logging
import traceback
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.automation import JobExecution, JobStatus, Workflow

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Engine for executing automation workflows."""

    def __init__(self):
        self.action_handlers = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default action handlers."""
        self.action_handlers = {
            "http_request": self._execute_http_request,
            "delay": self._execute_delay,
            "log": self._execute_log,
            "condition": self._execute_condition,
            "transform": self._execute_transform,
        }

    def register_handler(self, action_type: str, handler):
        """Register a custom action handler.

        Args:
            action_type: The type of action to handle
            handler: Async function that takes (action_config, context) and returns result

        """
        self.action_handlers[action_type] = handler

    async def execute_workflow(
        self,
        workflow_id: int,
        input_data: dict[str, Any] | None = None,
        scheduled_job_id: int | None = None,
        trigger_id: int | None = None,
    ) -> JobExecution:
        """Execute a workflow and track the execution.

        Args:
            workflow_id: ID of the workflow to execute
            input_data: Input data for the workflow
            scheduled_job_id: ID of the scheduled job (if applicable)
            trigger_id: ID of the trigger (if applicable)

        Returns:
            JobExecution instance with execution results

        """
        async with AsyncSessionLocal() as session:
            # Create job execution record
            execution = JobExecution(
                workflow_id=workflow_id,
                scheduled_job_id=scheduled_job_id,
                trigger_id=trigger_id,
                input_data=input_data or {},
                status=JobStatus.PENDING,
            )
            session.add(execution)
            await session.commit()
            await session.refresh(execution)

            try:
                # Get workflow
                result = await session.execute(select(Workflow).where(Workflow.id == workflow_id))
                workflow = result.scalar_one_or_none()

                if not workflow:
                    raise ValueError(f"Workflow {workflow_id} not found")

                # Update status to running
                execution.status = JobStatus.RUNNING
                execution.started_at = datetime.utcnow()
                await session.commit()

                # Execute workflow
                logger.info(f"Executing workflow {workflow_id}: {workflow.name}")
                output = await self._execute_workflow_definition(
                    workflow.definition,
                    input_data or {},
                )

                # Mark as successful
                execution.status = JobStatus.SUCCESS
                execution.output_data = output
                execution.completed_at = datetime.utcnow()
                execution.duration_seconds = int(
                    (execution.completed_at - execution.started_at).total_seconds(),
                )

                logger.info(f"Workflow {workflow_id} completed successfully")

            except Exception as e:
                # Mark as failed
                execution.status = JobStatus.FAILED
                execution.error_message = str(e)
                execution.error_traceback = traceback.format_exc()
                execution.completed_at = datetime.utcnow()

                if execution.started_at:
                    execution.duration_seconds = int(
                        (execution.completed_at - execution.started_at).total_seconds(),
                    )

                logger.error(f"Workflow {workflow_id} failed: {e}\n{execution.error_traceback}")

            finally:
                await session.commit()
                await session.refresh(execution)

            return execution

    async def _execute_workflow_definition(
        self,
        definition: dict[str, Any],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the workflow definition.

        Args:
            definition: Workflow definition dictionary
            input_data: Input data for the workflow

        Returns:
            Output data from workflow execution

        """
        context = {
            "input": input_data,
            "variables": {},
            "output": {},
        }

        # Get workflow steps
        steps = definition.get("steps", [])

        for step in steps:
            action_type = step.get("type")
            action_config = step.get("config", {})
            step_name = step.get("name", action_type)

            logger.info(f"Executing step: {step_name}")

            # Get handler for action type
            handler = self.action_handlers.get(action_type)

            if not handler:
                raise ValueError(f"Unknown action type: {action_type}")

            # Execute action
            result = await handler(action_config, context)

            # Store result in context
            context["variables"][step_name] = result

            # Check if step should stop execution
            if step.get("stop_on_success") and result:
                break

        # Set output
        context["output"] = context["variables"]

        return context["output"]

    async def _execute_http_request(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute an HTTP request action."""
        import httpx

        url = config.get("url")
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        body = config.get("body")
        timeout = config.get("timeout", 30)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body or None,
                timeout=timeout,
            )

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            }

    async def _execute_delay(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a delay action."""
        seconds = config.get("seconds", 1)
        await asyncio.sleep(seconds)
        return {"delayed": seconds}

    async def _execute_log(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute a log action."""
        message = config.get("message", "")
        level = config.get("level", "INFO").upper()

        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message)

        return {"logged": message}

    async def _execute_condition(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a conditional action."""
        condition = config.get("condition")
        if_true = config.get("if_true", {})
        if_false = config.get("if_false", {})

        # Simple condition evaluation (can be expanded)
        result = eval(condition, {"context": context})

        if result:
            return if_true
        return if_false

    async def _execute_transform(
        self,
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a data transformation action."""
        transformation = config.get("transformation", {})
        output = {}

        for key, value in transformation.items():
            # Simple template substitution
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2].strip()
                output[key] = context.get("variables", {}).get(var_name)
            else:
                output[key] = value

        return output


# Global workflow engine instance
workflow_engine = WorkflowEngine()
