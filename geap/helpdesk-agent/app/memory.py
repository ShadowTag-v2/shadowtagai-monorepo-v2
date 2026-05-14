# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GEAP Part 3: Memory Bank Integration for the IT Helpdesk Agent.

Implements always-on memory using the Agent Platform Memory Bank
(VertexAiMemoryBankService) with a local InMemoryMemoryService fallback
for development. Provides:

1. Memory generation callback: Extracts facts from conversations and
   stores them for future retrieval across sessions.
2. Memory retrieval tools: PreloadMemoryTool (auto-load at turn start)
   and LoadMemoryTool (on-demand via model decision).
3. Custom memory search tool: Allows the agent to query memories
   with natural language when the built-in tools are insufficient.
4. Session management: VertexAiSessionService for cloud, InMemory
   for local dev.

Reference: https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# --- Feature flags ---
USE_VERTEX_MEMORY = os.environ.get("GEAP_USE_VERTEX_MEMORY", "false").lower() == "true"
AGENT_ENGINE_ID = os.environ.get("GEAP_AGENT_ENGINE_ID", "")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")


def get_memory_tools() -> list:
    """Return the appropriate memory tools based on deployment context.

    In production (USE_VERTEX_MEMORY=true), uses PreloadMemoryTool and
    LoadMemoryTool from ADK which connect to Vertex AI Memory Bank.

    In local dev, returns a custom search_user_preferences tool that
    queries in-memory state.

    Returns:
        List of ADK-compatible tool functions or Tool instances.
    """
    if USE_VERTEX_MEMORY:
        try:
            from google.adk.tools.load_memory_tool import LoadMemoryTool
            from google.adk.tools.preload_memory_tool import PreloadMemoryTool

            logger.info("Memory Bank: Using Vertex AI Memory Bank tools")
            return [PreloadMemoryTool(), LoadMemoryTool()]
        except ImportError:
            logger.warning(
                "Memory Bank: ADK memory tools not available, "
                "falling back to local memory"
            )

    # Local development fallback — in-memory store
    logger.info("Memory Bank: Using local in-memory fallback")
    return [search_user_preferences]


# --- In-Memory Fallback Store ---

_local_memory_store: dict[str, list[dict[str, Any]]] = {}


def _store_memory(user_id: str, fact: str, source: str = "conversation") -> None:
    """Store a memory fact for a user in the local fallback store.

    Args:
        user_id: Unique identifier for the user.
        fact: The extracted fact to remember.
        source: Where the fact came from (e.g., 'conversation', 'ticket').
    """
    if user_id not in _local_memory_store:
        _local_memory_store[user_id] = []
    _local_memory_store[user_id].append({
        "fact": fact,
        "source": source,
    })
    logger.debug("Stored memory for %s: %s", user_id, fact[:50])


def _search_memories(user_id: str, query: str) -> list[dict[str, Any]]:
    """Search stored memories for a user using keyword matching.

    Args:
        user_id: Unique identifier for the user.
        query: Natural language search query.

    Returns:
        List of matching memory dicts with 'fact' and 'source' keys.
    """
    memories = _local_memory_store.get(user_id, [])
    if not memories:
        return []

    query_lower = query.lower()
    query_terms = query_lower.split()

    scored = []
    for mem in memories:
        fact_lower = mem["fact"].lower()
        score = sum(1 for term in query_terms if term in fact_lower)
        if score > 0:
            scored.append((score, mem))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:5]]


def search_user_preferences(query: str, user_id: str = "default") -> str:
    """Search for previously stored user preferences and context.

    Use this tool when you need to recall information about a user's
    previous interactions, preferences, equipment, or past issues.

    Args:
        query: Natural language query about what to remember
            (e.g., "What laptop does this user have?").
        user_id: The user's identifier. Defaults to 'default'.

    Returns:
        A string with relevant memories or a message if none found.
    """
    results = _search_memories(user_id, query)
    if not results:
        return (
            f"No stored memories found for user '{user_id}' "
            f"matching '{query}'. This may be a new user or "
            "the topic hasn't been discussed before."
        )

    lines = [f"Found {len(results)} relevant memories for '{user_id}':"]
    for i, mem in enumerate(results, 1):
        lines.append(f"  {i}. {mem['fact']} (source: {mem['source']})")
    return "\n".join(lines)


