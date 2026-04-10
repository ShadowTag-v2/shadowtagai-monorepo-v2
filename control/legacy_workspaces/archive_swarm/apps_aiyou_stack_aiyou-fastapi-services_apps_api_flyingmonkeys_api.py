"""
n-autoresearch/Kosmos/BioAgentss v8 API
Trigger swarm from iOS, web, or any HTTP client.
"""

import os
import sys
import uuid

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from n-autoresearch/Kosmos/BioAgentss_v8 import n-autoresearch/Kosmos/BioAgentssV8, SwarmResult

app = FastAPI(
    title="n-autoresearch/Kosmos/BioAgentss v8 API",
    description="Swarm orchestration with Claude Opus 4.5",
    version="8.0",
)

# CORS for iOS/web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
jobs = {}


class HuntRequest(BaseModel):
    target: str
    strategies: int = 5


class SwarmRequest(BaseModel):
    tasks: list[str]
    max_parallel: int = 5


class BrainstormRequest(BaseModel):
    topic: str
    num_ideas: int = 5


class SingleRequest(BaseModel):
    task: str


class PuzzleSolveRequest(BaseModel):
    lock_id: int
    answer: str


class PuzzleCodeRequest(BaseModel):
    code: str


class VaultInteractionRequest(BaseModel):
    """Unified vault interaction (Gemini VaultSimulation compatible)"""

    command: str  # "status", "inspect", "submit"
    lock_id: int | None = None
    solution_value: str | None = None


class BulkAnalyzeRequest(BaseModel):
    """Multi-model bulk analysis (Claude + Gemini)"""

    documents: list[str]  # List of document contents
    question: str  # Analysis question


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


def swarm_result_to_dict(result: SwarmResult) -> dict:
    return {
        "total": result.total,
        "completed": result.completed,
        "approved": result.approved,
        "blocked": result.blocked,
        "avg_latency_ms": result.avg_latency_ms,
        "results": result.results,
    }


# Initialize n-autoresearch/Kosmos/BioAgentss
fm = n-autoresearch/Kosmos/BioAgentssV8()

# Puzzle rooms storage (session-based)
puzzle_rooms = {}


@app.get("/")
def root():
    return {
        "service": "n-autoresearch/Kosmos/BioAgentss v8",
        "mission": fm.mission,
        "model": "claude-opus-4-5-20250514",
        "features": [
            "Tool Search (85% token savings)",
            "Programmatic Tool Calling (37% token savings)",
            "Token/Cost Tracking",
            "Puzzle Room Challenge",
            "Multi-Model Routing (Claude + Gemini)",
        ],
        "endpoints": [
            "POST /hunt",
            "POST /swarm",
            "POST /brainstorm",
            "POST /single",
            "POST /bulk_analyze  ← NEW: Multi-model bulk analysis",
            "GET /cost_stats  ← NEW: Multi-model cost comparison",
            "POST /puzzle/start",
            "POST /puzzle/{room_id}/solve",
            "POST /puzzle/{room_id}/code",
            "POST /puzzle/{room_id}/vault_interaction",
            "GET /puzzle/{room_id}/status",
            "GET /puzzle/{room_id}/history",
            "GET /status/{job_id}",
        ],
    }


@app.post("/hunt")
def hunt(request: HuntRequest):
    """
    Hunt mode - focused attack on a target.

    Example iOS Shortcut:
    POST https://your-server/hunt
    {"target": "$50k revenue in 30 days", "strategies": 5}
    """
    result = fm.hunt(request.target, strategies=request.strategies)
    return {"mode": "hunt", "target": request.target, **swarm_result_to_dict(result)}


@app.post("/swarm")
def swarm(request: SwarmRequest):
    """
    Multi-task swarm execution.

    POST /swarm
    {"tasks": ["task1", "task2", "task3"], "max_parallel": 5}
    """
    result = fm.release(request.tasks, max_parallel=request.max_parallel)
    return {"mode": "swarm", **swarm_result_to_dict(result)}


@app.post("/brainstorm")
def brainstorm(request: BrainstormRequest):
    """
    Brainstorm mode - generate and evaluate ideas.

    POST /brainstorm
    {"topic": "Ways to monetize AI", "num_ideas": 5}
    """
    result = fm.brainstorm(request.topic, num_ideas=request.num_ideas)
    return {
        "mode": "brainstorm",
        "topic": request.topic,
        **swarm_result_to_dict(result),
    }


@app.post("/single")
def single(request: SingleRequest):
    """
    Single task execution.

    POST /single
    {"task": "Find fastest path to $10k MRR"}
    """
    result = fm.release_single(request.task)
    return {"mode": "single", **result}


