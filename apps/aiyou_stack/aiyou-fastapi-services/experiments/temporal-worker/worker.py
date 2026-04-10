import asyncio
import logging
import os

from activities import fetch_connections, index_connection
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows and activities
# In a real app, these would be in separate modules as scaffolded below
from workflows import IndexingWorkflow

logging.basicConfig(level=logging.INFO)


async def main():
    # Connect to Temporal Cloud (or local server)
    # Temporal Cloud Address: namespace.tmprl.cloud:7233
    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        api_key=os.getenv("TEMPORAL_API_KEY"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )

    # Initialize Worker
    # This worker polls the 'indexing-queue' task queue
    worker = Worker(
        client,
        task_queue="indexing-queue",
        workflows=[IndexingWorkflow],
        activities=[fetch_connections, index_connection],
    )

    logging.info("Starting Temporal Worker on Cloud Run Worker Pool...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
