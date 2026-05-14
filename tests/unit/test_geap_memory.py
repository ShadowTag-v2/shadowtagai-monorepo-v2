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

"""Unit tests for GEAP Part 3: Memory Bank integration.

Tests the memory module's local fallback functionality including:
- Memory storage and retrieval
- Keyword-based memory search
- Memory generation callback (local fallback)
- Session and memory service factory functions
- Memory tools resolution
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


def _load_memory_module() -> ModuleType:
    """Load the memory module without triggering __init__.py ADK imports."""
    module_path = (
        Path(__file__).resolve().parents[2]
        / "geap"
        / "helpdesk-agent"
        / "app"
        / "memory.py"
    )
    spec = importlib.util.spec_from_file_location("geap_memory", str(module_path))
    if spec is None or spec.loader is None:
        pytest.skip(f"Cannot load memory module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["geap_memory"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def memory_module():
    """Load and return the memory module, clearing state between tests."""
    mod = _load_memory_module()
    # Clear the in-memory store between tests
    mod._local_memory_store.clear()
    return mod


# --- Memory Store Tests ---


class TestMemoryStorage:
    """Tests for the in-memory fallback store."""

    def test_store_memory_creates_user_entry(self, memory_module):
        memory_module._store_memory("user1", "Uses MacBook Pro M4")
        assert "user1" in memory_module._local_memory_store
        assert len(memory_module._local_memory_store["user1"]) == 1

    def test_store_memory_appends_facts(self, memory_module):
        memory_module._store_memory("user1", "Fact 1")
        memory_module._store_memory("user1", "Fact 2")
        assert len(memory_module._local_memory_store["user1"]) == 2

    def test_store_memory_preserves_source(self, memory_module):
        memory_module._store_memory("user1", "A fact", source="ticket")
        mem = memory_module._local_memory_store["user1"][0]
        assert mem["source"] == "ticket"

    def test_store_memory_default_source(self, memory_module):
        memory_module._store_memory("user1", "A fact")
        mem = memory_module._local_memory_store["user1"][0]
        assert mem["source"] == "conversation"

    def test_store_memory_isolates_users(self, memory_module):
        memory_module._store_memory("user1", "Fact A")
        memory_module._store_memory("user2", "Fact B")
        assert len(memory_module._local_memory_store["user1"]) == 1
        assert len(memory_module._local_memory_store["user2"]) == 1
        assert memory_module._local_memory_store["user1"][0]["fact"] == "Fact A"
        assert memory_module._local_memory_store["user2"][0]["fact"] == "Fact B"


# --- Memory Search Tests ---


class TestMemorySearch:
    """Tests for keyword-based memory search."""

    def test_search_empty_store(self, memory_module):
        results = memory_module._search_memories("user1", "laptop")
        assert results == []

    def test_search_no_matches(self, memory_module):
        memory_module._store_memory("user1", "Uses Windows desktop")
        results = memory_module._search_memories("user1", "macbook")
        assert results == []

    def test_search_finds_keyword_match(self, memory_module):
        memory_module._store_memory("user1", "User has a MacBook Pro laptop")
        results = memory_module._search_memories("user1", "laptop")
        assert len(results) == 1
        assert "MacBook Pro laptop" in results[0]["fact"]

    def test_search_ranks_by_relevance(self, memory_module):
        memory_module._store_memory("user1", "Uses VPN daily")
        memory_module._store_memory("user1", "VPN disconnects frequently on laptop")
        results = memory_module._search_memories("user1", "VPN laptop")
        # The second fact matches both "VPN" and "laptop"
        assert len(results) == 2
        assert "disconnects" in results[0]["fact"]  # Higher score

    def test_search_limits_results_to_five(self, memory_module):
        for i in range(10):
            memory_module._store_memory("user1", f"Network issue #{i}")
        results = memory_module._search_memories("user1", "network")
        assert len(results) == 5

    def test_search_case_insensitive(self, memory_module):
        memory_module._store_memory("user1", "MACBOOK PRO M4")
        results = memory_module._search_memories("user1", "macbook")
        assert len(results) == 1

    def test_search_wrong_user(self, memory_module):
        memory_module._store_memory("user1", "Has a laptop")
        results = memory_module._search_memories("user2", "laptop")
        assert results == []


# --- search_user_preferences Tool Tests ---


class TestSearchUserPreferences:
    """Tests for the ADK-compatible search tool."""

    def test_no_memories_returns_message(self, memory_module):
        result = memory_module.search_user_preferences("laptop", user_id="new_user")
        assert "No stored memories" in result
        assert "new_user" in result

    def test_found_memories_returns_list(self, memory_module):
        memory_module._store_memory("user1", "User has ThinkPad X1 laptop")
        result = memory_module.search_user_preferences("laptop", user_id="user1")
        assert "1 relevant memories" in result
        assert "ThinkPad" in result

    def test_default_user_id(self, memory_module):
        memory_module._store_memory("default", "Default user fact")
        result = memory_module.search_user_preferences("fact")
        assert "Default user fact" in result

    def test_includes_source(self, memory_module):
        memory_module._store_memory("user1", "Ticket INC-123", source="ticket")
        result = memory_module.search_user_preferences("ticket", user_id="user1")
        assert "source: ticket" in result


# --- Memory Generation Callback Tests ---


class TestGenerateMemoriesCallback:
    """Tests for the after-agent memory generation callback."""

    @pytest.mark.asyncio
    async def test_callback_extracts_laptop_mention(self, memory_module):
        """Callback should extract equipment mentions from events."""
        # Build a mock session with an event mentioning a laptop
        part = MagicMock()
        part.text = "I need help with my laptop, it's running slow"

        content = MagicMock()
        content.parts = [part]

        event = MagicMock()
        event.content = content

        session = MagicMock()
        session.user_id = "test_user"
        session.events = [event]

        ctx = MagicMock()
        ctx.session = session

        # Ensure local fallback is used
        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            await memory_module.generate_memories_callback(ctx)

        memories = memory_module._local_memory_store.get("test_user", [])
        assert len(memories) >= 1
        assert any("laptop" in m["fact"].lower() for m in memories)

    @pytest.mark.asyncio
    async def test_callback_extracts_ticket_reference(self, memory_module):
        """Callback should extract ticket references from events."""
        part = MagicMock()
        part.text = "Ticket INC-ABC12345 has been created for your issue"

        content = MagicMock()
        content.parts = [part]

        event = MagicMock()
        event.content = content

        session = MagicMock()
        session.user_id = "test_user"
        session.events = [event]

        ctx = MagicMock()
        ctx.session = session

        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            await memory_module.generate_memories_callback(ctx)

        memories = memory_module._local_memory_store.get("test_user", [])
        ticket_mems = [m for m in memories if m["source"] == "ticket"]
        assert len(ticket_mems) >= 1

    @pytest.mark.asyncio
    async def test_callback_handles_empty_events(self, memory_module):
        """Callback should not crash on empty event list."""
        session = MagicMock()
        session.user_id = "test_user"
        session.events = []

        ctx = MagicMock()
        ctx.session = session

        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            await memory_module.generate_memories_callback(ctx)

        # No crash, no memories stored
        assert memory_module._local_memory_store.get("test_user") is None

    @pytest.mark.asyncio
    async def test_callback_handles_no_text_parts(self, memory_module):
        """Callback should skip events without text parts."""
        part = MagicMock()
        part.text = None

        content = MagicMock()
        content.parts = [part]

        event = MagicMock()
        event.content = content

        session = MagicMock()
        session.user_id = "test_user"
        session.events = [event]

        ctx = MagicMock()
        ctx.session = session

        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            await memory_module.generate_memories_callback(ctx)

        # No crash, no memories stored
        assert memory_module._local_memory_store.get("test_user") is None

    @pytest.mark.asyncio
    async def test_callback_defaults_user_id(self, memory_module):
        """Callback should use 'default' if user_id is missing."""
        part = MagicMock()
        part.text = "My monitor is flickering"

        content = MagicMock()
        content.parts = [part]

        event = MagicMock()
        event.content = content

        session = MagicMock()
        session.user_id = None
        session.events = [event]

        ctx = MagicMock()
        ctx.session = session

        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            await memory_module.generate_memories_callback(ctx)

        assert "default" in memory_module._local_memory_store


# --- Service Factory Tests ---


class TestServiceFactories:
    """Tests for session and memory service factory functions."""

    def test_get_memory_tools_local(self, memory_module):
        """Local mode should return the search_user_preferences function."""
        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            tools = memory_module.get_memory_tools()
        assert len(tools) == 1
        assert tools[0] == memory_module.search_user_preferences

    def test_get_session_service_local(self, memory_module):
        """Local mode should return InMemorySessionService or raise if ADK missing."""
        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            try:
                service = memory_module.get_session_service()
                assert service is not None
                assert "InMemory" in type(service).__name__
            except ModuleNotFoundError:
                # ADK not installed in this environment — expected
                pytest.skip("google.adk not installed")

    def test_get_memory_service_local(self, memory_module):
        """Local mode should return InMemoryMemoryService or raise if ADK missing."""
        with patch.object(memory_module, "USE_VERTEX_MEMORY", False):
            try:
                service = memory_module.get_memory_service()
                assert service is not None
                assert "InMemory" in type(service).__name__
            except ModuleNotFoundError:
                # ADK not installed in this environment — expected
                pytest.skip("google.adk not installed")

    def test_get_memory_tools_vertex_without_import(self, memory_module):
        """Should fall back to local if ADK memory tools can't be imported."""
        with patch.object(memory_module, "USE_VERTEX_MEMORY", True):
            with patch.dict("sys.modules", {
                "google.adk.tools.load_memory_tool": None,
                "google.adk.tools.preload_memory_tool": None,
            }):
                tools = memory_module.get_memory_tools()
        # Falls back to local tool
        assert len(tools) == 1
