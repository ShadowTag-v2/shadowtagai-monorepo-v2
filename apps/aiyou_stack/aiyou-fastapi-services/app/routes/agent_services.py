"""API endpoints for high-value agent services."""

import structlog
from agnt_services.extract_memories_service import ExtractMemoriesService

# Assuming these are available in packages/agnt_services
from agnt_services.session_memory_service import SessionMemoryService
from fastapi import APIRouter
from pydantic import BaseModel

logger = structlog.get_logger()
router = APIRouter(prefix="/agent", tags=["agent-services"])


class SummaryRequest(BaseModel):
    task_id: str
    agent_id: str


@router.post("/summary/start")
async def start_summary(request: SummaryRequest):
    """Start periodic background summarization for an agent."""
    logger.info("agent_summary_start_requested", task_id=request.task_id)
    # Stubbed implementation relying on the backend state
    return {"status": "started", "task_id": request.task_id}


@router.post("/summary/stop")
async def stop_summary(request: SummaryRequest):
    """Stop background summarization."""
    logger.info("agent_summary_stop_requested", task_id=request.task_id)
    return {"status": "stopped", "task_id": request.task_id}


class MemoryRequest(BaseModel):
    session_id: str
    context: dict


@router.post("/memory/session")
async def get_session_memory(request: MemoryRequest):
    """Retrieve session memory."""
    service = SessionMemoryService(session_id=request.session_id)
    memory = await service.retrieve_memory()
    return {"status": "success", "memory": memory}


@router.post("/memory/extract")
async def extract_memories(request: MemoryRequest):
    """Extract memories from conversation context."""
    service = ExtractMemoriesService(session_id=request.session_id)
    extracted = await service.extract(request.context)
    return {"status": "success", "extracted": extracted}


class WatchdogRequest(BaseModel):
    task_id: str
    timeout_s: int = 300


@router.post("/watchdog/register")
async def register_watchdog(request: WatchdogRequest):
    """Register a task with the watchdog."""
    # Assuming TaskWatchdog has a method or function to register
    return {"status": "registered", "task_id": request.task_id}