@app.post("/bulk_analyze")
async def bulk_analyze(request: BulkAnalyzeRequest):
    """
    Multi-model bulk analysis: Gemini reads, Claude reasons.

    Demonstrates Claude Architect + Gemini Specialist pattern:
    - Routes bulk reading to Gemini (200x cheaper) via VertexAIClient
    - Claude synthesizes final answer from Gemini summaries
    - 84-93% cost savings on bulk document analysis

    POST /bulk_analyze
    {
        "documents": ["doc1 content...", "doc2 content...", ...],
        "question": "Find security vulnerabilities in these files"
    }
    """

    result = await fm.bulk_analyze(request.documents, request.question)
    return {
        "mode": "bulk_analyze",
        "model_routing": "claude_architect_gemini_specialist",
        **result,
    }


@app.get("/cost_stats")
def cost_stats():
    """Get multi-model cost comparison stats"""
    return {
        "multi_model_router": fm.router.cost_comparison(),
        "claude_tokens": fm.tokens.display(),
    }


# Async job support for long-running tasks
def run_hunt_async(job_id: str, target: str, strategies: int):
    jobs[job_id]["status"] = "running"
    try:
        result = fm.hunt(target, strategies=strategies)
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = swarm_result_to_dict(result)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/hunt/async", response_model=JobResponse)
def hunt_async(request: HuntRequest, background_tasks: BackgroundTasks):
    """
    Async hunt - returns immediately with job_id.
    Poll /status/{job_id} for results.
    """
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"status": "queued", "target": request.target}
    background_tasks.add_task(run_hunt_async, job_id, request.target, request.strategies)
    return JobResponse(
        job_id=job_id, status="queued", message=f"Hunt started. Poll /status/{job_id}"
    )


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Check status of async job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/health")
def health():
    return {"status": "ok", "api_key_set": bool(fm.api_key)}


# =============================================================================
# PUZZLE ROOM ENDPOINTS
# =============================================================================


@app.post("/puzzle/start")
def puzzle_start():
    """
    Start a new Puzzle Room Challenge.
    Returns room_id for subsequent calls.

    POST /puzzle/start
    """
    room_id = str(uuid.uuid4())[:8]
    puzzle_rooms[room_id] = fm.puzzle_room()
    return {
        "room_id": room_id,
        "message": "Puzzle Room started! Solve 7 locks to open the vault.",
        "status": puzzle_rooms[room_id].get_status(),
    }


@app.get("/puzzle/{room_id}/status")
def puzzle_status(room_id: str):
    """Get puzzle room status"""
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return puzzle_rooms[room_id].get_status()


@app.post("/puzzle/{room_id}/solve")
def puzzle_solve(room_id: str, request: PuzzleSolveRequest):
    """
    Attempt to solve a lock.

    POST /puzzle/{room_id}/solve
    {"lock_id": 1, "answer": "2131"}
    """
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = puzzle_rooms[room_id]
    result = room.attempt_lock(request.lock_id, request.answer)
    return {**result, "status": room.get_status()}


@app.post("/puzzle/{room_id}/code")
def puzzle_code(room_id: str, request: PuzzleCodeRequest):
    """
    Solve using code execution sandbox (Programmatic Tool Calling).

    POST /puzzle/{room_id}/code
    {"code": "results[1] = 1847 + 1776 - 1492"}
    """
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = puzzle_rooms[room_id]
    result = room.solve_with_code(request.code)
    return result


@app.post("/puzzle/{room_id}/auto")
def puzzle_auto(room_id: str):
    """
    Auto-solve all locks using code execution.
    Demonstrates Programmatic Tool Calling efficiency.

    POST /puzzle/{room_id}/auto
    """
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = puzzle_rooms[room_id]
    auto_code = """
results[1] = 1847 + 1776 - 1492
results[2] = 1415
results[3] = 55
results[4] = "HELLO"
results[5] = int("10101010", 2)
results[6] = 29
results[7] = (results[1] + results[2] + results[3] + 170 + results[6]) % 1000
"""
    result = room.solve_with_code(auto_code)
    return {"mode": "auto_solve", "code_executed": auto_code, **result}


@app.post("/puzzle/{room_id}/vault_interaction")
def vault_interaction(room_id: str, request: VaultInteractionRequest):
    """
    Unified vault interaction endpoint (Gemini VaultSimulation compatible).

    Commands:
    - status: Get open/remaining locks
    - inspect: Get puzzle clue for a lock
    - submit: Submit solution for a lock

    POST /puzzle/{room_id}/vault_interaction
    {"command": "inspect", "lock_id": 1}
    {"command": "submit", "lock_id": 1, "solution_value": "2131"}
    """
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = puzzle_rooms[room_id]
    result = room.handle_tool_call(
        {
            "command": request.command,
            "lock_id": request.lock_id,
            "solution_value": request.solution_value,
        }
    )
    return {"result": result, "status": room.get_status()}


@app.get("/puzzle/{room_id}/history")
def puzzle_history(room_id: str):
    """Get interaction history for audit trail"""
    if room_id not in puzzle_rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = puzzle_rooms[room_id]
    return {"history": room.get_history()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)
