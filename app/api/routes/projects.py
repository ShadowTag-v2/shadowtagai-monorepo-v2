# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Project API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.models import Project, Conversation, Message, Memory
from app.schemas.project import (
  ProjectCreate,
  ProjectUpdate,
  ProjectResponse,
  ProjectStats,
)

router = APIRouter(prefix="/projects", tags=["projects"])


# Mock user dependency (replace with real auth)
async def get_current_user_id() -> int:
  """Get current user ID from auth token."""
  return 1  # TODO: Implement real authentication


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
  project_data: ProjectCreate,
  db: AsyncSession = Depends(get_db),
  user_id: int = Depends(get_current_user_id),
):
  """Create a new project."""
  project = Project(
    user_id=user_id,
    name=project_data.name,
    description=project_data.description,
    memory_enabled=project_data.memory_enabled,
  )

  db.add(project)
  await db.commit()
  await db.refresh(project)

  return project


@router.get("/", response_model=list[ProjectResponse])
async def get_projects(
  db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
  """Get all projects for the current user."""
  stmt = (
    select(Project)
    .where(Project.user_id == user_id)
    .order_by(Project.created_at.desc())
  )
  result = await db.execute(stmt)
  projects = result.scalars().all()

  return list(projects)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
  project_id: int,
  db: AsyncSession = Depends(get_db),
  user_id: int = Depends(get_current_user_id),
):
  """Get a project by ID."""
  stmt = select(Project).where(
    and_(Project.id == project_id, Project.user_id == user_id)
  )
  result = await db.execute(stmt)
  project = result.scalar_one_or_none()

  if not project:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
    )

  return project


@router.get("/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(
  project_id: int,
  db: AsyncSession = Depends(get_db),
  user_id: int = Depends(get_current_user_id),
):
  """Get statistics for a project."""
  # Verify project belongs to user
  stmt = select(Project).where(
    and_(Project.id == project_id, Project.user_id == user_id)
  )
  result = await db.execute(stmt)
  project = result.scalar_one_or_none()

  if not project:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
    )

  # Get conversation count
  stmt = select(func.count(Conversation.id)).where(
    and_(Conversation.project_id == project_id, Conversation.is_active == True)
  )
  result = await db.execute(stmt)
  conversation_count = result.scalar() or 0

  # Get message count
  stmt = (
    select(func.count(Message.id))
    .join(Conversation)
    .where(and_(Conversation.project_id == project_id, Conversation.is_active == True))
  )
  result = await db.execute(stmt)
  message_count = result.scalar() or 0

  # Get memory count
  stmt = select(func.count(Memory.id)).where(
    and_(Memory.project_id == project_id, Memory.is_active == True)
  )
  result = await db.execute(stmt)
  memory_count = result.scalar() or 0

  # Get last activity
  stmt = select(func.max(Conversation.last_message_at)).where(
    Conversation.project_id == project_id
  )
  result = await db.execute(stmt)
  last_activity = result.scalar()

  return ProjectStats(
    project_id=project_id,
    conversation_count=conversation_count,
    message_count=message_count,
    memory_count=memory_count,
    last_activity=last_activity,
  )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
  project_id: int,
  project_data: ProjectUpdate,
  db: AsyncSession = Depends(get_db),
  user_id: int = Depends(get_current_user_id),
):
  """Update a project."""
  stmt = select(Project).where(
    and_(Project.id == project_id, Project.user_id == user_id)
  )
  result = await db.execute(stmt)
  project = result.scalar_one_or_none()

  if not project:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
    )

  update_data = project_data.model_dump(exclude_unset=True)
  for field, value in update_data.items():
    setattr(project, field, value)

  await db.commit()
  await db.refresh(project)

  return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
  project_id: int,
  db: AsyncSession = Depends(get_db),
  user_id: int = Depends(get_current_user_id),
):
  """Delete a project and all associated data."""
  stmt = select(Project).where(
    and_(Project.id == project_id, Project.user_id == user_id)
  )
  result = await db.execute(stmt)
  project = result.scalar_one_or_none()

  if not project:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
    )

  await db.delete(project)
  await db.commit()
