"""Verdict Systems - Main FastAPI Application
Executive Function Replacement Platform

Mission: Duplicate and perfect human executive function across domains—
helping individuals, families, schools, workplaces, and professionals
move through life without dropping critical tasks.
"""

import os
import uuid
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API Key"""
    valid_key = os.environ.get("VERDICT_API_KEY", "dev-key")
    if api_key != valid_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key


# Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# --- JR Engine Integration ---
from ...judge_six.jr_engine import JREngine  # noqa: E402
from ...judge_six.models import Action  # noqa: E402
from ...judge_six.models import VerdictStatus as JRVerdictStatus  # noqa: E402
from ..core.schiznit_engine import schiznit_engine  # noqa: E402
from ..enums import TaskStatus, UrgencyLevel, VerticalType  # noqa: E402
from ..models.task import Task, TaskCompletion, TaskCreate, TaskUpdate  # noqa: E402
from ..verticals.family import FamilyTaskCreate  # noqa: E402
from ..verticals.medical import MedicalTaskCreate  # noqa: E402
from ..verticals.school import SchoolTaskCreate  # noqa: E402
from ..verticals.workplace import WorkplaceTaskCreate  # noqa: E402

jr_engine = JREngine()


def validate_action(payload: dict, source: str = "api", type: str = "create_task"):
    """Helper to run JR validation"""
    action = Action(
        id=str(uuid.uuid4()),
        type=type,
        payload=payload,
        source=source,
        timestamp=datetime.utcnow(),
    )
    verdict = jr_engine.validate(action)

    if verdict.status == JRVerdictStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JR Engine Rejection: {verdict.summary}",
        )
    return verdict


app = FastAPI(
    title="Verdict Systems API",
    description="Executive Function Replacement Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception Handlers
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Verdict Systems Operational",
        "mission": "Duplicate and perfect human executive function",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# --- Task Management ---


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_api_key)],
)
@limiter.limit("100/minute")
async def create_task(request: Request, task_create: TaskCreate):
    """Create a generic task"""
    # JR Validation
    validate_action(task_create.model_dump(), source="api_generic")
    return schiznit_engine.create_task(task_create)


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = schiznit_engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.update_urgency()
    return task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    # MVP: Basic update support
    task = schiznit_engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Apply updates (simplified)
    data = task_update.model_dump(exclude_unset=True)
    # JR Validation on update? Maybe later. For now, trust updates.

    for k, v in data.items():
        setattr(task, k, v)

    task.update_urgency()
    return task


@app.post("/tasks/{task_id}/complete", response_model=Task)
async def complete_task(task_id: str, completion: TaskCompletion | None = None):
    task = schiznit_engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    task.completion = completion
    task.update_urgency()
    return task


@app.get("/tasks", response_model=list[Task])
async def list_tasks(user_id: str, vertical: VerticalType | None = None):
    tasks = schiznit_engine.get_user_tasks(user_id)
    if vertical:
        tasks = [t for t in tasks if t.vertical == vertical]
    return tasks


# --- Vertical Specific Create Endpoints ---


@app.post("/school/assignments", response_model=Task)
async def create_school_task(task_create: SchoolTaskCreate):
    validate_action(task_create.model_dump(), source="api_school")
    return schiznit_engine.create_task(task_create.to_task_create())


@app.post("/family/chores", response_model=Task)
async def create_family_task(task_create: FamilyTaskCreate):
    validate_action(task_create.model_dump(), source="api_family")
    return schiznit_engine.create_task(task_create.to_task_create())


@app.post("/workplace/tasks", response_model=Task)
async def create_workplace_task(task_create: WorkplaceTaskCreate):
    validate_action(task_create.model_dump(), source="api_workplace")
    return schiznit_engine.create_task(task_create.to_task_create())


@app.post("/medical/tasks", response_model=Task)
async def create_medical_task(task_create: MedicalTaskCreate):
    validate_action(task_create.model_dump(), source="api_medical")
    return schiznit_engine.create_task(task_create.to_task_create())


# --- Lockout & Urgency ---


@app.get("/lockout/{user_id}", response_model=dict[str, str])
async def check_lockout_status(user_id: str):
    mode = schiznit_engine.check_lockout_state(user_id)
    active = schiznit_engine.get_active_lockouts(user_id)
    return {
        "status": mode,
        "active_lockout_tasks": [t.id for t in active],
        "message": f"Lockout Mode: {mode}",
    }


@app.get("/urgency-tiles/{user_id}")
async def get_urgency_tiles(user_id: str):
    """Visualization data for tiles"""
    tasks = schiznit_engine.get_user_tasks(user_id)
    tiles = {
        "critical": [t for t in tasks if t.urgency == UrgencyLevel.CRITICAL],
        "red": [t for t in tasks if t.urgency == UrgencyLevel.RED],
        "yellow": [t for t in tasks if t.urgency == UrgencyLevel.YELLOW],
        "green": [t for t in tasks if t.urgency == UrgencyLevel.GREEN],
    }
    return tiles
