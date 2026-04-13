"""
Task service layer.

Extracts all database operations from task routes
into a proper service/repository pattern.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.database import Task, User
from app.models import TaskCreate, TaskStatus


class TaskService:
    """Service layer for task operations."""

    @staticmethod
    def get_user(db: Session, user_id: int) -> User | None:
        """Get a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        """Create a new task."""
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status.value,
            priority=task_data.priority,
            user_id=task_data.user_id,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def list_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: TaskStatus | None = None,
        priority: int | None = None,
    ) -> list[Task]:
        """List tasks with optional filtering and pagination."""
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status.value)
        if priority:
            query = query.filter(Task.priority == priority)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task | None:
        """Get a task by ID."""
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def update_task(db: Session, task: Task, task_data: TaskCreate) -> Task:
        """Update a task."""
        task.title = task_data.title
        task.description = task_data.description
        task.status = task_data.status.value
        task.priority = task_data.priority
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task: Task) -> None:
        """Delete a task."""
        db.delete(task)
        db.commit()

    @staticmethod
    def update_task_status(db: Session, task: Task, new_status: TaskStatus) -> Task:
        """Update only the status of a task."""
        task.status = new_status.value
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
        return task
