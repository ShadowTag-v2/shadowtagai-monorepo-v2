# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import sys
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel
from temporalio.client import Client  # Temporal temporalio routing logic

# Add workflows to python path to avoid relative import issues during Temporal execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

router = APIRouter(tags=["Agents"])


class SwarmQuery(BaseModel):
    task: str
    target: str = "swarm"
    context: dict[str, Any] | None = None
    session_id: str | None = None
    priority: int = 1


@router.post("/query")
async def run_swarm_payload(query: SwarmQuery):
    """Invariant #2: Invincible Routing.
    Heavy lift execution payloads are dispatched through temporalio.client.
    """
    task_id = f"st-swarm-{query.target}-1"

    try:
        # Connect to local cluster
        client = await Client.connect("localhost:7233")

        # Execute the swarm logic durably in the worker cluster
        # Using string name to prevent circular imports if necessary, or actual class
        result = await client.execute_workflow(
            "SwarmWorkflow",
            query.task,
            id=task_id,
            task_queue="omega-swarm-queue",
        )
        status = "completed"
        message = result
    except Exception as e:
        status = "failed or dispatched async"
        message = f"Temporal Execution Message: {e}"

    response_payload = {
        "status": status,
        "task_id": task_id,
        "routing": "temporalio.client",
        "message": message,
    }

    return response_payload
