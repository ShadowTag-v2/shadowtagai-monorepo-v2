"""
Verdict Systems - Main FastAPI Application
Executive Function Replacement Platform

Mission: Duplicate and perfect human executive function across domains—
helping individuals, families, schools, workplaces, and professionals
move through life without dropping critical tasks.
"""

import uuid
from datetime import datetime

from fastapi import FastAPI, HTTPException, Path, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.enums import TaskStatus, UrgencyLevel, VerticalType
from ..core.schiznit_engine import schiznit_engine
from ..models.task import Task, TaskCompletion, TaskCreate, TaskUpdate
from ..verticals.family import FamilyCheckIn, FamilyTask, ScreenTimeControl
from ..verticals.medical import MedicalTask, MedicationReminder, SafetyAlert

# Vertical imports
from ..verticals.school import (
    AITutorSession,
    Assignment,
    GradeSubmission,
    TeacherPing,
    create_ai_tutor_session,
    create_assignment_task,
    handle_assignment_submission,
    handle_teacher_grading,
)
from ..verticals.workplace import FocusSession, WorkTask

# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="Verdict Systems API",
    description="""
    **Executive Function Replacement Platform**

    Verdict Systems provides a universal task and life-orchestration layer with:

    - **Urgency Tile System**: Visual urgency escalation (green → yellow → red → critical)
    - **Lockout Protocols**: Focus enforcement through app blocking
    - **Multi-Vertical Support**: Family, School, Workplace, Medical, Senior Care, Transportation, Smart Home
    - **AI Assistance**: Integrated tutoring and guidance
    - **Admin Oversight**: Parent, teacher, manager, and caregiver controls
    - **Multi-Device Sync**: Seamless integration across phones, desktops, vehicles, and IoT

    **MVP**: School/Student vertical with academic scheduling, lockouts, AI tutoring, and teacher oversight
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for cross-device access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Core Task Management Endpoints
# ============================================================================


@app.get("/", tags=["Health"])
async def root():
    """API root endpoint"""
    return {
        "service": "Verdict Systems API",
        "version": "1.0.0",
        "status": "operational",
        "mission": "Executive function replacement across all life domains",
        "documentation": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "engine": "Schiznit v1.0",
        "active_users": len(schiznit_engine.user_tasks),
        "active_tasks": len(schiznit_engine.tasks),
        "active_lockouts": sum(len(tasks) for tasks in schiznit_engine.active_lockouts.values()),
    }


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task_create: TaskCreate):
    """
    Create a new task

    Creates a task and registers it with the Schiznit engine for:
    - Urgency monitoring and escalation
    - Lockout protocol enforcement
    - Notification scheduling
    - Dashboard updates
    """
    task = Task(
        id=f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        **task_create.dict(),
    )

    created_task = await schiznit_engine.create_task(task)
    return created_task


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: str = Path(..., description="Task ID")):
    """Get a specific task by ID"""
    task = await schiznit_engine.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task.update_status()  # Ensure current urgency
    return task


@app.get("/tasks", response_model=list[Task], tags=["Tasks"])
async def get_tasks(
    user_id: str = Query(..., description="User ID"),
    status: TaskStatus | None = Query(None, description="Filter by status"),
    urgency: UrgencyLevel | None = Query(None, description="Filter by urgency level"),
    vertical: VerticalType | None = Query(None, description="Filter by vertical"),
):
    """
    Get all tasks for a user

    Returns tasks sorted by urgency (critical first) and deadline.
    Automatically updates urgency levels before returning.
    """
    tasks = await schiznit_engine.get_user_tasks(user_id, status, urgency, vertical)
    return tasks


@app.patch("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(
    task_id: str = Path(..., description="Task ID"), task_update: TaskUpdate = None
):
    """Update a task"""
    task = await schiznit_engine.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Apply updates
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.update_status()
    return task


@app.post("/tasks/{task_id}/complete", response_model=Task, tags=["Tasks"])
async def complete_task(
    task_id: str = Path(..., description="Task ID"), completion: TaskCompletion = None
):
    """
    Mark a task as completed

    Handles:
    - Approval workflows (if required)
    - Lockout release
    - Completion notifications
    """
    try:
        task = await schiznit_engine.complete_task(task_id, completion)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
async def delete_task(task_id: str = Path(..., description="Task ID")):
    """Cancel/delete a task"""
    task = await schiznit_engine.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task.status = TaskStatus.CANCELLED
    return None


# ============================================================================
# Dashboard & User Experience
# ============================================================================


@app.get("/dashboard/{user_id}", tags=["Dashboard"])
async def get_dashboard(user_id: str = Path(..., description="User ID")):
    """
    Get comprehensive user dashboard

    Returns:
    - Urgency tile summary (count by color)
    - Next 5 upcoming deadlines
    - Lockout status
    - Today's completion stats
    - Productivity metrics
    """
    dashboard = await schiznit_engine.get_dashboard(user_id)
    return dashboard


@app.get("/urgency-tiles/{user_id}", tags=["Dashboard"])
async def get_urgency_tiles(user_id: str = Path(..., description="User ID")):
    """
    Get urgency tile visualization

    Returns tasks grouped by urgency level for tile display:
    - 🟢 Green: Low urgency
    - 🟡 Yellow: Medium urgency
    - 🔴 Red: High urgency
    - ⚫ Critical: Overdue/lockout active
    """
    tasks = await schiznit_engine.get_user_tasks(user_id)

    tiles = {"green": [], "yellow": [], "red": [], "critical": []}

    for task in tasks:
        if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            continue

        urgency = task.urgency_level or task.calculate_urgency()

        tiles[urgency.value].append(
            {
                "id": task.id,
                "title": task.title,
                "deadline": task.deadline,
                "time_remaining": str(task.time_until_deadline()),
                "vertical": task.vertical,
                "priority": task.priority,
            }
        )

    return tiles


# ============================================================================
# Lockout Management
# ============================================================================


@app.get("/lockout/{user_id}/{device_id}", tags=["Lockout"])
async def get_lockout_status(
    user_id: str = Path(..., description="User ID"),
    device_id: str = Path(..., description="Device ID"),
):
    """
    Get current lockout status for a device

    Returns:
    - Whether lockout is active
    - Lockout mode (none/soft/moderate/strict/emergency_only)
    - List of blocked apps
    - Tasks causing lockout
    - Override availability
    """
    lockout_status = await schiznit_engine.get_lockout_status(user_id, device_id)
    return lockout_status


@app.post("/lockout/{user_id}/override", tags=["Lockout"])
async def override_lockout(
    user_id: str = Path(..., description="User ID"),
    admin_id: str = Query(..., description="Admin/parent/teacher ID"),
    reason: str = Query(..., description="Reason for override"),
    duration_minutes: int = Query(60, description="Override duration in minutes"),
):
    """
    Admin override to temporarily disable lockout

    Use cases:
    - Emergency situations
    - Parent discretion
    - Teacher accommodation
    - Medical necessity

    Requires admin/parent/teacher/caregiver permissions.
    """
    result = await schiznit_engine.override_lockout(
        user_id=user_id,
        admin_id=admin_id,
        reason=reason,
        duration_minutes=duration_minutes,
    )

    return result


# ============================================================================
# School Vertical Endpoints (MVP)
# ============================================================================


@app.post(
    "/school/assignments",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["School"],
)
async def create_assignment(assignment: Assignment):
    """
    Create a school assignment

    Creates an assignment task with:
    - Teacher oversight and approval requirement
    - AI tutor configuration
    - Submission requirements
    - Automatic lockout for overdue assignments
    """
    task = create_assignment_task(assignment)
    created_task = await schiznit_engine.create_task(task)
    return created_task


@app.post("/school/assignments/{task_id}/submit", response_model=Task, tags=["School"])
async def submit_assignment(
    task_id: str = Path(..., description="Assignment task ID"),
    student_id: str = Query(..., description="Student ID"),
    submission_url: str = Query(..., description="URL to submitted work"),
    notes: str | None = Query(None, description="Student notes"),
):
    """
    Submit assignment for grading

    Marks assignment as submitted and:
    - Notifies teacher for grading
    - Optionally releases lockout (based on policy)
    - Waits for teacher approval
    """
    task = await handle_assignment_submission(task_id, student_id, submission_url, notes)
    return task


@app.post("/school/assignments/{task_id}/grade", response_model=Task, tags=["School"])
async def grade_assignment(
    task_id: str = Path(..., description="Assignment task ID"),
    grading: GradeSubmission = None,
):
    """
    Teacher grading and approval

    Records grade, provides feedback, and:
    - Approves task completion
    - Releases lockout
    - Notifies student
    """
    task = await handle_teacher_grading(grading)
    return task


@app.post("/school/ai-tutor/start", response_model=AITutorSession, tags=["School"])
async def start_ai_tutor(
    task_id: str = Query(..., description="Assignment task ID"),
    student_id: str = Query(..., description="Student ID"),
    subject: str = Query(..., description="Subject area"),
):
    """
    Start AI tutor session

    Provides scaffolded help:
    - Hints and guidance (not full solutions)
    - Concept explanations
    - Step-by-step walkthroughs
    - Limited hints before requiring break
    """
    session = await create_ai_tutor_session(task_id, student_id, subject)
    return session


@app.post("/school/teacher-ping", response_model=TeacherPing, tags=["School"])
async def ping_teacher(ping: TeacherPing):
    """
    Student pings teacher for help

    Notifies teacher with:
    - Student question
    - Urgency level
    - Preferred response method (message/video/office hours)
    """
    # TODO: Send notification to teacher
    # TODO: Create real-time response channel

    return ping


# ============================================================================
# Family Vertical Endpoints
# ============================================================================


@app.post(
    "/family/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Family"],
)
async def create_family_task(family_task: FamilyTask):
    """
    Create family task (chore, homework, goal, check-in)

    Features:
    - Allowance tracking
    - Photo proof requirements
    - Parental approval
    - Encouraging messages
    """
    task = Task(
        id=f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        **family_task.dict(),
    )

    created_task = await schiznit_engine.create_task(task)
    return created_task


@app.post("/family/checkin", response_model=FamilyCheckIn, tags=["Family"])
async def record_family_checkin(checkin: FamilyCheckIn):
    """Record family check-in (e.g., daily parent call for seniors)"""
    # TODO: Store in database
    # TODO: Update related task if check-in was task-based
    return checkin


@app.get("/family/screen-time/{user_id}", response_model=ScreenTimeControl, tags=["Family"])
async def get_screen_time(user_id: str = Path(..., description="User ID")):
    """Get screen time settings and usage"""
    # TODO: Retrieve from database
    # Mock response
    return ScreenTimeControl(
        user_id=user_id,
        daily_limit_minutes=120,
        blocked_during=[
            {"start": "20:00", "end": "07:00"},  # Nighttime block
            {"start": "12:00", "end": "13:00"},  # Lunch time (family time)
        ],
        earn_time_by_tasks=True,
        minutes_per_task=15,
    )


# ============================================================================
# Workplace Vertical Endpoints
# ============================================================================


@app.post(
    "/workplace/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Workplace"],
)
async def create_work_task(work_task: WorkTask):
    """
    Create workplace task

    Features:
    - Project tracking
    - Billable hours
    - Focus mode enforcement
    - Manager oversight
    """
    task = Task(
        id=f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        **work_task.dict(),
    )

    created_task = await schiznit_engine.create_task(task)
    return created_task


@app.post("/workplace/focus-session/start", response_model=FocusSession, tags=["Workplace"])
async def start_focus_session(
    user_id: str = Query(..., description="User ID"),
    task_id: str | None = Query(None, description="Related task ID"),
    duration_minutes: int = Query(..., ge=15, le=240, description="Session duration"),
):
    """
    Start deep work focus session

    Activates:
    - App blocking
    - Notification silencing
    - Productivity tracking
    """
    session = FocusSession(
        session_id=f"focus_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        task_id=task_id,
        duration_minutes=duration_minutes,
        started_at=datetime.utcnow(),
    )

    # TODO: Activate focus mode lockout
    # TODO: Start productivity tracking

    return session


# ============================================================================
# Medical/Senior Care Vertical Endpoints
# ============================================================================


@app.post(
    "/medical/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Medical"],
)
async def create_medical_task(medical_task: MedicalTask):
    """
    Create medical/health task

    Features:
    - Medication reminders
    - Appointment tracking
    - Photo proof verification
    - Caregiver oversight
    - Safety alerts
    """
    task = Task(
        id=f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        **medical_task.dict(),
    )

    created_task = await schiznit_engine.create_task(task)
    return created_task


@app.post("/medical/medication/taken", response_model=MedicationReminder, tags=["Medical"])
async def record_medication_taken(reminder: MedicationReminder):
    """
    Record medication taken

    Requires:
    - Photo proof (optional)
    - Caregiver confirmation (for critical meds)
    """
    # TODO: Store in database
    # TODO: Send confirmation to caregiver
    return reminder


@app.post("/medical/safety-alert", response_model=SafetyAlert, tags=["Medical"])
async def trigger_safety_alert(alert: SafetyAlert):
    """
    Trigger safety alert

    Alert types:
    - Fall detection
    - Missed medication
    - No movement detected
    - Emergency button pressed

    Notifies:
    - Caregivers
    - Emergency contacts
    - Optionally emergency services
    """
    # TODO: Send immediate notifications
    # TODO: Log alert
    # TODO: Optionally call emergency services

    return alert


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 60)
    print("Verdict Systems API - Schiznit Engine v1.0")
    print("Executive Function Replacement Platform")
    print("=" * 60)
    print("✓ Urgency tile system initialized")
    print("✓ Lockout protocols loaded")
    print("✓ Multi-vertical support active")
    print("✓ AI assistance layer ready")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("Verdict Systems API shutting down")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Different port from ingestion API
        reload=True,
        log_level="info",
    )
