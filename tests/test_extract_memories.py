# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages/agnt_services/extract_memories.py."""

from __future__ import annotations

import pytest

from packages.agnt_services.extract_memories import (
    ExtractionResult,
    MemoryExtractor,
    count_model_visible_since,
    has_memory_writes_since,
    is_model_visible,
    is_tool_allowed_for_extraction,
)


def _msg(typ="user", uuid="u1", content=None):
    m = {"type": typ, "uuid": uuid}
    if content is not None:
        m["content"] = content
    return m


class TestIsModelVisible:
    def test_user(self):
        assert is_model_visible({"type": "user"}) is True

    def test_assistant(self):
        assert is_model_visible({"type": "assistant"}) is True

    def test_system(self):
        assert is_model_visible({"type": "system"}) is False


class TestCountModelVisible:
    def test_all_no_cursor(self):
        msgs = [_msg("user", "u1"), _msg("assistant", "a1"), _msg("system", "s1")]
        assert count_model_visible_since(msgs, None) == 2

    def test_after_cursor(self):
        msgs = [_msg("user", "u1"), _msg("assistant", "a1"), _msg("user", "u2")]
        assert count_model_visible_since(msgs, "u1") == 2

    def test_fallback_missing_cursor(self):
        msgs = [_msg("user", "u1")]
        assert count_model_visible_since(msgs, "missing") == 1


class TestHasMemoryWrites:
    def test_no_writes(self):
        msgs = [_msg("assistant", "a1", content=[{"type": "text"}])]
        assert has_memory_writes_since(msgs, None, lambda p: True) is False

    def test_write_detected(self):
        msgs = [
            _msg(
                "assistant",
                "a1",
                content=[
                    {
                        "type": "tool_use",
                        "name": "file_write",
                        "input": {"file_path": "/mem/note.md"},
                    }
                ],
            )
        ]
        assert has_memory_writes_since(msgs, None, lambda p: True) is True


class TestToolPermissions:
    def test_read_tools_allowed(self):
        assert is_tool_allowed_for_extraction("file_read", {}, "/mem") is True
        assert is_tool_allowed_for_extraction("grep", {}, "/mem") is True

    def test_bash_denied(self):
        assert is_tool_allowed_for_extraction("bash", {}, "/mem") is False

    def test_write_in_memdir(self):
        assert is_tool_allowed_for_extraction("file_write", {"file_path": "/mem/x.md"}, "/mem") is True

    def test_write_outside_memdir(self):
        assert is_tool_allowed_for_extraction("file_write", {"file_path": "/other/x.md"}, "/mem") is False


class TestMemoryExtractor:
    @pytest.mark.asyncio
    async def test_basic_run(self):
        ext = MemoryExtractor()
        result = await ext.run([_msg("user", "u1")])
        assert isinstance(result, ExtractionResult)
        assert result.skipped is False

    @pytest.mark.asyncio
    async def test_subagent_skipped(self):
        ext = MemoryExtractor()
        result = await ext.run([_msg()], is_subagent=True)
        assert result.skipped is True
        assert result.skip_reason == "subagent"

    @pytest.mark.asyncio
    async def test_overlap_coalesced(self):
        ext = MemoryExtractor()
        ext._in_progress = True
        result = await ext.run([_msg()])
        assert result.skipped is True
        assert result.skip_reason == "coalesced"
        ext._in_progress = False

    @pytest.mark.asyncio
    async def test_reset(self):
        ext = MemoryExtractor()
        await ext.run([_msg("user", "u1")])
        ext.reset()
        assert ext._last_cursor_uuid is None
        assert not ext.is_extracting

    @pytest.mark.asyncio
    async def test_drain_empty(self):
        ext = MemoryExtractor()
        await ext.drain(timeout=0.1)  # Should return immediately
