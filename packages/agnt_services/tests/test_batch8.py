# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Batch 8 unit tests + cross-service integration tests."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase


# ── Batch 8: MCP Channel Service ────────────────────────────────────


class TestMCPChannelService(TestCase):
    def test_short_request_id_length(self):
        from packages.agnt_services.mcp_channel_service import short_request_id

        rid = short_request_id("toolu_abc123def456")
        assert len(rid) == 5
        assert rid.isalpha()
        assert "l" not in rid  # no 'l' in alphabet

    def test_short_request_id_deterministic(self):
        from packages.agnt_services.mcp_channel_service import short_request_id

        a = short_request_id("toolu_test_id_1")
        b = short_request_id("toolu_test_id_1")
        assert a == b

    def test_short_request_id_unique(self):
        from packages.agnt_services.mcp_channel_service import short_request_id

        ids = {short_request_id(f"toolu_{i}") for i in range(100)}
        assert len(ids) > 90  # very high uniqueness

    def test_truncate_for_preview(self):
        from packages.agnt_services.mcp_channel_service import truncate_for_preview

        short = truncate_for_preview({"key": "value"})
        assert len(short) < 200
        long_input = {"key": "x" * 500}
        result = truncate_for_preview(long_input)
        assert result.endswith("…")

    def test_channel_allowlist(self):
        from packages.agnt_services.mcp_channel_service import ChannelAllowlist

        al = ChannelAllowlist(enabled=True)
        assert not al.is_allowed("telegram")
        al.add("telegram")
        assert al.is_allowed("telegram")
        al.clear()
        assert not al.is_allowed("telegram")

    def test_channel_allowlist_disabled(self):
        from packages.agnt_services.mcp_channel_service import ChannelAllowlist

        al = ChannelAllowlist(enabled=False)
        al.add("telegram")
        assert not al.is_allowed("telegram")

    def test_permission_callbacks_resolve(self):
        from packages.agnt_services.mcp_channel_service import ChannelPermissionCallbacks

        cb = ChannelPermissionCallbacks()
        results = []
        cb.on_response("req1", lambda r: results.append(r.behavior))
        assert cb.pending_count == 1
        resolved = cb.resolve("req1", "allow", "plugin:telegram:tg")
        assert resolved
        assert results == ["allow"]
        assert cb.pending_count == 0

    def test_permission_callbacks_unknown_id(self):
        from packages.agnt_services.mcp_channel_service import ChannelPermissionCallbacks

        cb = ChannelPermissionCallbacks()
        assert not cb.resolve("nonexistent", "deny", "test")

    def test_filter_permission_relay_clients(self):
        from packages.agnt_services.mcp_channel_service import filter_permission_relay_clients

        clients = [
            {
                "type": "connected",
                "name": "telegram",
                "capabilities": {
                    "experimental": {
                        "claude/channel": True,
                        "claude/channel/permission": True,
                    }
                },
            },
            {"type": "disconnected", "name": "discord"},
            {
                "type": "connected",
                "name": "slack",
                "capabilities": {"experimental": {"claude/channel": True}},
            },
        ]
        result = filter_permission_relay_clients(clients, lambda n: n in ("telegram", "slack"))
        assert len(result) == 1
        assert result[0]["name"] == "telegram"

    def test_permission_reply_regex(self):
        from packages.agnt_services.mcp_channel_service import PERMISSION_REPLY_RE

        assert PERMISSION_REPLY_RE.match("yes abcde")
        assert PERMISSION_REPLY_RE.match("no fghij")
        assert PERMISSION_REPLY_RE.match("Y abcde")
        assert not PERMISSION_REPLY_RE.match("maybe abcde")
        assert not PERMISSION_REPLY_RE.match("yes")  # no ID


# ── Batch 8: Session Memory Service ─────────────────────────────────


