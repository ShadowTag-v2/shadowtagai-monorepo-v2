from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    # Simulate DB connections safely
    pass


@workflow.defn
class LanceDBIngestionWorkflow:
    @workflow.run
    async def run(self, filename: str, content_size: int) -> str:
        workflow.logger.info(f"Initiating LanceDB Ingestion for {filename} ({content_size} bytes)")

        # Execute Activity
        status = await workflow.execute_activity(
            "ingest_to_lancedb",
            args=[filename, content_size],
            start_to_close_timeout=timedelta(minutes=5),
        )
        return status
