# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for context_compactor.conversation_compact.

Covers:
  - Image/document stripping from messages
  - Reinjected attachment stripping
  - PTL retry with head truncation
  - Compact boundary message creation and detection
  - Full compact_conversation orchestrator (happy path + error paths)
  - Partial compact_conversation (UP_TO and FROM directions)
  - Token truncation
  - File path collection
  - Exclusion filter
  - summarize_fn error handling
"""

from __future__ import annotations

import uuid

import pytest

from context_compactor.conversation_compact import (
    CompactDirection,
    ConversationCompactionResult,
    PromptTooLongError,
    build_post_compact_messages,
    collect_read_tool_file_paths,
    compact_conversation,
    get_assistant_message_text,
    get_messages_after_compact_boundary,
    is_compact_boundary_message,
    merge_hook_instructions,
    partial_compact_conversation,
    should_exclude_from_restore,
    strip_images_from_messages,
    strip_reinjected_attachments,
    truncate_head_for_ptl_retry,
    truncate_to_tokens,
    PTL_RETRY_MARKER,
    _create_compact_boundary_message,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _msg(role: str, content: str | list, **kwargs) -> dict:
    """Create a minimal message dict."""
    return {"role": role, "content": content, "uuid": str(uuid.uuid4()), **kwargs}


def _user(text: str, **kwargs) -> dict:
    return _msg("user", text, **kwargs)


def _assistant(text: str, msg_id: str | None = None) -> dict:
    m = _msg("assistant", text)
    if msg_id:
        m["message"] = {"id": msg_id}
    return m


def _simple_conversation(n: int = 10) -> list[dict]:
    """Generate n user-assistant pairs."""
    msgs = []
    for i in range(n):
        msgs.append(_user(f"Question {i}"))
        msgs.append(_assistant(f"Answer {i}", msg_id=f"msg-{i}"))
    return msgs


def _mock_summarize(summary: str = "This is a summary."):
    """Return a summarize_fn that returns a fixed summary."""

    def _fn(messages, prompt):
        return summary

    return _fn


def _mock_summarize_ptl(fail_n: int = 1, summary: str = "Recovered summary."):
    """Return a summarize_fn that raises PTL n times then succeeds."""
    call_count = {"n": 0}

    def _fn(messages, prompt):
        call_count["n"] += 1
        if call_count["n"] <= fail_n:
            resp = {"role": "assistant", "content": "Error: prompt too long by 5000 tokens"}
            raise PromptTooLongError("too long", response=resp)
        return summary

    return _fn


def _mock_summarize_always_ptl():
    """Return a summarize_fn that always raises PTL."""

    def _fn(messages, prompt):
        resp = {"role": "assistant", "content": "Error: prompt too long by 5000 tokens"}
        raise PromptTooLongError("too long", response=resp)

    return _fn


def _mock_summarize_raises(exc_type=RuntimeError, msg="API error"):
    """Return a summarize_fn that raises an unexpected error."""

    def _fn(messages, prompt):
        raise exc_type(msg)

    return _fn


# ── strip_images_from_messages ────────────────────────────────────────────────


class TestStripImagesFromMessages:
    def test_no_images_passthrough(self):
        msgs = [_user("hello"), _assistant("world")]
        result = strip_images_from_messages(msgs)
        assert len(result) == 2
        assert result[0]["content"] == "hello"

    def test_strips_image_blocks(self):
        msg = _msg(
            "user",
            [
                {"type": "text", "text": "Look at this:"},
                {"type": "image", "source": {"data": "base64..."}},
            ],
        )
        result = strip_images_from_messages([msg])
        assert len(result) == 1
        blocks = result[0]["content"]
        assert len(blocks) == 2
        assert blocks[1] == {"type": "text", "text": "[image]"}

    def test_strips_document_blocks(self):
        msg = _msg(
            "user",
            [
                {"type": "text", "text": "Check this doc:"},
                {"type": "document", "source": {"data": "pdf..."}},
            ],
        )
        result = strip_images_from_messages([msg])
        blocks = result[0]["content"]
        assert blocks[1] == {"type": "text", "text": "[document]"}

    def test_strips_images_in_tool_results(self):
        msg = _msg(
            "user",
            [
                {
                    "type": "tool_result",
                    "tool_use_id": "t1",
                    "content": [
                        {"type": "text", "text": "result text"},
                        {"type": "image", "source": {"data": "base64..."}},
                    ],
                },
            ],
        )
        result = strip_images_from_messages([msg])
        tool_result = result[0]["content"][0]
        assert tool_result["content"][1] == {"type": "text", "text": "[image]"}

    def test_does_not_modify_assistant_messages(self):
        msg = _msg(
            "assistant",
            [
                {"type": "text", "text": "Some response"},
                {"type": "image", "source": {"data": "base64..."}},
            ],
        )
        result = strip_images_from_messages([msg])
        # Assistant messages are passed through unchanged
        assert result[0]["content"] == msg["content"]

    def test_string_content_passthrough(self):
        msg = _user("plain text")
        result = strip_images_from_messages([msg])
        assert result[0]["content"] == "plain text"


# ── strip_reinjected_attachments ──────────────────────────────────────────────


class TestStripReinjectedAttachments:
    def test_strips_skill_discovery(self):
        msgs = [
            _user("question"),
            {"role": "attachment", "attachment": {"type": "skill_discovery"}, "content": "..."},
            _assistant("answer"),
        ]
        result = strip_reinjected_attachments(msgs)
        assert len(result) == 2
        assert result[0]["content"] == "question"

    def test_strips_skill_listing(self):
        msgs = [
            {"role": "attachment", "attachment": {"type": "skill_listing"}, "content": "..."},
            _user("question"),
        ]
        result = strip_reinjected_attachments(msgs)
        assert len(result) == 1

    def test_keeps_other_attachments(self):
        msgs = [
            {"role": "attachment", "attachment": {"type": "file"}, "content": "..."},
            _user("question"),
        ]
        result = strip_reinjected_attachments(msgs)
        assert len(result) == 2


# ── is_compact_boundary_message / get_messages_after_compact_boundary ─────────


class TestCompactBoundary:
    def test_detects_boundary(self):
        boundary = _create_compact_boundary_message("auto", 10000)
        assert is_compact_boundary_message(boundary) is True

    def test_regular_message_not_boundary(self):
        msg = _user("hello")
        assert is_compact_boundary_message(msg) is False

    def test_get_messages_after_boundary(self):
        pre = [_user("old1"), _assistant("old2")]
        boundary = _create_compact_boundary_message("manual", 5000)
        post = [_user("new1"), _assistant("new2")]
        all_msgs = [*pre, boundary, *post]
        result = get_messages_after_compact_boundary(all_msgs)
        assert len(result) == 2
        assert result[0]["content"] == "new1"

    def test_get_messages_no_boundary_returns_all(self):
        msgs = [_user("a"), _assistant("b")]
        result = get_messages_after_compact_boundary(msgs)
        assert len(result) == 2


# ── get_assistant_message_text ────────────────────────────────────────────────


class TestGetAssistantMessageText:
    def test_string_content(self):
        msg = _assistant("hello world")
        assert get_assistant_message_text(msg) == "hello world"

    def test_list_content(self):
        msg = _msg(
            "assistant",
            [
                {"type": "text", "text": "Part 1 "},
                {"type": "text", "text": "Part 2"},
            ],
        )
        assert get_assistant_message_text(msg) == "Part 1 Part 2"

    def test_non_assistant_returns_none(self):
        msg = _user("hello")
        assert get_assistant_message_text(msg) is None

    def test_empty_list_returns_none(self):
        msg = _msg("assistant", [])
        assert get_assistant_message_text(msg) is None


# ── truncate_to_tokens ────────────────────────────────────────────────────────


class TestTruncateToTokens:
    def test_short_content_passthrough(self):
        assert truncate_to_tokens("hello", 1000) == "hello"

    def test_long_content_truncated(self):
        content = "x" * 100_000
        result = truncate_to_tokens(content, 100)
        assert len(result) < len(content)
        assert result.endswith("use Read on the skill path if you need the full text]")


# ── merge_hook_instructions ───────────────────────────────────────────────────


class TestMergeHookInstructions:
    def test_both_present(self):
        result = merge_hook_instructions("user stuff", "hook stuff")
        assert "user stuff" in result
        assert "hook stuff" in result

    def test_only_user(self):
        assert merge_hook_instructions("user only", None) == "user only"

    def test_only_hook(self):
        assert merge_hook_instructions(None, "hook only") == "hook only"

    def test_both_none(self):
        assert merge_hook_instructions(None, None) is None


# ── collect_read_tool_file_paths ──────────────────────────────────────────────


class TestCollectReadToolFilePaths:
    def test_collects_file_paths(self):
        msgs = [
            _msg(
                "assistant",
                [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "Read",
                        "input": {"file_path": "/src/main.py"},
                    },
                ],
            ),
            _msg(
                "user",
                [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "file contents"},
                ],
            ),
        ]
        paths = collect_read_tool_file_paths(msgs)
        assert "/src/main.py" in paths

    def test_excludes_unchanged_stubs(self):
        msgs = [
            _msg(
                "assistant",
                [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "Read",
                        "input": {"file_path": "/src/main.py"},
                    },
                ],
            ),
            _msg(
                "user",
                [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "[File content unchanged"},
                ],
            ),
        ]
        paths = collect_read_tool_file_paths(msgs)
        assert len(paths) == 0

    def test_ignores_non_read_tools(self):
        msgs = [
            _msg(
                "assistant",
                [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "Write",
                        "input": {"file_path": "/src/other.py"},
                    },
                ],
            ),
        ]
        paths = collect_read_tool_file_paths(msgs)
        assert len(paths) == 0


# ── should_exclude_from_restore ───────────────────────────────────────────────


class TestShouldExcludeFromRestore:
    def test_excludes_plan_file(self):
        assert should_exclude_from_restore("/src/plan.md", plan_file_path="/src/plan.md") is True

    def test_excludes_memory_path(self):
        assert should_exclude_from_restore("/memory/state.json", memory_paths={"/memory/state.json"}) is True

    def test_keeps_normal_files(self):
        assert should_exclude_from_restore("/src/main.py") is False


# ── ConversationCompactionResult ──────────────────────────────────────────────


class TestConversationCompactionResult:
    def test_savings_pct(self):
        r = ConversationCompactionResult(
            tokens_before=1000,
            tokens_after=300,
        )
        assert abs(r.savings_pct - 70.0) < 0.01

    def test_savings_pct_zero_before(self):
        r = ConversationCompactionResult(tokens_before=0, tokens_after=0)
        assert r.savings_pct == 0.0


# ── PromptTooLongError ────────────────────────────────────────────────────────


class TestPromptTooLongError:
    def test_basic(self):
        e = PromptTooLongError("test msg")
        assert str(e) == "test msg"
        assert e.response == {}

    def test_with_response(self):
        resp = {"role": "assistant", "content": "error info"}
        e = PromptTooLongError("err", response=resp)
        assert e.response == resp


# ── PTL retry (truncate_head_for_ptl_retry) ───────────────────────────────────


class TestTruncateHeadForPTLRetry:
    def test_drops_groups_by_token_gap(self):
        msgs = _simple_conversation(5)  # 10 messages, 5 groups
        ptl_resp = {
            "role": "assistant",
            "content": "Error: prompt too long by 50 tokens",
        }
        result = truncate_head_for_ptl_retry(msgs, ptl_resp)
        assert result is not None
        assert len(result) < len(msgs)

    def test_fallback_20_percent_drop(self):
        msgs = _simple_conversation(10)
        ptl_resp = {"role": "assistant", "content": "Error: some random error"}
        result = truncate_head_for_ptl_retry(msgs, ptl_resp)
        assert result is not None
        assert len(result) < len(msgs)

    def test_returns_none_for_single_group(self):
        msgs = [_user("only one message")]
        ptl_resp = {"role": "assistant", "content": "too long by 100 tokens"}
        result = truncate_head_for_ptl_retry(msgs, ptl_resp)
        assert result is None

    def test_strips_existing_ptl_marker(self):
        marker_msg = {
            "role": "user",
            "content": PTL_RETRY_MARKER,
            "isMeta": True,
            "uuid": str(uuid.uuid4()),
        }
        msgs = [marker_msg, *_simple_conversation(5)]
        ptl_resp = {"role": "assistant", "content": "too long by 50 tokens"}
        result = truncate_head_for_ptl_retry(msgs, ptl_resp)
        assert result is not None
        # The existing marker should have been stripped before re-grouping
        if result[0].get("isMeta"):
            assert result[0]["content"] == PTL_RETRY_MARKER


# ── compact_conversation ──────────────────────────────────────────────────────


class TestCompactConversation:
    def test_happy_path(self):
        msgs = _simple_conversation(5)
        result = compact_conversation(
            msgs,
            summarize_fn=_mock_summarize("Great summary of 5 rounds."),
        )
        assert isinstance(result, ConversationCompactionResult)
        assert result.summary == "Great summary of 5 rounds."
        assert result.tokens_before > 0
        assert result.tokens_after > 0
        assert result.tokens_after < result.tokens_before
        assert result.is_partial is False
        # Result messages should contain boundary + summary
        assert len(result.messages) == 2
        assert is_compact_boundary_message(result.messages[0])
        assert result.messages[1].get("isCompactSummary") is True

    def test_empty_messages_raises(self):
        with pytest.raises(ValueError, match="Not enough messages"):
            compact_conversation([], summarize_fn=_mock_summarize())

    def test_none_summarize_fn_raises(self):
        with pytest.raises(NotImplementedError):
            compact_conversation(_simple_conversation(3), summarize_fn=None)

    def test_ptl_retry_success(self):
        msgs = _simple_conversation(5)
        result = compact_conversation(
            msgs,
            summarize_fn=_mock_summarize_ptl(fail_n=1, summary="Recovered."),
        )
        assert result.summary == "Recovered."
        assert len(result.messages) == 2

    def test_ptl_retry_exhausted(self):
        msgs = _simple_conversation(5)
        with pytest.raises(ValueError, match="Conversation too long"):
            compact_conversation(
                msgs,
                summarize_fn=_mock_summarize_always_ptl(),
            )

    def test_summarize_fn_generic_error(self):
        """Unexpected errors from summarize_fn become ValueError."""
        msgs = _simple_conversation(3)
        with pytest.raises(ValueError, match="Compaction interrupted"):
            compact_conversation(
                msgs,
                summarize_fn=_mock_summarize_raises(RuntimeError, "network down"),
            )

    def test_auto_compact_trigger(self):
        msgs = _simple_conversation(3)
        result = compact_conversation(
            msgs,
            is_auto_compact=True,
            summarize_fn=_mock_summarize("auto summary"),
        )
        boundary = result.messages[0]
        assert boundary["compactMetadata"]["trigger"] == "auto"

    def test_suppress_follow_up(self):
        msgs = _simple_conversation(3)
        result = compact_conversation(
            msgs,
            suppress_follow_up_questions=True,
            summarize_fn=_mock_summarize("summary"),
        )
        summary_msg = result.messages[1]
        assert "Continue the conversation" in summary_msg["content"]

    def test_custom_instructions_passed(self):
        """Custom instructions are passed through to the compact prompt."""
        captured = {}

        def _fn(messages, prompt):
            captured["prompt"] = prompt
            return "summary"

        compact_conversation(
            _simple_conversation(3),
            custom_instructions="Focus on code changes only.",
            summarize_fn=_fn,
        )
        assert "Focus on code changes only." in captured["prompt"]


# ── partial_compact_conversation ──────────────────────────────────────────────


class TestPartialCompactConversation:
    def test_up_to_direction(self):
        msgs = _simple_conversation(6)  # 12 messages
        result = partial_compact_conversation(
            msgs,
            pivot_index=6,  # Summarize first 6, keep last 6
            direction=CompactDirection.UP_TO,
            summarize_fn=_mock_summarize("First half summary"),
        )
        assert result.is_partial is True
        assert result.summary == "First half summary"
        # Should have boundary + summary + kept messages
        assert len(result.messages) >= 3

    def test_from_direction(self):
        msgs = _simple_conversation(6)
        result = partial_compact_conversation(
            msgs,
            pivot_index=6,
            direction=CompactDirection.FROM,
            summarize_fn=_mock_summarize("Second half summary"),
        )
        assert result.is_partial is True
        assert result.summary == "Second half summary"

    def test_empty_segment_raises(self):
        msgs = _simple_conversation(3)
        with pytest.raises(ValueError, match="Nothing to summarize"):
            partial_compact_conversation(
                msgs,
                pivot_index=0,
                direction=CompactDirection.UP_TO,
                summarize_fn=_mock_summarize(),
            )

    def test_none_summarize_fn_raises(self):
        msgs = _simple_conversation(3)
        with pytest.raises(NotImplementedError):
            partial_compact_conversation(
                msgs,
                pivot_index=2,
                summarize_fn=None,
            )

    def test_user_feedback_in_metadata(self):
        msgs = _simple_conversation(4)
        result = partial_compact_conversation(
            msgs,
            pivot_index=4,
            direction=CompactDirection.UP_TO,
            user_feedback="Summarize the bug-fixing portion.",
            summarize_fn=_mock_summarize("Bug fix summary"),
        )
        boundary = result.messages[0]
        assert boundary["compactMetadata"]["userFeedback"] == "Summarize the bug-fixing portion."

    def test_ptl_retry_in_partial(self):
        msgs = _simple_conversation(5)
        result = partial_compact_conversation(
            msgs,
            pivot_index=4,
            direction=CompactDirection.UP_TO,
            summarize_fn=_mock_summarize_ptl(fail_n=1, summary="Recovered partial."),
        )
        assert result.summary == "Recovered partial."


# ── build_post_compact_messages ───────────────────────────────────────────────


class TestBuildPostCompactMessages:
    def test_builds_list(self):
        r = ConversationCompactionResult(
            messages=[_user("summary"), _assistant("ok")],
        )
        result = build_post_compact_messages(r)
        assert len(result) == 2


# ── Telemetry hooks (logging verification) ────────────────────────────────────


class TestTelemetryHooks:
    def test_compact_logs_token_savings(self, caplog):
        """Verify the compaction pipeline emits token-savings log lines."""
        msgs = _simple_conversation(3)
        with caplog.at_level("INFO", logger="context_compactor.conversation_compact"):
            compact_conversation(
                msgs,
                summarize_fn=_mock_summarize("summary"),
            )
        log_text = caplog.text
        assert "compact:" in log_text
        assert "→" in log_text or "->" in log_text or "tokens" in log_text

    def test_partial_compact_logs_direction(self, caplog):
        msgs = _simple_conversation(4)
        with caplog.at_level("INFO", logger="context_compactor.conversation_compact"):
            partial_compact_conversation(
                msgs,
                pivot_index=4,
                direction=CompactDirection.UP_TO,
                summarize_fn=_mock_summarize("partial"),
            )
        assert "partial_compact:" in caplog.text
        assert "direction=up_to" in caplog.text


# ── Backward compatibility shim ───────────────────────────────────────────────


class TestBackwardCompatibilityShim:
    def test_import_from_agnt_utils_compact(self):
        """The deprecated shim should still export all symbols."""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from packages.agnt_utils.compact import (  # noqa: F401
                compact_conversation as cc,
                CompactDirection as cd,
                ConversationCompactionResult as cr,
                PromptTooLongError as pe,
            )
        assert cc is compact_conversation
        assert cd is CompactDirection
        assert cr is ConversationCompactionResult
        assert pe is PromptTooLongError

    def test_deprecation_warning_emitted(self):
        """Importing from the shim should emit a DeprecationWarning."""
        import importlib
        import warnings
        import sys

        # Force re-import to trigger the warning
        mod_name = "packages.agnt_utils.compact"
        if mod_name in sys.modules:
            del sys.modules[mod_name]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            importlib.import_module(mod_name)

        dep_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
        assert len(dep_warnings) >= 1
        assert "context_compactor" in str(dep_warnings[0].message)