class TestSessionMemoryService(TestCase):
    def test_count_tool_calls_since(self):
        from packages.agnt_services.session_memory_service import (
            Message,
            count_tool_calls_since,
        )

        msgs = [
            Message(uuid="1", type="user"),
            Message(uuid="2", type="assistant", tool_calls=[{"name": "read"}]),
            Message(uuid="3", type="assistant", tool_calls=[{"name": "write"}, {"name": "edit"}]),
        ]
        assert count_tool_calls_since(msgs, None) == 3
        assert count_tool_calls_since(msgs, "1") == 3
        assert count_tool_calls_since(msgs, "2") == 2

    def test_should_extract_below_threshold(self):
        from packages.agnt_services.session_memory_service import (
            Message,
            SessionMemoryState,
            should_extract_memory,
        )

        state = SessionMemoryState()
        msgs = [Message(uuid="1", type="user")]
        assert not should_extract_memory(msgs, 5000, state)
        assert not state.initialized

    def test_should_extract_above_threshold(self):
        from packages.agnt_services.session_memory_service import (
            Message,
            SessionMemoryState,
            SessionMemoryConfig,
            should_extract_memory,
        )

        config = SessionMemoryConfig(
            initialization_threshold=100,
            minimum_tokens_between_update=50,
            tool_calls_between_updates=1,
        )
        state = SessionMemoryState(config=config)
        msgs = [
            Message(uuid="1", type="user"),
            Message(uuid="2", type="assistant", tool_calls=[{"name": "x"}]),
        ]
        # First call initializes baseline at 200 tokens
        should_extract_memory(msgs, 200, state)
        assert state.initialized
        # Second call with sufficient growth triggers extraction
        result = should_extract_memory(msgs, 260, state)
        assert result

    def test_memory_file_ops(self):
        from packages.agnt_services.session_memory_service import (
            load_session_memory,
            save_session_memory,
        )

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / ".claude" / "session_memory.md"
            assert load_session_memory(path) is None
            assert save_session_memory(path, "# Test Memory")
            assert load_session_memory(path) == "# Test Memory"

    def test_service_lifecycle(self):
        from packages.agnt_services.session_memory_service import (
            SessionMemoryService,
            SessionMemoryConfig,
            Message,
        )

        with tempfile.TemporaryDirectory() as td:
            config = SessionMemoryConfig(
                initialization_threshold=100,
                minimum_tokens_between_update=50,
                tool_calls_between_updates=1,
            )
            svc = SessionMemoryService(td, config=config)
            msgs = [
                Message(uuid="1", type="user"),
                Message(uuid="2", type="assistant", tool_calls=[{"t": 1}]),
            ]
            # First call initializes baseline
            svc.check_and_extract(msgs, 200)
            # Second call with growth triggers extraction
            triggered = svc.check_and_extract(msgs, 260)
            assert triggered
            assert svc.state.extraction_count == 1
            svc.reset()
            assert svc.state.extraction_count == 0


# ── Batch 8: Extract Memories Service ────────────────────────────────


class TestExtractMemoriesService(TestCase):
    def test_count_model_visible(self):
        from packages.agnt_services.extract_memories_service import (
            MemoryMessage,
            count_model_visible_since,
        )

        msgs = [
            MemoryMessage(uuid="1", type="user"),
            MemoryMessage(uuid="2", type="assistant"),
            MemoryMessage(uuid="3", type="system"),
            MemoryMessage(uuid="4", type="user"),
        ]
        assert count_model_visible_since(msgs, None) == 3
        assert count_model_visible_since(msgs, "2") == 1
        # UUID not found -> fallback to counting all
        assert count_model_visible_since(msgs, "nonexistent") == 3

    def test_can_use_tool_sandbox(self):
        from packages.agnt_services.extract_memories_service import can_use_tool_for_extraction

        allowed, _ = can_use_tool_for_extraction("file_read", {}, "/mem")
        assert allowed
        allowed, _ = can_use_tool_for_extraction("grep", {}, "/mem")
        assert allowed
        allowed, _ = can_use_tool_for_extraction("file_write", {"file_path": "/mem/note.md"}, "/mem")
        assert allowed
        allowed, _ = can_use_tool_for_extraction("file_write", {"file_path": "/etc/passwd"}, "/mem")
        assert not allowed
        allowed, _ = can_use_tool_for_extraction("bash", {"command": "rm -rf /"}, "/mem")
        assert not allowed

    def test_should_extract_threshold(self):
        from packages.agnt_services.extract_memories_service import (
            ExtractMemoriesService,
            ExtractMemoriesConfig,
            MemoryMessage,
        )

        with tempfile.TemporaryDirectory() as td:
            config = ExtractMemoriesConfig(
                min_messages_for_first_extraction=2,
                cooldown_seconds=0,
            )
            svc = ExtractMemoriesService(td, config=config)
            msgs = [
                MemoryMessage(uuid="1", type="user"),
                MemoryMessage(uuid="2", type="assistant"),
                MemoryMessage(uuid="3", type="user"),
            ]
            assert svc.should_extract(msgs)
            svc.mark_extraction_complete(msgs)
            assert svc.state.extraction_count == 1

    def test_scan_memory_files(self):
        from packages.agnt_services.extract_memories_service import ExtractMemoriesService

        with tempfile.TemporaryDirectory() as td:
            svc = ExtractMemoriesService(td)
            Path(td, "note1.md").write_text("# Note 1")
            Path(td, "note2.md").write_text("# Note 2")
            Path(td, "ignore.txt").write_text("not md")
            entries = svc.scan_memory_files()
            assert len(entries) == 2


