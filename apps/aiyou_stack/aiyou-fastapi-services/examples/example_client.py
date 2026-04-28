# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Example client script demonstrating how to interact with the Automation Builder API."""

import asyncio

import httpx

API_BASE_URL = "http://localhost:8000/api/v1"


async def create_workflow():
    """Create a simple workflow."""
    workflow = {
        "name": "Example Workflow",
        "description": "An example workflow created via API",
        "definition": {
            "steps": [
                {
                    "name": "start",
                    "type": "log",
                    "config": {"message": "Workflow started", "level": "INFO"},
                },
                {"name": "delay", "type": "delay", "config": {"seconds": 1}},
                {
                    "name": "end",
                    "type": "log",
                    "config": {"message": "Workflow completed", "level": "INFO"},
                },
            ],
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/workflows", json=workflow)
        response.raise_for_status()
        result = response.json()
        print(f"Created workflow: {result['id']} - {result['name']}")
        return result


async def create_scheduled_job(workflow_id: int):
    """Create a scheduled job for a workflow."""
    job = {
        "name": "Hourly Job",
        "description": "Runs every hour",
        "workflow_id": workflow_id,
        "interval_seconds": 3600,  # Every hour
        "enabled": True,
        "max_retries": 3,
        "timeout_seconds": 600,
        "parameters": {"mode": "automatic"},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/jobs", json=job)
        response.raise_for_status()
        result = response.json()
        print(f"Created scheduled job: {result['id']} - {result['name']}")
        return result


async def create_event_trigger(workflow_id: int):
    """Create an event-based trigger."""
    trigger = {
        "name": "Data Updated Event",
        "description": "Triggers when data is updated",
        "trigger_type": "event",
        "workflow_id": workflow_id,
        "config": {"event_name": "data.updated"},
        "enabled": True,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/triggers", json=trigger)
        response.raise_for_status()
        result = response.json()
        print(f"Created trigger: {result['id']} - {result['name']}")
        return result


async def execute_workflow(workflow_id: int):
    """Manually execute a workflow."""
    execution_request = {
        "workflow_id": workflow_id,
        "input_data": {"source": "manual", "timestamp": "2024-01-01T00:00:00Z"},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/executions", json=execution_request)
        response.raise_for_status()
        result = response.json()
        print(f"Started execution: {result['id']} - Status: {result['status']}")
        return result


async def trigger_event():
    """Trigger an event."""
    event = {
        "event_name": "data.updated",
        "event_data": {"entity": "user", "entity_id": "12345", "changes": ["email", "name"]},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_BASE_URL}/triggers/events", json=event)
        response.raise_for_status()
        result = response.json()
        print(f"Triggered event: {result['message']}")
        print(f"Started {result['executions_started']} execution(s)")
        return result


async def list_executions():
    """List recent executions."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/executions?limit=5")
        response.raise_for_status()
        executions = response.json()
        print(f"\nRecent executions ({len(executions)}):")
        for execution in executions:
            print(
                f"  - Execution {execution['id']}: "
                f"Workflow {execution['workflow_id']} - "
                f"Status: {execution['status']}",
            )
        return executions


async def main():
    """Main example workflow."""
    print("=== Automation Builder API Example ===\n")

    # 1. Create a workflow
    print("1. Creating workflow...")
    workflow = await create_workflow()

    # 2. Create a scheduled job
    print("\n2. Creating scheduled job...")
    await create_scheduled_job(workflow["id"])

    # 3. Create an event trigger
    print("\n3. Creating event trigger...")
    await create_event_trigger(workflow["id"])

    # 4. Execute workflow manually
    print("\n4. Executing workflow manually...")
    await execute_workflow(workflow["id"])

    # Wait a bit for execution to complete
    await asyncio.sleep(2)

    # 5. Trigger an event
    print("\n5. Triggering event...")
    await trigger_event()

    # Wait a bit for triggered execution
    await asyncio.sleep(2)

    # 6. List recent executions
    print("\n6. Listing recent executions...")
    await list_executions()

    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(main())
