import asyncio
from datetime import timedelta

from temporalio import workflow

# Import activity stubs
with workflow.unsafe.imports_passed_through():
    from activities import fetch_connections, index_connection


@workflow.defn
class IndexingWorkflow:
    @workflow.run
    async def run(self, workspace_id: str):
        workflow.logger.info(f"Starting Indexing Workflow for {workspace_id}")

        # 1. Fetch Connections
        connections = await workflow.execute_activity(
            fetch_connections,
            workspace_id,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 2. Fan-out / Parallel Execution
        # Launch indexing for all connections found
        futures = []
        for connection in connections:
            futures.append(
                workflow.execute_activity(
                    index_connection,
                    connection,
                    start_to_close_timeout=timedelta(minutes=30),
                )
            )

        # Wait for all to complete
        await asyncio.gather(*futures)

        workflow.logger.info("Indexing Workflow Completed.")
        return "Done"
