import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import SwarmWorkflow, execute_swarm_agent


async def main():
    try:
        # Connect to local Temporal server (requires 'temporal server start-dev' active)
        client = await Client.connect("localhost:7233")
    except Exception as e:
        print(
            f"[-] FATAL: Temporal cluster unreachable. Make sure 'temporal server start-dev' is active. {e}"
        )
        return

    # Run the worker to actively consume the 'omega-swarm-queue' referenced in invariant #2
    worker = Worker(
        client,
        task_queue="omega-swarm-queue",
        workflows=[SwarmWorkflow],
        activities=[execute_swarm_agent],
    )
    print("[+] Temporal Swarm Worker Daemon Online. Listening on omega-swarm-queue...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
