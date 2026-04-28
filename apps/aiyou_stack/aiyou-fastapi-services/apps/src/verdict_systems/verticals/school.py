# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Verdict Systems - School/Student Vertical (MVP)
Academic scheduling, lockouts, AI tutoring, and teacher oversight

This is the MVP vertical for Verdict Systems, targeting:
- K-12 students
- College students
- Teachers and educators
- Parent oversight of student work
"""

from datetime import datetime

from pydantic import BaseModel

from ..enums import VerticalType
from ..models.task import TaskCreate


class SchoolAssignmentMetadata(BaseModel):
    subject: str
    teacher_id: str | None = None
    course_id: str | None = None
    assignment_type: str = "homework"  # homework, project, exam_prep
    grade_weight: float = 1.0
    submit_url: str | None = None
    ai_tutor_enabled: bool = True
    rubric_id: str | None = None


class SchoolTaskCreate(TaskCreate):
    """Helper to create school tasks with correct defaults"""

    vertical: VerticalType = VerticalType.SCHOOL
    school_metadata: SchoolAssignmentMetadata

    def to_task_create(self) -> TaskCreate:
        data = self.model_dump(exclude={"school_metadata"})
        data["metadata"] = self.school_metadata.model_dump()
        return TaskCreate(**data)


class AITutorSession(BaseModel):
    session_id: str
    task_id: str
    student_id: str
    started_at: datetime
    messages: list[dict[str, str]] = []  # Role/Content
    summary: str | None = None
