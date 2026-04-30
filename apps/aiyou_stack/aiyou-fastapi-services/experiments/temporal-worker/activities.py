import asyncio

from temporalio import activity

# Activities are just standard Python functions
# They can perform API calls, DB operations, etc.


@activity.defn
async def fetch_connections(workspace_id: str) -> list[str]:
    activity.logger.info(f"Fetching connections for {workspace_id}")
    # Simulate IO
    await asyncio.sleep(1)
    return ["conn_1", "conn_2", "conn_3"]


@activity.defn
async def index_connection(connection_id: str) -> str:
    activity.logger.info(f"Indexing connection {connection_id}")
    # Simulate heavy processing
    await asyncio.sleep(2)
    return f"indexed_{connection_id}"
