"""
Verdict Systems - School/Student Vertical (MVP)
Academic scheduling, lockouts, AI tutoring, and teacher oversight

This is the MVP vertical for Verdict Systems, targeting:
- K-12 students
- College students
- Teachers and educators
- Parent oversight of student work
"""

from datetime import datetime

from pydantic import BaseModel, Field

from ..core.enums import CompletionMethod, PriorityLevel, VerticalType
from ..models.task import Task, TaskCompletion, TaskCreate


class Assignment(TaskCreate):
    """
    School assignment with academic-specific features

    Extends base Task with:
    - Subject/course tracking
    - Grading integration
    - Group project support
    - Submission requirements
    """

    vertical: VerticalType = Field(default=VerticalType.SCHOOL, const=True)

    # Academic fields
    subject: str = Field(..., description="Subject/course name")
    course_id: str | None = Field(None, description="Course identifier")
    teacher_id: str = Field(..., description="Teacher/instructor ID")
    assignment_type: str = Field(..., description="homework|test|project|reading|study")

    # Submission
    submission_required: bool = Field(default=True)
    submission_format: list[str] = Field(
        default_factory=lambda: ["pdf"], description="Accepted file formats"
    )
    max_file_size_mb: int = Field(default=10, description="Max submission size")

    # Group work
    is_group_project: bool = Field(default=False)
    group_members: list[str] = Field(default_factory=list, description="Student IDs")

    # AI assistance
    ai_tutor_enabled: bool = Field(default=True)
    ai_hints_allowed: bool = Field(default=True)
    ai_full_solutions: bool = Field(default=False, description="Allow AI to show full solutions")

    # Lockout (default enabled for schoolwork)
    enable_lockout: bool = Field(default=True)
    lockout_grace_minutes: int = Field(default=30)
    blocked_apps: list[str] = Field(
        default_factory=lambda: [
            "instagram",
            "tiktok",
            "snapchat",
            "youtube",
            "facebook",
            "twitter",
            "reddit",
            "discord",
        ]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chapter 5 Homework - Quadratic Equations",
                "description": "Complete problems 1-20, show all work. Submit PDF by 2pm tomorrow.",
                "deadline": "2025-11-18T14:00:00Z",
                "estimated_duration_minutes": 60,
                "priority": 4,
                "user_id": "student_12345",
                "subject": "Algebra II",
                "course_id": "math_201",
                "teacher_id": "teacher_jones",
                "assignment_type": "homework",
                "submission_required": True,
                "submission_format": ["pdf", "docx"],
                "ai_tutor_enabled": True,
                "ai_hints_allowed": True,
                "ai_full_solutions": False,
                "enable_lockout": True,
                "lockout_grace_minutes": 30,
                "tags": ["math", "homework", "algebra"],
            }
        }


class TeacherPing(BaseModel):
    """
    Student request for teacher help

    Allows students to "ping" teachers for help during work sessions.
    Teachers can respond via video call, message, or schedule office hours.
    """

    task_id: str
    student_id: str
    teacher_id: str
    question: str = Field(..., max_length=500)
    urgency: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    preferred_response: str = Field(
        default="message", description="message|video_call|office_hours"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AITutorSession(BaseModel):
    """
    AI tutor assistance session

    Provides scaffolded help for students:
    - Hints and guidance (not full solutions)
    - Concept explanations
    - Similar example problems
    - Step-by-step walkthroughs
    """

    session_id: str
    task_id: str
    student_id: str
    subject: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None

    # Interaction log
    messages: list[dict[str, str]] = Field(default_factory=list, description="Conversation history")

    # Constraints
    hints_given: int = Field(default=0)
    max_hints: int = Field(default=5, description="Hint limit before requiring break")
    full_solutions_shown: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "tutor_20251117_001",
                "task_id": "task_20251117_001",
                "student_id": "student_12345",
                "subject": "Algebra II",
                "messages": [
                    {"role": "student", "content": "I don't understand problem 5"},
                    {
                        "role": "tutor",
                        "content": "Let's break down problem 5. What's the first step in solving a quadratic equation?",
                    },
                ],
                "hints_given": 1,
                "max_hints": 5,
            }
        }


class GradeSubmission(BaseModel):
    """
    Teacher grading of student work

    Allows teachers to:
    - Grade assignments
    - Provide feedback
    - Approve task completion
    - Trigger lockout release
    """

    task_id: str
    student_id: str
    teacher_id: str
    grade: str | None = Field(None, description="Letter grade or score")
    score: float | None = Field(None, ge=0, le=100, description="Percentage score")
    feedback: str | None = Field(None, max_length=2000)
    approved: bool = Field(..., description="Approve task as complete")
    graded_at: datetime = Field(default_factory=datetime.utcnow)


