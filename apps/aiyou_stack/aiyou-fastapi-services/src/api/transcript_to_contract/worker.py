import asyncio
import logging

from lancedb_engine import physical_ingest
from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker
from upload_workflow import LanceDBIngestionWorkflow

logging.basicConfig(level=logging.INFO)


@activity.defn(name="ingest_to_lancedb")
async def ingest_to_lancedb(filename: str, content_size: int) -> str:
    logging.info(f"Worker routing {filename} chunks into Sovereign PyArrow Matrix...")
    physical_ingest(filename, content_size)
    logging.info(f"Sovereign Ingestion Complete: {content_size} bytes indexed in LanceDB.")
    return "SUCCESS_VECTORIZED"


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="omega-swarm-queue",
        workflows=[LanceDBIngestionWorkflow],
        activities=[ingest_to_lancedb],
    )
    logging.info("Temporal LanceDB Worker Matrix Online.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
