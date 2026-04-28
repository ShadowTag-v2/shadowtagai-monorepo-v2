# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""GPTRAM - GPT Retrieval Augmented Memory
Temporal agent memory with Redis backend
"""

import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as redis

from app.config.settings import settings

logger = logging.getLogger(__name__)


class GPTRAMMemory:
    """Temporal agent memory storage with retrieval capabilities"""

    def __init__(self):
        self.redis_client: redis.Redis | None = None
        self.memory_ttl = 86400  # 24 hours default TTL

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("✅ GPTRAM memory initialized with Redis")
        except Exception as e:
            logger.error(f"Failed to initialize GPTRAM: {e}")
            raise

    async def shutdown(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("GPTRAM memory connection closed")

    async def store_interaction(
        self,
        session_id: str,
        interaction: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """Store an interaction in temporal memory

        Args:
            session_id: Unique session identifier
            interaction: Interaction data to store
            ttl: Time to live in seconds

        Returns:
            Success status

        """
        try:
            key = f"gptram:session:{session_id}:{interaction.get('timestamp', datetime.utcnow().isoformat())}"
            interaction_data = {**interaction, "stored_at": datetime.utcnow().isoformat()}

            await self.redis_client.setex(key, ttl or self.memory_ttl, json.dumps(interaction_data))

            # Add to session index
            await self.redis_client.zadd(
                f"gptram:index:{session_id}",
                {key: datetime.utcnow().timestamp()},
            )

            return True
        except Exception as e:
            logger.error(f"Failed to store interaction: {e}")
            return False

    async def retrieve_session_history(
        self,
        session_id: str,
        limit: int = 100,
        min_timestamp: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve session interaction history

        Args:
            session_id: Session identifier
            limit: Maximum number of interactions to retrieve
            min_timestamp: Minimum timestamp for filtering

        Returns:
            List of interactions

        """
        try:
            # Get keys from session index
            min_score = min_timestamp.timestamp() if min_timestamp else 0
            keys = await self.redis_client.zrangebyscore(
                f"gptram:index:{session_id}",
                min_score,
                "+inf",
                start=0,
                num=limit,
            )

            # Retrieve interaction data
            interactions = []
            for key in keys:
                data = await self.redis_client.get(key)
                if data:
                    interactions.append(json.loads(data))

            return interactions
        except Exception as e:
            logger.error(f"Failed to retrieve session history: {e}")
            return []

    async def store_reasoning_graph(self, session_id: str, graph: dict[str, Any]) -> bool:
        """Store reasoning graph for RoT (Retrieval-of-Thought)

        Args:
            session_id: Session identifier
            graph: Reasoning graph structure

        Returns:
            Success status

        """
        try:
            key = f"gptram:rot:graph:{session_id}"
            await self.redis_client.setex(key, self.memory_ttl, json.dumps(graph))
            logger.debug(f"Stored reasoning graph for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store reasoning graph: {e}")
            return False

    async def retrieve_reasoning_graph(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve reasoning graph for RoT

        Args:
            session_id: Session identifier

        Returns:
            Reasoning graph or None

        """
        try:
            key = f"gptram:rot:graph:{session_id}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to retrieve reasoning graph: {e}")
            return None

    async def get_memory_stats(self, session_id: str) -> dict[str, Any]:
        """Get memory statistics for a session"""
        try:
            interaction_count = await self.redis_client.zcard(f"gptram:index:{session_id}")
            has_reasoning_graph = await self.redis_client.exists(f"gptram:rot:graph:{session_id}")

            return {
                "session_id": session_id,
                "interaction_count": interaction_count,
                "has_reasoning_graph": bool(has_reasoning_graph),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
