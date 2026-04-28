# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Request

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/eventarc",
    tags=["eventarc"],
    # Eventarc calls originate from standard GCP services inside the VPC
    # without zero_trust_token unless OIDC identity proxy is strict.
)


async def _boot_temporal_swarm(issue_id: str):
    """Temporal.io Client execution.
    Triggers the Python Swarm, creates the gVisor sandbox, and executes the Cor.Cursor visual proofing.
    """
    logger.info(
        f"[TEMPORAL BRIDGE] Spinning up gVisor sandbox and Cor.Cursor recorder for {issue_id}...",
    )
    temporal_host = os.environ.get("TEMPORAL_HOST", "localhost:7233")
    try:
        from temporalio.client import Client

        client = await Client.connect(temporal_host)
        workflow_id = f"omega-leviathan-wake-{uuid.uuid4().hex[:8]}"

        await client.start_workflow(
            "OmegaPayloadOrchestrator",
            f"EXECUTE_SWARM_FOR_ISSUE:{issue_id}",
            id=workflow_id,
            task_queue="omega-swarm-queue",
        )
        logger.info(f"[TEMPORAL BRIDGE] Workflow {workflow_id} dispatched successfully to Swarm.")
    except Exception as e:
        logger.error(f"[TEMPORAL BRIDGE] Temporal cluster unreachable: {e}. Swarm payload failed.")


@router.post("/webhook")
async def eventarc_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receives Eventarc payloads from Firestore when whiteboard_issues are updated.
    If status == 'CLEARED_FOR_SWARM', wakes up the Temporal Swarm workflows.
    """
    try:
        payload = await request.json()

        # Extract the fields from the v1.Document format
        updated_fields = payload.get("updateMask", {}).get("fieldPaths", [])
        if "status" in updated_fields:
            doc_data = payload.get("value", {}).get("fields", {})
            status = doc_data.get("status", {}).get("stringValue")

            if status == "CLEARED_FOR_SWARM":
                # Parse issueID from the document name path: projects/X/databases/Y/documents/whiteboard_issues/ISSUE_ID
                full_name = payload.get("value", {}).get("name", "")
                issue_id = full_name.split("/")[-1]

                logger.info(f"[EVENTARC] Leviathan Waking for Issue: {issue_id}")
                # Defer the swarm boot to a background task so we return 200 OK immediately to Eventarc
                background_tasks.add_task(_boot_temporal_swarm, issue_id)

    except Exception as e:
        logger.error(f"[EVENTARC] Payload parsing error: {e}")
        return {"status": "error", "message": str(e)}

    return {"status": "received"}