class ClassSchedule(BaseModel):
    """
    Automated class schedule integration

    Imports class schedules and creates tasks for:
    - Homework assignments
    - Test preparation
    - Project deadlines
    - Reading assignments
    """

    schedule_id: str
    student_id: str
    course_id: str
    course_name: str
    teacher_id: str

    # Schedule
    days_of_week: list[str] = Field(..., description="mon|tue|wed|thu|fri|sat|sun")
    start_time: str = Field(..., description="HH:MM format")
    end_time: str = Field(..., description="HH:MM format")

    # Auto-task creation
    auto_create_homework: bool = Field(default=True)
    homework_default_deadline_days: int = Field(
        default=1, description="Days after assignment to deadline"
    )
    auto_enable_lockout: bool = Field(default=True)


# ============================================================================
# School Vertical Helper Functions
# ============================================================================


def create_assignment_task(assignment: Assignment) -> Task:
    """
    Convert Assignment to Task with school-specific defaults

    Applies:
    - Approval requirement (teacher must approve)
    - AI tutor configuration
    - Lockout settings
    - Submission-based completion
    """
    task_dict = assignment.dict()

    # Set school-specific fields
    task_dict["requires_approval"] = True
    task_dict["approver_id"] = assignment.teacher_id

    # Store academic metadata
    task_dict["metadata"] = {
        "subject": assignment.subject,
        "course_id": assignment.course_id,
        "teacher_id": assignment.teacher_id,
        "assignment_type": assignment.assignment_type,
        "submission_required": assignment.submission_required,
        "submission_format": assignment.submission_format,
        "is_group_project": assignment.is_group_project,
        "group_members": assignment.group_members,
        "ai_tutor_config": {
            "enabled": assignment.ai_tutor_enabled,
            "hints_allowed": assignment.ai_hints_allowed,
            "full_solutions": assignment.ai_full_solutions,
        },
    }

    return Task(**task_dict)


async def handle_assignment_submission(
    task_id: str, student_id: str, submission_url: str, notes: str | None = None
) -> Task:
    """
    Handle student submission of assignment

    Process:
    1. Mark task as submitted (blocked, awaiting approval)
    2. Notify teacher for grading
    3. Optionally release lockout (based on policy)
    4. Wait for teacher approval
    """
    from ..core.schiznit_engine import schiznit_engine

    completion = TaskCompletion(
        completion_method=CompletionMethod.SUBMISSION_BASED,
        completed_by=student_id,
        notes=notes,
        submission_url=submission_url,
    )

    task = await schiznit_engine.complete_task(task_id, completion)

    # TODO: Send notification to teacher
    # TODO: Optionally release lockout (configurable)

    return task


async def handle_teacher_grading(grading: GradeSubmission) -> Task:
    """
    Handle teacher grading and approval

    Process:
    1. Record grade and feedback
    2. If approved, mark task complete
    3. Release lockout
    4. Notify student
    """
    from ..core.schiznit_engine import schiznit_engine

    task = await schiznit_engine.get_task(grading.task_id)

    if not task:
        raise ValueError(f"Task {grading.task_id} not found")

    # Store grading in metadata
    task.metadata["grading"] = {
        "teacher_id": grading.teacher_id,
        "grade": grading.grade,
        "score": grading.score,
        "feedback": grading.feedback,
        "graded_at": grading.graded_at.isoformat(),
    }

    # If approved, complete the task
    if grading.approved:
        completion = TaskCompletion(
            completion_method=CompletionMethod.TEACHER_APPROVED,
            completed_by=grading.teacher_id,
            notes=grading.feedback,
            metadata={"grade": grading.grade, "score": grading.score},
        )

        task = await schiznit_engine.complete_task(grading.task_id, completion)

    return task


async def create_ai_tutor_session(task_id: str, student_id: str, subject: str) -> AITutorSession:
    """
    Start AI tutor session for a task

    Returns configured tutor session with:
    - Hint limits
    - Subject-specific knowledge
    - Solution restrictions
    """
    import uuid

    from ..core.schiznit_engine import schiznit_engine

    task = await schiznit_engine.get_task(task_id)

    if not task:
        raise ValueError(f"Task {task_id} not found")

    if not task.ai_tutor_enabled:
        raise ValueError(f"AI tutor not enabled for task {task_id}")

    # Get AI config from task metadata
    ai_config = task.metadata.get("ai_tutor_config", {})

    session = AITutorSession(
        session_id=f"tutor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        student_id=student_id,
        subject=subject,
        max_hints=5 if ai_config.get("hints_allowed", True) else 0,
    )

    # TODO: Initialize Claude/Gemini session with task context
    # TODO: Configure system prompt for tutoring (hints only, no full solutions)

    return session
