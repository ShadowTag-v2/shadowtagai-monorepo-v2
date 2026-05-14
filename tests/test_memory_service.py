# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for memory service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models import User, Project
from app.schemas.memory import MemoryCreate, MemoryUpdate
from app.services.memory_service import memory_service


@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    user = User(email="test@example.com", username="testuser", hashed_password="hashed", memory_enabled=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_project(db_session, test_user):
    """Create test project."""
    project = Project(user_id=test_user.id, name="Test Project", memory_enabled=True)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.mark.asyncio
async def test_create_memory(db_session, test_user, test_project):
    """Test creating a memory."""
    memory_data = MemoryCreate(title="Test Memory", content="This is a test memory about FastAPI", memory_type="fact", project_id=test_project.id)

    memory = await memory_service.create_memory(db_session, test_user.id, memory_data)

    assert memory.id is not None
    assert memory.title == "Test Memory"
    assert memory.content == "This is a test memory about FastAPI"
    assert memory.memory_type == "fact"
    assert memory.user_id == test_user.id
    assert memory.project_id == test_project.id


@pytest.mark.asyncio
async def test_get_memories(db_session, test_user, test_project):
    """Test retrieving memories."""
    # Create multiple memories
    for i in range(3):
        memory_data = MemoryCreate(title=f"Memory {i}", content=f"Content {i}", memory_type="fact", project_id=test_project.id)
        await memory_service.create_memory(db_session, test_user.id, memory_data)

    # Retrieve memories
    memories = await memory_service.get_memories(db_session, test_user.id, project_id=test_project.id)

    assert len(memories) == 3


@pytest.mark.asyncio
async def test_update_memory(db_session, test_user, test_project):
    """Test updating a memory."""
    # Create memory
    memory_data = MemoryCreate(title="Original Title", content="Original content", memory_type="fact", project_id=test_project.id)
    memory = await memory_service.create_memory(db_session, test_user.id, memory_data)

    # Update memory
    update_data = MemoryUpdate(title="Updated Title", content="Updated content")
    updated_memory = await memory_service.update_memory(db_session, memory.id, test_user.id, update_data)

    assert updated_memory.title == "Updated Title"
    assert updated_memory.content == "Updated content"
    assert updated_memory.is_user_edited is True


@pytest.mark.asyncio
async def test_delete_memory(db_session, test_user, test_project):
    """Test deleting a memory."""
    # Create memory
    memory_data = MemoryCreate(title="To Delete", content="This will be deleted", memory_type="fact", project_id=test_project.id)
    memory = await memory_service.create_memory(db_session, test_user.id, memory_data)

    # Delete memory
    success = await memory_service.delete_memory(db_session, memory.id, test_user.id)

    assert success is True

    # Verify it's soft deleted
    memories = await memory_service.get_memories(db_session, test_user.id, project_id=test_project.id)
    assert len(memories) == 0
