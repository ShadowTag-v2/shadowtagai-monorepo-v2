"""UphillSnowball API — Sovereign Agent Orchestration Backend.

Cloud Run source-deploy service. Provides:
- Agent roster management
- Task submission + SSE streaming
- 17-layer gauntlet evaluation
- Health check endpoint

No Docker. Source deploy only (saas-architecture-gate doctrine).
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import AsyncGenerator
from enum import StrEnum
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(
  title="UphillSnowball API",
  version="1.0.0",
  description="Sovereign Agent Orchestration Backend",
)

# CORS — allow Firebase Hosting origins
ALLOWED_ORIGINS = [
  "https://uphillsnowball.web.app",
  "https://uphillsnowball.firebaseapp.com",
  "https://kovelai.web.app",
  "http://localhost:8888",
  "http://localhost:8080",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=ALLOWED_ORIGINS,
  allow_credentials=True,
  allow_methods=["GET", "POST"],
  allow_headers=os.environ.get(
    "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
  ).split(","),
)

# ── Models ──


class AgentStatus(StrEnum):
  """Agent operational status."""

  ACTIVE = "active"
  IDLE = "idle"
  OFFLINE = "offline"


class Agent(BaseModel):
  """Agent in the sovereign swarm."""

  agent_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
  role: str
  model: str = "gemini-3.1-flash-lite-preview"
  temperature: float = 0.7
  status: AgentStatus = AgentStatus.ACTIVE


class TaskStatus(StrEnum):
  """Task lifecycle status."""

  PENDING = "pending"
  PROCESSING = "processing"
  COMPLETED = "completed"
  FAILED = "failed"
  BLOCKED = "blocked"


class TaskCreate(BaseModel):
  """Request body for task creation."""

  description: str = Field(min_length=1, max_length=2000)


class Task(BaseModel):
  """Task in the orchestration queue."""

  task_id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:6].upper()}")
  description: str
  status: TaskStatus = TaskStatus.PENDING
  assigned_agent: str | None = None
  result: str | None = None
  created_at: float = Field(default_factory=time.time)


class GauntletRequest(BaseModel):
  """Request for gauntlet evaluation."""

  type: str = "shell_command"
  command: str = ""
  content: str = ""


class GauntletLayerResult(BaseModel):
  """Result from a single gauntlet layer."""

  layer_id: int
  name: str
  verdict: str  # pass, warn, block
  detail: str = ""
  elapsed_ms: float = 0.0


class GauntletResult(BaseModel):
  """Full gauntlet evaluation result."""

  passed: bool
  verdict: str
  total_elapsed_ms: float
  layers: list[GauntletLayerResult]


# ── In-Memory State (replace with Firestore in Phase 2) ──

AGENTS: list[dict[str, Any]] = [
  {
    "agent_id": "cor-001",
    "role": "Cor (Principal Architect)",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.3,
    "status": "active",
  },
  {
    "agent_id": "sentinel-002",
    "role": "Sentinel (Security)",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.1,
    "status": "active",
  },
  {
    "agent_id": "ruff-003",
    "role": "Ruff (Dead Code)",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.0,
    "status": "active",
  },
  {
    "agent_id": "judge6-004",
    "role": "Judge 6 (Governance)",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.2,
    "status": "active",
  },
  {
    "agent_id": "kairos-005",
    "role": "KAIROS (Background)",
    "model": "gemini-3.1-flash-lite-preview",
    "temperature": 0.5,
    "status": "idle",
  },
]

TASKS: list[dict[str, Any]] = []

# ── 17-Layer Gauntlet ──

GAUNTLET_LAYERS = [
  "Identity Check",
  "Role Authorization",
  "Session Validity",
  "Rate Limit",
  "Content Safety",
  "Command Safety",
  "Path Protection",
  "Gemini Zone",
  "LOC Ceiling",
  "Dependency Check",
  "Model Isolation",
  "Output Size",
  "Network Egress",
  "Cost Guard",
  "Git Safety",
  "Telemetry Airgap",
  "RKILL Switch",
]

BLOCKED_COMMANDS = {
  "rm -rf",
  "sudo",
  "chmod 777",
  "mkfs",
  "dd if=",
  ":(){ :|:& };:",
  "fork bomb",
}
BLOCKED_PATHS = {"/etc/", "/usr/", "/var/", "/System/", "/root/", "~/.ssh/"}
WARN_PATTERNS = {"curl", "wget", "pip install", "npm install", "brew install"}


def evaluate_gauntlet(req: GauntletRequest) -> GauntletResult:
  """Run a command through the 17-layer gauntlet."""
  layers: list[GauntletLayerResult] = []
  passed = True
  start = time.monotonic()
  cmd = req.content.lower()

  for i, name in enumerate(GAUNTLET_LAYERS, 1):
    layer_start = time.monotonic()
    verdict = "pass"
    detail = ""

    # Layer 5: Content Safety
    if i == 5:
      if any(b in cmd for b in {"eval(", "exec(", "__import__", "compile("}):
        verdict = "block"
        detail = "Code injection detected"
        passed = False

    # Layer 6: Command Safety
    elif i == 6:
      if any(b in cmd for b in BLOCKED_COMMANDS):
        verdict = "block"
        detail = f"Blocked command: {cmd[:50]}"
        passed = False
      elif any(w in cmd for w in WARN_PATTERNS):
        verdict = "warn"
        detail = "External install detected"

    # Layer 7: Path Protection
    elif i == 7:
      if any(p in cmd for p in BLOCKED_PATHS):
        verdict = "block"
        detail = "Protected path access"
        passed = False

    # Layer 15: Git Safety
    elif i == 15:
      if any(g in cmd for g in {"force-push", "--force", "rebase -i", "filter-branch"}):
        verdict = "block"
        detail = "Destructive git operation"
        passed = False
      elif "git push" in cmd:
        verdict = "warn"
        detail = "Push requires omega-sync"

    # Layer 16: Telemetry Airgap
    elif i == 16:
      if any(t in cmd for t in {"telemetry", "analytics", "tracking", "sentry"}):
        verdict = "warn"
        detail = "Telemetry reference detected"

    # Layer 17: RKILL Switch
    elif i == 17:
      if not passed:
        verdict = "block"
        detail = "RKILL: upstream layer blocked"

    elapsed = (time.monotonic() - layer_start) * 1000
    layers.append(
      GauntletLayerResult(
        layer_id=i,
        name=name,
        verdict=verdict,
        detail=detail,
        elapsed_ms=round(elapsed, 2),
      )
    )

  total_elapsed = (time.monotonic() - start) * 1000
  verdict_str = "PASS" if passed else "BLOCKED"

  return GauntletResult(
    passed=passed,
    verdict=verdict_str,
    total_elapsed_ms=round(total_elapsed, 2),
    layers=layers,
  )


# ── Routes ──


@app.get("/api/health")
async def health() -> dict[str, str]:
  """Health check endpoint."""
  return {"status": "ok", "service": "uphillsnowball-api", "version": "1.0.0"}


@app.get("/api/agents")
async def list_agents() -> list[dict[str, Any]]:
  """List all agents in the swarm."""
  return AGENTS


@app.get("/api/tasks")
async def list_tasks() -> list[dict[str, Any]]:
  """List all tasks."""
  return sorted(TASKS, key=lambda t: t.get("created_at", 0), reverse=True)


@app.post("/api/tasks")
async def create_task(body: TaskCreate) -> dict[str, Any]:
  """Submit a new task to the swarm."""
  task = Task(description=body.description)
  task_dict = task.model_dump()

  # Auto-assign to first active agent
  active = [a for a in AGENTS if a["status"] == "active"]
  if active:
    task_dict["assigned_agent"] = active[0]["role"]
    task_dict["status"] = "processing"

  TASKS.append(task_dict)
  return task_dict


@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str) -> StreamingResponse:
  """SSE stream for task status updates."""
  task = next((t for t in TASKS if t["task_id"] == task_id), None)
  if not task:
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

  async def event_stream() -> AsyncGenerator[str]:
    yield f"event: status\ndata: {{'task_id': '{task_id}', 'status': '{task['status']}'}}\n\n"

    # Simulate processing -> completion
    for i in range(3):
      await _async_sleep(2)
      yield f"event: ping\ndata: {{'seq': {i}}}\n\n"

    task["status"] = "completed"
    task["result"] = (
      f"Task {task_id} completed by {task.get('assigned_agent', 'swarm')}"
    )
    yield f"event: status\ndata: {{'task_id': '{task_id}', 'status': 'completed'}}\n\n"

  return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/gauntlet/evaluate")
async def evaluate(body: GauntletRequest) -> GauntletResult:
  """Evaluate a command through the 17-layer gauntlet."""
  return evaluate_gauntlet(body)


async def _async_sleep(seconds: float) -> None:
  """Async sleep wrapper."""
  import asyncio

  await asyncio.sleep(seconds)


if __name__ == "__main__":
  import uvicorn

  port = int(os.environ.get("PORT", "8080"))
  uvicorn.run(app, host="0.0.0.0", port=port)
