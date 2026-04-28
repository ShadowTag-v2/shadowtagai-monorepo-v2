# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Task management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TaskCreate, TaskResponse, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):  # noqa: B008
    """Create a new task."""
    user = TaskService.get_user(db, task.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return TaskService.create_task(db, task)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: int | None = None,
    db: Session = Depends(get_db),  # noqa: B008
):
    """List all tasks with filtering and pagination."""
    return TaskService.list_tasks(db, skip, limit, status, priority)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):  # noqa: B008
    """Get a specific task by ID."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):  # noqa: B008
    """Update a task."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskService.update_task(db, task, task_update)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):  # noqa: B008
    """Delete a task."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    TaskService.delete_task(db, task)


@router.patch("/{task_id}/status")
async def update_task_status(task_id: int, new_status: TaskStatus, db: Session = Depends(get_db)):  # noqa: B008
    """Update only the status of a task."""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskService.update_task_status(db, task, new_status)