# ── Batch 8: Token Estimation Service ────────────────────────────────


class TestTokenEstimationService(TestCase):
    def test_estimate_tokens_from_text(self):
        from packages.agnt_services.token_estimation_service import estimate_tokens_from_text

        assert estimate_tokens_from_text("") == 0
        tokens = estimate_tokens_from_text("Hello world")
        assert tokens > 0
        code_tokens = estimate_tokens_from_text("def foo(): pass", "code")
        assert code_tokens > 0

    def test_strip_tool_search_fields(self):
        from packages.agnt_services.token_estimation_service import strip_tool_search_fields

        msgs = [
            {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": "1", "name": "read", "input": {}, "caller": "extra"},
                ],
            }
        ]
        cleaned = strip_tool_search_fields(msgs)
        assert "caller" not in cleaned[0]["content"][0]

    def test_estimate_message_tokens(self):
        from packages.agnt_services.token_estimation_service import estimate_message_tokens

        msgs = [
            {"role": "user", "content": "Hello world, this is a test message."},
            {"role": "assistant", "content": "I can help with that."},
        ]
        tokens = estimate_message_tokens(msgs)
        assert tokens > 10

    def test_service_count_and_cache(self):
        from packages.agnt_services.token_estimation_service import TokenEstimationService

        svc = TokenEstimationService()
        r1 = svc.count_tokens("test content")
        assert r1.input_tokens > 0
        r2 = svc.count_tokens("test content")
        assert r2.source == "cache"
        assert r1.input_tokens == r2.input_tokens
        svc.clear_cache()
        r3 = svc.count_tokens("test content")
        assert r3.source == "estimate"


# ── Batch 8: Team Memory Sync Service ────────────────────────────────


class TestTeamMemorySyncService(TestCase):
    def test_hash_content_deterministic(self):
        from packages.agnt_services.team_memory_sync_service import hash_content

        h1 = hash_content("test data")
        h2 = hash_content("test data")
        assert h1 == h2
        assert h1.startswith("sha256:")

    def test_scan_for_secrets(self):
        from packages.agnt_services.team_memory_sync_service import scan_for_secrets

        clean = scan_for_secrets("Just some normal text")
        assert not clean.has_secrets
        dirty = scan_for_secrets("api_key: sk-1234567890abcdefghijklmnop")
        assert dirty.has_secrets

    def test_read_local_team_memory(self):
        from packages.agnt_services.team_memory_sync_service import (
            read_local_team_memory,
            create_sync_state,
        )

        with tempfile.TemporaryDirectory() as td:
            Path(td, "note.md").write_text("# Team note")
            Path(td, "secret.md").write_text("api_key = sk-secretkey123456789012345")
            state = create_sync_state()
            entries, skipped = read_local_team_memory(Path(td), state)
            assert len(entries) == 1
            assert entries[0].key == "note.md"
            assert len(skipped) == 1

    def test_compute_push_delta(self):
        from packages.agnt_services.team_memory_sync_service import (
            TeamMemoryEntry,
            compute_push_delta,
            create_sync_state,
            hash_content,
        )

        state = create_sync_state()
        state.server_checksums["old.md"] = hash_content("old content")
        entries = [
            TeamMemoryEntry(key="old.md", content="old content", checksum=hash_content("old content")),
            TeamMemoryEntry(key="new.md", content="new content", checksum=hash_content("new content")),
        ]
        delta = compute_push_delta(entries, state)
        assert len(delta) == 1
        assert delta[0].key == "new.md"

    def test_batch_entries_for_push(self):
        from packages.agnt_services.team_memory_sync_service import (
            TeamMemoryEntry,
            batch_entries_for_push,
        )

        entries = [TeamMemoryEntry(key=f"file{i}.md", content="x" * 50000, checksum="sha256:test") for i in range(5)]
        batches = batch_entries_for_push(entries)
        assert len(batches) > 1  # should split across gateway limit

    def test_apply_pull_to_local(self):
        from packages.agnt_services.team_memory_sync_service import (
            apply_pull_to_local,
            create_sync_state,
        )

        with tempfile.TemporaryDirectory() as td:
            state = create_sync_state()
            server_entries = [
                {"key": "pulled.md", "content": "# From server", "checksum": "sha256:abc"},
            ]
            written = apply_pull_to_local(Path(td), server_entries, state)
            assert written == 1
            assert (Path(td) / "pulled.md").read_text() == "# From server"
            assert state.server_checksums["pulled.md"] == "sha256:abc"

    def test_service_prepare_push(self):
        from packages.agnt_services.team_memory_sync_service import TeamMemorySyncService

        with tempfile.TemporaryDirectory() as td:
            Path(td, "note.md").write_text("# Note")
            svc = TeamMemorySyncService(td)
            batches, skipped = svc.prepare_push()
            assert len(batches) == 1
            assert len(batches[0]) == 1

    def test_service_reset(self):
        from packages.agnt_services.team_memory_sync_service import TeamMemorySyncService

        with tempfile.TemporaryDirectory() as td:
            svc = TeamMemorySyncService(td)
            svc.state.last_known_checksum = "test"
            svc.reset()
            assert svc.state.last_known_checksum is None