# --- Memory Generation Callback ---

async def generate_memories_callback(callback_context: Any) -> None:
    """After-agent callback that triggers memory generation.

    In production: Uses callback_context.add_events_to_memory() to send
    the last 5 events to Vertex AI Memory Bank for background processing.

    In local dev: Extracts simple facts from the last exchange and
    stores them in the in-memory fallback.

    Args:
        callback_context: ADK CallbackContext with session and event access.
    """
    if USE_VERTEX_MEMORY:
        try:
            # Send last 5 events for incremental memory extraction
            events = callback_context.session.events[-5:-1]
            if events:
                await callback_context.add_events_to_memory(events=events)
                logger.info(
                    "Memory Bank: Sent %d events for memory generation",
                    len(events),
                )
        except Exception:
            logger.exception("Memory Bank: Failed to generate memories via Vertex AI")
        return

    # Local fallback — extract facts from the last assistant response
    try:
        session = callback_context.session
        user_id = getattr(session, "user_id", "default") or "default"
        events = session.events if hasattr(session, "events") else []

        for event in reversed(events[-4:]):
            if not hasattr(event, "content") or not event.content:
                continue
            if not hasattr(event.content, "parts"):
                continue

            for part in event.content.parts:
                text = getattr(part, "text", "") or ""
                if not text:
                    continue

                # Extract equipment mentions
                for keyword in ["laptop", "monitor", "phone", "printer", "headset"]:
                    if keyword in text.lower():
                        _store_memory(
                            user_id,
                            f"User discussed {keyword}: {text[:100]}",
                            source="conversation",
                        )
                        break

                # Extract ticket references
                if "INC-" in text:
                    _store_memory(
                        user_id,
                        f"Ticket interaction: {text[:100]}",
                        source="ticket",
                    )

    except Exception:
        logger.exception("Memory Bank: Local memory extraction failed")


# --- Session Service Factory ---

def get_session_service():
    """Create the appropriate session service for the deployment context.

    Returns:
        A session service instance (VertexAi or InMemory).
    """
    if USE_VERTEX_MEMORY and AGENT_ENGINE_ID:
        try:
            from google.adk.sessions import VertexAiSessionService

            logger.info("Sessions: Using Vertex AI Sessions (engine=%s)", AGENT_ENGINE_ID)
            return VertexAiSessionService(
                project=PROJECT_ID,
                location=LOCATION,
                agent_engine_id=AGENT_ENGINE_ID,
            )
        except ImportError:
            logger.warning("Sessions: VertexAiSessionService not available, using InMemory")

    from google.adk.sessions import InMemorySessionService

    logger.info("Sessions: Using InMemorySessionService for local development")
    return InMemorySessionService()


def get_memory_service():
    """Create the appropriate memory service for the deployment context.

    Returns:
        A memory service instance (VertexAi or InMemory).
    """
    if USE_VERTEX_MEMORY and AGENT_ENGINE_ID:
        try:
            from google.adk.memory import VertexAiMemoryBankService

            logger.info("Memory Service: Using Vertex AI Memory Bank (engine=%s)", AGENT_ENGINE_ID)
            return VertexAiMemoryBankService(
                project=PROJECT_ID,
                location=LOCATION,
                agent_engine_id=AGENT_ENGINE_ID,
            )
        except ImportError:
            logger.warning(
                "Memory Service: VertexAiMemoryBankService not available, using InMemory"
            )

    from google.adk.memory import InMemoryMemoryService

    logger.info("Memory Service: Using InMemoryMemoryService for local development")
    return InMemoryMemoryService()
