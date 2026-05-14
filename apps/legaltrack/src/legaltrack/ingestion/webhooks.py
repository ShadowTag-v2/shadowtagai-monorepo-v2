# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import base64
import datetime
import json
import logging
import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, Request

logger = logging.getLogger(__name__)

router = APIRouter()


async def push_to_aiyou(matter_id: str, email_payload: dict):
    """
    Background worker: Posts the extracted email payload directly to the ZT Ingestion pipeline.
    """
    logger.info(f"Webhook push to ZT Router for matter {matter_id}...")
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"http://127.0.0.1:8000/api/v1/rules/matters/{matter_id}/ingest",
                json={
                    "tenant_id": email_payload.get("tenant_id", str(uuid.uuid4())),
                    "raw_text": email_payload.get("body", "Default ECF or TrueFiling raw text payload..."),
                    "source": "email_webhook",
                    "jurisdiction": "FRCP",
                    "trigger_date": email_payload.get("date", datetime.date.today().isoformat()),
                },
                timeout=30.0,
            )
        except Exception as e:
            logger.error(f"Webhook forward failed: {e}")


@router.post("/pubsub")
async def receive_email_pubsub(request: Request, background_tasks: BackgroundTasks):
    """
    Receives email webhooks via Google Cloud Pub/Sub push subscription.
    """
    raw_body = await request.json()
    if not isinstance(raw_body, dict):
        return {"status": "invalid payload type"}

    body: dict = raw_body

    if not body or "message" not in body:
        return {"status": "invalid payload"}

    message = body["message"]
    if not isinstance(message, dict):
        return {"status": "invalid message type"}

    data_b64 = message.get("data")
    if data_b64:
        # Decode the PubSub message
        data = base64.b64decode(data_b64).decode("utf-8")
        email_payload = json.loads(data)

        # Enqueue live end-to-end processing parsing task
        matter_id = str(uuid.uuid4())
        background_tasks.add_task(push_to_aiyou, matter_id, email_payload)

    return {"status": "acknowledged"}