# ── Cross-Service Integration Tests ─────────────────────────────────


class TestCrossServiceIntegration(TestCase):
    def test_oauth_to_settings_to_orchestration_flow(self):
        """Integration: OAuth generates PKCE → Settings caches it → Tool runs."""
        from packages.agnt_services.oauth_service import (
            generate_code_verifier,
            generate_code_challenge,
        )
        from packages.agnt_services.remote_managed_settings import RemoteManagedSettingsService
        from packages.agnt_services.tool_orchestration import partition_tool_calls, ToolUseBlock

        # Step 1: OAuth generates PKCE challenge
        verifier = generate_code_verifier()
        challenge = generate_code_challenge(verifier)
        assert len(verifier) > 40
        assert challenge != verifier

        # Step 2: Settings service caches the PKCE verifier
        with tempfile.TemporaryDirectory() as td:
            settings_path = Path(td) / "settings.json"
            svc = RemoteManagedSettingsService(settings_path=settings_path)
            svc.save_settings({"pkce_verifier": verifier, "challenge": challenge})
            loaded = svc.load_cached_settings()
            assert loaded["pkce_verifier"] == verifier

        # Step 3: Tool orchestration partitions work
        tool_blocks = [
            ToolUseBlock(id="1", name="oauth_validate", input={}),
            ToolUseBlock(id="2", name="settings_apply", input={}),
            ToolUseBlock(id="3", name="cache_clear", input={}),
        ]
        batches = partition_tool_calls(tool_blocks)
        assert len(batches) > 0

    def test_memory_extraction_with_token_estimation(self):
        """Integration: Token estimation drives memory extraction timing."""
        from packages.agnt_services.session_memory_service import (
            SessionMemoryService,
            SessionMemoryConfig,
            Message,
        )
        from packages.agnt_services.token_estimation_service import TokenEstimationService

        token_svc = TokenEstimationService()
        config = SessionMemoryConfig(
            initialization_threshold=10,
            minimum_tokens_between_update=5,
            tool_calls_between_updates=1,
        )

        with tempfile.TemporaryDirectory() as td:
            memory_svc = SessionMemoryService(td, config=config)
            conversation = "This is a long conversation about Python development patterns."
            token_count = token_svc.count_tokens(conversation)
            msgs = [
                Message(uuid="1", type="user"),
                Message(uuid="2", type="assistant", tool_calls=[{"n": "r"}]),
            ]
            # First call initializes baseline
            memory_svc.check_and_extract(msgs, token_count.input_tokens)
            # Second call with growth triggers
            triggered = memory_svc.check_and_extract(msgs, token_count.input_tokens + 10)
            assert triggered

    def test_team_sync_with_secret_scanning(self):
        """Integration: Team sync blocks files containing secrets."""
        from packages.agnt_services.team_memory_sync_service import TeamMemorySyncService

        with tempfile.TemporaryDirectory() as td:
            # Clean file passes
            Path(td, "clean.md").write_text("# Architecture decisions\nUse microservices.")
            # Secret file blocked
            Path(td, "leaked.md").write_text("api_key: sk-proj-abcdefghijklmnopqrstuvwx")
            svc = TeamMemorySyncService(td)
            batches, skipped = svc.prepare_push()
            # Only clean file in batches
            all_keys = [e.key for batch in batches for e in batch]
            assert "clean.md" in all_keys
            assert "leaked.md" not in all_keys
            assert len(skipped) == 1
