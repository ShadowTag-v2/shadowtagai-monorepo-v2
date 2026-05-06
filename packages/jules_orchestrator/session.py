# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Jules Session orchestration layer.

Handles polling, plan approval, and telemetry integration.
"""

import time
import logging
from typing import Any, Callable

from .client import JulesClient, JulesAPIError
from agnt_bash_classifier.telemetry import BashTelemetryTracker

logger = logging.getLogger(__name__)


class JulesSession:
    """Represents a lifecycle-managed Jules Session."""

    def __init__(
        self,
        client: JulesClient,
        source_name: str,
        automation_mode: str = "AUTO_CREATE_PR",
        task_description: str = "",
        session_name: str | None = None,
    ) -> None:
        """Initialize a new or existing Jules Session."""
        self.client = client
        self.source_name = source_name
        self.automation_mode = automation_mode
        self.task_description = task_description
        
        self.session_name = session_name
        self.session_data: dict[str, Any] = {}
        self.telemetry = BashTelemetryTracker()

    def start(self) -> dict[str, Any]:
        """Start the session if not already started."""
        if not self.session_name:
            logger.info("Creating Jules session for %s", self.source_name)
            try:
                self.session_data = self.client.create_session(
                    source_name=self.source_name,
                    automation_mode=self.automation_mode,
                    task_description=self.task_description,
                )
                self.session_name = self.session_data.get("name")
                if self.session_name:
                    self.telemetry.track_jules_session_created(
                        self.source_name, self.session_name, self.automation_mode
                    )
            except JulesAPIError as e:
                self.telemetry.track_jules_api_error("/sessions", str(e))
                raise
        return self.session_data

    def get_status(self) -> str:
        """Get the current session status."""
        if not self.session_name:
            return "UNINITIALIZED"
        self.session_data = self.client.get_session(self.session_name)
        return self.session_data.get("state", "UNKNOWN")

    def approve_plan(self, message: str = "") -> dict[str, Any]:
        """Approve the pending plan."""
        if not self.session_name:
            raise JulesAPIError("Session not initialized.")
        logger.info("Approving plan for %s", self.session_name)
        try:
            result = self.client.approve_plan(self.session_name, message=message)
            self.telemetry.track_jules_plan_approved(self.session_name)
            return result
        except JulesAPIError as e:
            self.telemetry.track_jules_api_error(f"/{self.session_name}:approvePlan", str(e))
            raise
        
    def interact(self, text: str) -> dict[str, Any]:
        """Send interaction message to Jules."""
        if not self.session_name:
            raise JulesAPIError("Session not initialized.")
        return self.client.interact(self.session_name, text)

    def run_auto_pr_workflow(
        self,
        plan_approval_callback: Callable[[dict[str, Any]], bool] | None = None,
        timeout: int = 600,
        interval: int = 10,
    ) -> dict[str, Any]:
        """Execute the complete AUTO_CREATE_PR workflow.
        
        This will create the session, poll until a plan is ready, optionally 
        invoke a callback to approve the plan, and poll until completion.
        """
        self.start()
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status()
            
            if status == "NEEDS_APPROVAL":
                logger.info("Session %s needs approval.", self.session_name)
                approved = True
                if plan_approval_callback:
                    approved = plan_approval_callback(self.session_data)
                
                if approved:
                    self.approve_plan("Approved via auto PR workflow")
                else:
                    logger.warning("Plan rejected for %s", self.session_name)
                    return self.session_data
            elif status in ("COMPLETED", "FAILED"):
                logger.info("Session %s reached terminal state: %s", self.session_name, status)
                return self.session_data
            
            time.sleep(interval)
            
        raise JulesAPIError(f"Workflow timeout after {timeout} seconds")
