# labs/uphillsnowball/server.py
"""UphillSnowball API Server.

FastAPI service wrapping the sovereign agent swarm orchestrator.
Designed for Cloud Run deployment with Firebase Hosting proxy.

Endpoints:
    POST /api/tasks          — Submit a task to the swarm
    GET  /api/tasks          — List recent tasks
    GET  /api/tasks/{id}     — Get task status
    GET  /api/tasks/{id}/stream — SSE stream for real-time updates
    GET  /api/agents         — List agent swarm status
    POST /api/gauntlet/evaluate — Run gauntlet evaluation
    GET  /api/health         — Health check (Cloud Run required)
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from agent.gauntlet import GauntletVerdict, evaluate
from agent.memory import AgentState, TaskRecord, get_memory
from agent.swarm_orchestrator import AgentRole, SwarmTask, get_orchestrator

logger = logging.getLogger("uphillsnowball.server")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# ── App ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="UphillSnowball API",
    description="Sovereign Agent Swarm Orchestrator",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS for dashboard origins
_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://shadowtagai.web.app",
    "https://kovelai.web.app",
    "https://shadowtag-omega-v4.web.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── In-Memory Task Registry ───────────────────────────────────────────────
# MVP: tasks also persisted to Firestore via AgentMemory

_tasks: dict[str, SwarmTask] = {}
_task_events: dict[str, asyncio.Queue] = {}


# ── Request / Response Models ──────────────────────────────────────────────


class TaskCreateRequest(BaseModel):
    """Request body for creating a new task."""

    description: str = Field(..., min_length=1, max_length=4096)
    context: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response model for a task."""

    task_id: str
    description: str
    status: str
    assigned_agent: str | None = None
    result: str = ""
    created_at: float


class AgentResponse(BaseModel):
    """Response model for an agent."""

    role: str
    model: str
    temperature: float
    status: str = "active"


class GauntletRequest(BaseModel):
    """Request body for gauntlet evaluation."""

    agent_id: str = "manual"
    role: str = "executor"
    type: str = "code_write"
    content: str = ""
    command: str = ""
    target_file: str = ""
    session_start: float = Field(default_factory=time.time)


class GauntletResponse(BaseModel):
    """Response model for gauntlet evaluation."""

    passed: bool
    verdict: str
    blocked_by: int | None = None
    total_elapsed_ms: int
    layers: list[dict[str, Any]]


# ── Health ─────────────────────────────────────────────────────────────────


@app.get("/api/health")
async def health_check():
    """Cloud Run health check endpoint."""
    return {
        "status": "healthy",
        "service": "uphillsnowball-api",
        "version": "1.0.0",
        "timestamp": time.time(),
    }


# ── Tasks ──────────────────────────────────────────────────────────────────


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
async def create_task(req: TaskCreateRequest):
    """Submit a new task to the agent swarm."""
    orchestrator = get_orchestrator()

    # Create an event queue for SSE streaming
    task_id = f"task_{int(time.time())}"
    _task_events[task_id] = asyncio.Queue()

    try:
        task = await orchestrator.submit_task(req.description, req.context)
        _tasks[task.task_id] = task

        # Persist to Firestore
        memory = get_memory()
        await memory.record_task(
            TaskRecord(
                task_id=task.task_id,
                description=task.description,
                agent_role=task.assigned_agent.value if task.assigned_agent else "unassigned",
                status=task.status,
                result_summary=task.result[:200] if task.result else "",
            )
        )

        # Notify SSE subscribers
        if task.task_id in _task_events:
            await _task_events[task.task_id].put({
                "event": "status",
                "data": {"status": task.status, "result": task.result[:500]},
            })

        return TaskResponse(
            task_id=task.task_id,
            description=task.description,
            status=task.status,
            assigned_agent=task.assigned_agent.value if task.assigned_agent else None,
            result=task.result,
            created_at=task.created_at,
        )
    except Exception as e:
        logger.exception("Task creation failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/tasks", response_model=list[TaskResponse])
async def list_tasks():
    """List all in-memory tasks (recent first)."""
    sorted_tasks = sorted(_tasks.values(), key=lambda t: t.created_at, reverse=True)
    return [
        TaskResponse(
            task_id=t.task_id,
            description=t.description,
            status=t.status,
            assigned_agent=t.assigned_agent.value if t.assigned_agent else None,
            result=t.result,
            created_at=t.created_at,
        )
        for t in sorted_tasks[:50]
    ]


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return TaskResponse(
        task_id=task.task_id,
        description=task.description,
        status=task.status,
        assigned_agent=task.assigned_agent.value if task.assigned_agent else None,
        result=task.result,
        created_at=task.created_at,
    )


@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str, request: Request):
    """SSE stream for real-time task updates."""
    if task_id not in _task_events:
        _task_events[task_id] = asyncio.Queue()

    async def event_generator():
        queue = _task_events[task_id]
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {
                        "event": event.get("event", "message"),
                        "data": str(event.get("data", "")),
                    }
                except TimeoutError:
                    # Keep-alive ping
                    yield {"event": "ping", "data": ""}
        finally:
            # Cleanup stale queues
            if task_id in _task_events and _task_events[task_id].empty():
                del _task_events[task_id]

    return EventSourceResponse(event_generator())


# ── Agents ─────────────────────────────────────────────────────────────────


@app.get("/api/agents", response_model=list[AgentResponse])
async def list_agents():
    """List all agents in the swarm."""
    orchestrator = get_orchestrator()
    return [
        AgentResponse(
            role=config.role.value,
            model=config.model,
            temperature=config.temperature,
        )
        for config in orchestrator._agents.values()
    ]


# ── Gauntlet ───────────────────────────────────────────────────────────────


@app.post("/api/gauntlet/evaluate", response_model=GauntletResponse)
async def evaluate_gauntlet(req: GauntletRequest):
    """Run the 17-layer gauntlet on an action."""
    action = {
        "agent_id": req.agent_id,
        "role": req.role,
        "type": req.type,
        "content": req.content,
        "command": req.command,
        "target_file": req.target_file,
        "session_start": req.session_start,
        "actions_this_minute": 1,
        "lines_changed": 0,
        "output_tokens": 0,
        "estimated_cost_usd": 0.0,
        "urls": [],
    }

    result = evaluate(action)

    return GauntletResponse(
        passed=result.passed,
        verdict=result.verdict.value,
        blocked_by=result.blocked_by,
        total_elapsed_ms=result.total_elapsed_ms,
        layers=[
            {
                "layer_id": lr.layer_id,
                "layer_name": lr.layer_name,
                "verdict": lr.verdict.value,
                "detail": lr.detail,
                "elapsed_us": lr.elapsed_us,
            }
            for lr in result.layers
        ],
    )


# ── Startup ────────────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup():
    """Initialize the swarm on server boot."""
    logger.info("UphillSnowball API starting — initializing swarm orchestrator")
    get_orchestrator()
    logger.info("Swarm orchestrator ready")


# ── Error Handler ──────────────────────────────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """RFC 9457 structured error response."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
        },
    )
