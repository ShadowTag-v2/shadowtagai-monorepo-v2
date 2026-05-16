# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Background tasks for automatic memory synthesis and summarization."""

import logging
from datetime import datetime, timezone, timedelta
from celery import Celery
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Project, Conversation
from app.services import memory_service, summarization_service

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery("claude_memory_tasks", broker=settings.celery_broker_url, backend=settings.celery_result_backend)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Create async engine for background tasks
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="synthesize_user_memories")
async def synthesize_user_memories_task(user_id: int, project_id: int = None):
    """
    Background task to synthesize user memories.

    This task runs every 24 hours to update memory synthesis.
    """
    logger.info(f"Starting memory synthesis for user {user_id}, project {project_id}")

    async with AsyncSessionLocal() as db:
        try:
            # Synthesize memories
            result = await memory_service.synthesize_user_memories(db, user_id, project_id)

            logger.info(f"Completed memory synthesis for user {user_id}: {result.total_memories} memories synthesized")

            return {"user_id": user_id, "project_id": project_id, "total_memories": result.total_memories, "success": True}

        except Exception as e:
            logger.error(f"Error synthesizing memories for user {user_id}: {e}")
            return {"user_id": user_id, "project_id": project_id, "error": str(e), "success": False}


@celery_app.task(name="summarize_conversation")
async def summarize_conversation_task(conversation_id: int):
    """
    Background task to summarize a conversation.

    Called after a conversation reaches a certain number of messages.
    """
    logger.info(f"Starting conversation summarization for conversation {conversation_id}")

    async with AsyncSessionLocal() as db:
        try:
            # Get conversation
            from app.models import Message

            stmt = select(Conversation).where(Conversation.id == conversation_id)
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation or conversation.is_incognito:
                logger.info(f"Skipping summarization for conversation {conversation_id}")
                return {"conversation_id": conversation_id, "skipped": True}

            # Get messages
            stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
            result = await db.execute(stmt)
            messages = list(result.scalars().all())

            # Generate summary
            summary = await summarization_service.summarize_conversation(messages)
            conversation.summary = summary
            conversation.last_summarized_at = datetime.now(timezone.utc)

            await db.commit()

            logger.info(f"Completed conversation summarization for conversation {conversation_id}")

            return {"conversation_id": conversation_id, "message_count": len(messages), "success": True}

        except Exception as e:
            logger.error(f"Error summarizing conversation {conversation_id}: {e}")
            return {"conversation_id": conversation_id, "error": str(e), "success": False}


@celery_app.task(name="auto_extract_memories")
async def auto_extract_memories_task(conversation_id: int, user_id: int):
    """
    Background task to automatically extract memories from a conversation.

    Called after a conversation is completed or reaches a threshold.
    """
    logger.info(f"Starting memory extraction for conversation {conversation_id}")

    async with AsyncSessionLocal() as db:
        try:
            memories = await memory_service.auto_extract_memories_from_conversation(db, conversation_id, user_id)

            logger.info(f"Extracted {len(memories)} memories from conversation {conversation_id}")

            return {"conversation_id": conversation_id, "memories_created": len(memories), "success": True}

        except Exception as e:
            logger.error(f"Error extracting memories from conversation {conversation_id}: {e}")
            return {"conversation_id": conversation_id, "error": str(e), "success": False}


@celery_app.task(name="periodic_synthesis")
async def periodic_synthesis_task():
    """
    Periodic task to synthesize memories for all users and projects.

    Runs every 24 hours to update synthesis for projects that need it.
    """
    logger.info("Starting periodic memory synthesis for all users")

    async with AsyncSessionLocal() as db:
        try:
            # Get all projects that need synthesis
            threshold = datetime.now(timezone.utc) - timedelta(hours=settings.memory_synthesis_interval_hours)

            stmt = select(Project).where(
                and_(Project.memory_enabled == True, (Project.last_synthesis_at == None) | (Project.last_synthesis_at < threshold))
            )

            result = await db.execute(stmt)
            projects = result.scalars().all()

            synthesized_count = 0
            for project in projects:
                try:
                    await memory_service.synthesize_user_memories(db, project.user_id, project.id)
                    synthesized_count += 1
                except Exception as e:
                    logger.error(f"Error synthesizing project {project.id}: {e}")

            logger.info(f"Periodic synthesis completed: {synthesized_count} projects synthesized")

            return {"projects_synthesized": synthesized_count, "success": True}

        except Exception as e:
            logger.error(f"Error in periodic synthesis: {e}")
            return {"error": str(e), "success": False}


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    "periodic-memory-synthesis": {
        "task": "periodic_synthesis",
        "schedule": timedelta(hours=settings.memory_synthesis_interval_hours),
    },
}
