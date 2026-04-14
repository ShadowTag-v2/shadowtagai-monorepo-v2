import os
import sys
from datetime import timedelta

from temporalio import activity, workflow

# Ensure libs path is discoverable for swarm integration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


@activity.defn
async def execute_swarm_agent(task_payload: str) -> str:
    """Activity: Imports the global steel swarm orchestrator and executes the job.
    """
    from libs.steel.swarm import SwarmOrchestrator

    orchestrator = SwarmOrchestrator()
    # Jetski should automatically register on import from our previous patch

    # Swarm logic is synchronous in the prototype
    result = orchestrator.route_and_execute(task_payload)
    return result


@workflow.defn
class SwarmWorkflow:
    @workflow.run
    async def run(self, task_payload: str) -> str:
        """Durable workflow to execute agents
        """
        # Schedule the activity out to the Worker nodes
        return await workflow.execute_activity(
            execute_swarm_agent,
            task_payload,
            start_to_close_timeout=timedelta(seconds=60),
            # Retry policy defaults to robust backoff
        )
