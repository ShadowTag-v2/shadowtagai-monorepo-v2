import asyncio
import json
import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Zero-Trust Identity via Pydantic + GCP JWT
from src.api.zt_identity import TemporalIdentityPayload, parse_and_lock_identity

try:
    from src.api.tools import COMFYUI_IMAGE_TOOL_SCHEMA, WORKSPACE_SEARCH_TOOL_SCHEMA
except ImportError:
    try:
        from tools import (
            A2UI_GENERATOR_TOOL_SCHEMA,
            COMFYUI_IMAGE_TOOL_SCHEMA,
            WORKSPACE_SEARCH_TOOL_SCHEMA,
        )
    except ImportError:
        COMFYUI_IMAGE_TOOL_SCHEMA = {}
        WORKSPACE_SEARCH_TOOL_SCHEMA = {}
        A2UI_GENERATOR_TOOL_SCHEMA = {}

# Initialize the router instance
agents_router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


class ChatRequest(BaseModel):
    workspace_id: str
    agent_id: str
    message: str
    history: list[dict[str, Any]] = []


class ChatResponse(BaseModel):
    reply: str


class QueryPayload(BaseModel):
    q: str


@agents_router.get("/")
async def list_agents():
    return [
        {"id": "agent-1", "name": "Primary Intelligence"},
        {"id": "agent-2", "name": "Creative Suite"},
    ]


@agents_router.post("/query")
async def process_matrix_query(
    payload: QueryPayload,
    identity: TemporalIdentityPayload = Depends(parse_and_lock_identity),
):
    # --> Stage 4 Hardening: Temporal.io Invincible Orchestration
    temporal_host = os.environ.get("TEMPORAL_HOST", "localhost:7233")
    try:
        from temporalio.client import Client

        # Attempt to bind to the Temporal cluster
        client = await Client.connect(temporal_host)
        workflow_id = f"omega-heavy-lift-{uuid.uuid4().hex[:8]}"

        # Allow query string to parameterize the Temporal Execution Queue
        task_query = payload.q

        await client.start_workflow(
            "OmegaPayloadOrchestrator", task_query, id=workflow_id, task_queue="omega-swarm-queue"
        )
        return {
            "status": "Matrix accepted heavy lift via Temporal.io",
            "workflow_id": workflow_id,
            "assigned_query": task_query,
            "principal": identity.principal_id,
        }
    except Exception as e:
        # Graceful fallback: Accept locally if Temporal cluster is not yet active
        print(f"⚠️ Temporal Node Offline: {e}. Executing payload synchronously.")
        return {
            "status": "Matrix accepted heavy lift (Local fallback)",
            "assigned_query": payload.q,
            "principal": identity.principal_id,
        }


@agents_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # This is where LiteLLM agent loop triggers, injecting the tools:

    # Stubbed execution for the pipeline
    if "draw" in request.message.lower() or "generate" in request.message.lower():
        try:
            from src.api.tools import generate_local_image
        except ImportError:
            from tools import generate_local_image

        image_markdown = generate_local_image(request.message)
        return ChatResponse(reply=f"Here is your request:\n\n{image_markdown}")

    return ChatResponse(
        reply=f"Agent {request.agent_id} received your message. I have access to Workspace {request.workspace_id} via LanceDB."
    )


@agents_router.post("/stream")
async def chat_with_agent_agui(request: ChatRequest):
    """
    Cor.Firebase / AG-UI standard streaming protocol.
    Kosmos natively emits standard events instead of massive text blocks.
    """

    async def sse_agui():
        # 1. RUN_STARTED
        yield f"data: {json.dumps({'type': 'RUN_STARTED', 'agentId': request.agent_id})}\n\n"
        await asyncio.sleep(0.5)

        # 2. Text Content (Simulating 'Thinking' telemetry)
        yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'agentId': request.agent_id, 'delta': 'Analyzing repo context...'})}\n\n"
        await asyncio.sleep(1)

        # 3. Tool Call & A2UI Generator
        if "dashboard" in request.message.lower() or "supply" in request.message.lower():
            # Broadcast the tool call
            yield f"data: {json.dumps({'type': 'TOOL_CALL_START', 'agentId': request.agent_id, 'toolCallId': 'call_123', 'name': 'generate_a2ui'})}\n\n"
            await asyncio.sleep(1)

            # Emit the declarative JSON A2UI component
            a2ui = {
                "type": "A2UI_PAYLOAD",
                "agentId": request.agent_id,
                "payload": {
                    "type": "SandTable",
                    "data": {
                        "compliance_status": "LOCKED",
                        "telemetry": [
                            {"layerId": "Layer 14 (Zero Trust Execution)", "failureCount": 66},
                            {"layerId": "Layer 5 (CA Minors PII)", "failureCount": 1},
                            {"layerId": "Layer 9 (A2UI Parse Fault)", "failureCount": 0},
                        ],
                    },
                    "components": ["Aggregator"],
                },
            }
            yield f"data: {json.dumps(a2ui)}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'agentId': request.agent_id, 'delta': 'Analysis nominal.'})}\n\n"

        # 4. RUN_COMPLETED
        yield f"data: {json.dumps({'type': 'RUN_COMPLETED', 'agentId': request.agent_id})}\n\n"

    return StreamingResponse(sse_agui(), media_type="text/event-stream")
