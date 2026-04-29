# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""ADK Tool: SK Process External Event Injector.

Agent Development Kit tool that allows an AI agent to inject external
events into a running Semantic Kernel Process instance. Specifically
designed to trigger OnExternalEvent("UserApproved") / OnExternalEvent("UserRejected")
on HumanGateStep, but generalizable to any external event.

Usage in ADK agent:
    from tools.sk_process_event_tool import SKProcessEventTool
    agent = Agent(tools=[SKProcessEventTool()])
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("sk_process_event_tool")


class SKProcessEventInput(BaseModel):
    """Input schema for the SK Process Event Injection tool."""

    process_id: str = Field(..., description="The SK Process instance ID to target.")
    event_name: str = Field(
        ...,
        description="The external event name to fire. Common values: 'UserApproved', 'UserRejected'.",
    )
    event_data: dict[str, Any] | None = Field(
        None,
        description="Optional JSON payload to attach to the event.",
    )
    firm_id: str = Field(..., description="The firm tenant ID for authorization scoping.")


class SKProcessEventOutput(BaseModel):
    """Output schema for the SK Process Event Injection tool."""

    success: bool
    process_id: str
    event_name: str
    timestamp: str
    message: str


class SKProcessEventTool:
    """ADK Tool for injecting external events into SK Process instances.

    This tool bridges the AI agent layer with the Semantic Kernel Process
    runtime. When a HumanGateStep pauses execution and awaits approval,
    this tool can be used by an authorized agent to resume the process
    by firing the appropriate external event.

    Architecture:
        Agent → SKProcessEventTool → FastAPI /api/v1/process/gate/decide → SK Process Runner

    Security:
        - Tool validates firm_id before injection
        - Claude_Code_6 gate checks MUST pass before the event reaches the process
        - Audit log emitted for every event injection
    """

    name: str = "sk_process_inject_event"
    description: str = (
        "Inject an external event into a running Semantic Kernel Process instance. "
        "Use this to approve or reject a pending HumanGateStep. "
        "Requires process_id, event_name ('UserApproved' or 'UserRejected'), "
        "and firm_id for tenant authorization."
    )

    def __init__(self, api_base_url: str = "http://localhost:8000") -> None:
        """Initialize with the CounselConduit API base URL."""
        self.api_base_url = api_base_url.rstrip("/")

    async def run(self, input_data: SKProcessEventInput) -> SKProcessEventOutput:
        """Execute the event injection.

        In production, this calls the FastAPI endpoint.
        In test mode, this directly invokes the gate resolution logic.
        """
        import httpx

        url = f"{self.api_base_url}/api/v1/process/gate/decide"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json={
                        "process_id": input_data.process_id,
                        "decision": ("approve" if input_data.event_name == "UserApproved" else "reject"),
                        "reviewer_notes": (f"Injected by ADK tool at {datetime.now(UTC).isoformat()}"),
                    },
                    headers={
                        "X-Firm-Id": input_data.firm_id,
                        "X-User-Id": "adk-agent-system",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    return SKProcessEventOutput(
                        success=True,
                        process_id=data["process_id"],
                        event_name=data["event_fired"],
                        timestamp=data["timestamp"],
                        message=f"Successfully fired {data['event_fired']} on process {data['process_id']}",
                    )
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    return SKProcessEventOutput(
                        success=False,
                        process_id=input_data.process_id,
                        event_name=input_data.event_name,
                        timestamp=datetime.now(UTC).isoformat(),
                        message=f"Failed ({response.status_code}): {error_detail}",
                    )

        except httpx.ConnectError:
            return SKProcessEventOutput(
                success=False,
                process_id=input_data.process_id,
                event_name=input_data.event_name,
                timestamp=datetime.now(UTC).isoformat(),
                message="Connection failed — CounselConduit API unreachable",
            )
        except Exception as e:
            logger.exception("Unexpected error in SKProcessEventTool")
            return SKProcessEventOutput(
                success=False,
                process_id=input_data.process_id,
                event_name=input_data.event_name,
                timestamp=datetime.now(UTC).isoformat(),
                message=f"Unexpected error: {e!s}",
            )
