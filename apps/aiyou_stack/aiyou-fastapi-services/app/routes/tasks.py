"""
Task management endpoints
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import Task, User, get_db
from app.models import TaskCreate, TaskResponse, TaskStatus

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task
    """
    # Verify user exists
    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Create task
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority,
        user_id=task.user_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: TaskStatus | None = None,
    priority: int | None = None,
    db: Session = Depends(get_db),
):
    """
    List all tasks with filtering and pagination
    """
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status.value)
    if priority:
        query = query.filter(Task.priority == priority)

    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):
    """
    Update a task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Update fields
    task.title = task_update.title
    task.description = task_update.description
    task.status = task_update.status.value
    task.priority = task_update.priority
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return None


@router.patch("/{task_id}/status")
async def update_task_status(task_id: int, new_status: TaskStatus, db: Session = Depends(get_db)):
    """
    Update only the status of a task
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    task.status = new_status.value
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task
