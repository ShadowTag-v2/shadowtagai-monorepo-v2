# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for packages/agnt_utils — ported infrastructure utilities.

Coverage:
  - token_budget:      parse_token_budget, find_token_budget_positions, continuation msg
  - circular_buffer:   add, add_all, get_recent, to_list, clear, overflow, edge cases
  - activity_manager:  user/cli activity, dedup, overlapping ops, reset
  - memoize:           TTL (fresh/stale/cold), LRU (basic, custom key, eviction)
"""

from __future__ import annotations

import importlib

import pytest


# ── importlib resolution for hyphenated package dirs ──────────────────────────

def _import(module_path: str):
    return importlib.import_module(module_path)


# ═══════════════════════════════════════════════════════════════════════════════
#  token_budget
# ═══════════════════════════════════════════════════════════════════════════════

class TestTokenBudget:
    """Tests for packages.agnt_utils.token_budget."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.token_budget")
        self.parse = mod.parse_token_budget
        self.find_positions = mod.find_token_budget_positions
        self.continuation_msg = mod.get_budget_continuation_message

    # ── parse_token_budget ────────────────────────────────────────────────

    def test_shorthand_start_k(self):
        assert self.parse("+500k fix everything") == 500_000

    def test_shorthand_start_m(self):
        assert self.parse("+2M refactor") == 2_000_000

    def test_shorthand_start_b(self):
        assert self.parse("+1b go wild") == 1_000_000_000

    def test_shorthand_start_decimal(self):
        assert self.parse("+1.5m fix") == 1_500_000

    def test_shorthand_end(self):
        assert self.parse("fix this thing +500k") == 500_000

    def test_shorthand_end_with_period(self):
        assert self.parse("fix this +2m.") == 2_000_000

    def test_verbose_use(self):
        assert self.parse("use 500k tokens to refactor") == 500_000

    def test_verbose_spend(self):
        assert self.parse("spend 2m tokens") == 2_000_000

    def test_verbose_singular_token(self):
        assert self.parse("use 1m token") == 1_000_000

    def test_no_budget(self):
        assert self.parse("just fix the bug") is None

    def test_empty_string(self):
        assert self.parse("") is None

    def test_case_insensitive(self):
        assert self.parse("+500K fix") == 500_000
        assert self.parse("+2M fix") == 2_000_000

    # ── find_token_budget_positions ───────────────────────────────────────

    def test_positions_start(self):
        positions = self.find_positions("+500k fix")
        assert len(positions) >= 1
        assert positions[0].start >= 0

    def test_positions_verbose(self):
        positions = self.find_positions("use 2m tokens to fix")
        assert len(positions) >= 1

    def test_positions_none(self):
        positions = self.find_positions("no budget here")
        assert len(positions) == 0

    # ── get_budget_continuation_message ───────────────────────────────────

    def test_continuation_message_format(self):
        msg = self.continuation_msg(50, 250_000, 500_000)
        assert "50%" in msg
        assert "250,000" in msg
        assert "500,000" in msg
        assert "Keep working" in msg


# ═══════════════════════════════════════════════════════════════════════════════
#  circular_buffer
# ═══════════════════════════════════════════════════════════════════════════════

class TestCircularBuffer:
    """Tests for packages.agnt_utils.circular_buffer."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.circular_buffer")
        self.CircularBuffer = mod.CircularBuffer

    def test_add_under_capacity(self):
        buf = self.CircularBuffer(5)
        buf.add(1)
        buf.add(2)
        assert buf.to_list() == [1, 2]
        assert len(buf) == 2

    def test_add_at_capacity(self):
        buf = self.CircularBuffer(3)
        buf.add(1)
        buf.add(2)
        buf.add(3)
        assert buf.to_list() == [1, 2, 3]

    def test_add_overflow_evicts_oldest(self):
        buf = self.CircularBuffer(3)
        for i in range(5):
            buf.add(i)
        assert buf.to_list() == [2, 3, 4]

    def test_get_recent(self):
        buf = self.CircularBuffer(5)
        for i in range(5):
            buf.add(i)
        assert buf.get_recent(2) == [3, 4]
        assert buf.get_recent(5) == [0, 1, 2, 3, 4]
        assert buf.get_recent(10) == [0, 1, 2, 3, 4]

    def test_get_recent_after_overflow(self):
        buf = self.CircularBuffer(3)
        for i in range(10):
            buf.add(i)
        assert buf.get_recent(2) == [8, 9]
        assert buf.get_recent(3) == [7, 8, 9]

    def test_add_all(self):
        buf = self.CircularBuffer(3)
        buf.add_all([1, 2, 3, 4, 5])
        assert buf.to_list() == [3, 4, 5]

    def test_clear(self):
        buf = self.CircularBuffer(3)
        buf.add_all([1, 2, 3])
        buf.clear()
        assert len(buf) == 0
        assert buf.to_list() == []

    def test_bool_empty(self):
        buf = self.CircularBuffer(3)
        assert not buf

    def test_bool_nonempty(self):
        buf = self.CircularBuffer(3)
        buf.add(1)
        assert buf

    def test_repr(self):
        buf = self.CircularBuffer(5)
        buf.add(1)
        assert "capacity=5" in repr(buf)
        assert "size=1" in repr(buf)

    def test_capacity_must_be_positive(self):
        with pytest.raises(ValueError, match="capacity must be >= 1"):
            self.CircularBuffer(0)


# ═══════════════════════════════════════════════════════════════════════════════
#  activity_manager
# ═══════════════════════════════════════════════════════════════════════════════

class TestActivityManager:
    """Tests for packages.agnt_utils.activity_manager."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.activity_manager")
        self.ActivityManager = mod.ActivityManager

    def test_initial_state(self):
        t = 100.0
        am = self.ActivityManager(get_now=lambda: t)
        states = am.get_activity_states()
        assert not states.is_user_active
        assert not states.is_cli_active
        assert states.active_operation_count == 0

    def test_user_activity_within_timeout(self):
        t = [100.0]
        am = self.ActivityManager(get_now=lambda: t[0])
        am.record_user_activity()
        t[0] = 102.0  # within 5s timeout
        states = am.get_activity_states()
        assert states.is_user_active

    def test_user_activity_expired(self):
        t = [100.0]
        am = self.ActivityManager(get_now=lambda: t[0])
        am.record_user_activity()
        t[0] = 106.0  # past 5s timeout
        states = am.get_activity_states()
        assert not states.is_user_active

    def test_user_activity_delta_recorded(self):
        deltas = []
        t = [100.0]
        am = self.ActivityManager(
            get_now=lambda: t[0],
            record_callback=lambda dt, kind: deltas.append((dt, kind)),
        )
        am.record_user_activity()  # first event — no delta
        t[0] = 103.0
        am.record_user_activity()  # second event — records delta
        assert len(deltas) == 1
        assert deltas[0][1] == "user"
        assert abs(deltas[0][0] - 3.0) < 0.01

    def test_user_activity_not_recorded_during_cli(self):
        deltas = []
        t = [100.0]
        am = self.ActivityManager(
            get_now=lambda: t[0],
            record_callback=lambda dt, kind: deltas.append((dt, kind)),
        )
        am.record_user_activity()
        am.start_cli_activity("op1")
        t[0] = 102.0
        am.record_user_activity()  # cli is active — should NOT record user delta
        user_deltas = [d for d in deltas if d[1] == "user"]
        assert len(user_deltas) == 0

    def test_cli_activity_tracking(self):
        deltas = []
        t = [100.0]
        am = self.ActivityManager(
            get_now=lambda: t[0],
            record_callback=lambda dt, kind: deltas.append((dt, kind)),
        )
        am.start_cli_activity("op1")
        t[0] = 105.0
        am.end_cli_activity("op1")
        cli_deltas = [d for d in deltas if d[1] == "cli"]
        assert len(cli_deltas) == 1
        assert abs(cli_deltas[0][0] - 5.0) < 0.01

    def test_overlapping_cli_operations(self):
        deltas = []
        t = [100.0]
        am = self.ActivityManager(
            get_now=lambda: t[0],
            record_callback=lambda dt, kind: deltas.append((dt, kind)),
        )
        am.start_cli_activity("op1")
        t[0] = 102.0
        am.start_cli_activity("op2")
        t[0] = 107.0
        am.end_cli_activity("op1")  # op2 still active — no delta yet
        cli_deltas = [d for d in deltas if d[1] == "cli"]
        assert len(cli_deltas) == 0

        am.end_cli_activity("op2")  # now all done — records total
        cli_deltas = [d for d in deltas if d[1] == "cli"]
        assert len(cli_deltas) == 1
        assert abs(cli_deltas[0][0] - 7.0) < 0.01

    def test_reset(self):
        t = [100.0]
        am = self.ActivityManager(get_now=lambda: t[0])
        am.start_cli_activity("op1")
        am.record_user_activity()
        am.reset()
        states = am.get_activity_states()
        assert not states.is_cli_active
        assert states.active_operation_count == 0
        assert am.total_user_seconds == 0.0
        assert am.total_cli_seconds == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  memoize
# ═══════════════════════════════════════════════════════════════════════════════

class TestMemoize:
    """Tests for packages.agnt_utils.memoize."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.memoize")
        self.memoize_with_ttl = mod.memoize_with_ttl
        self.memoize_with_lru = mod.memoize_with_lru

    # ── TTL ────────────────────────────────────────────────────────────────

    def test_ttl_caches_result(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        cached = self.memoize_with_ttl(fn, cache_lifetime_s=10.0)
        assert cached(5) == 10
        assert cached(5) == 10
        assert call_count == 1

    def test_ttl_different_args(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        cached = self.memoize_with_ttl(fn, cache_lifetime_s=10.0)
        assert cached(5) == 10
        assert cached(6) == 12
        assert call_count == 2

    def test_ttl_cache_clear(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        cached = self.memoize_with_ttl(fn, cache_lifetime_s=10.0)
        cached(1)
        cached.cache_clear()
        cached(1)
        assert call_count == 2

    # ── LRU ────────────────────────────────────────────────────────────────

    def test_lru_caches_result(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        cached = self.memoize_with_lru(fn, maxsize=10)
        assert cached(5) == 10
        assert cached(5) == 10
        assert call_count == 1

    def test_lru_eviction(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        cached = self.memoize_with_lru(fn, maxsize=2)
        cached(1)
        cached(2)
        cached(3)  # evicts 1
        cached(1)  # cache miss — recomputes
        assert call_count == 4

    def test_lru_custom_key(self):
        call_count = 0

        def fn(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        cached = self.memoize_with_lru(
            fn, maxsize=10, cache_key=lambda x, y: f"{x}:{y}"
        )
        assert cached(1, 2) == 3
        assert cached(1, 2) == 3
        assert call_count == 1

    def test_lru_custom_key_cache_clear(self):
        call_count = 0

        def fn(x):
            nonlocal call_count
            call_count += 1
            return x

        cached = self.memoize_with_lru(
            fn, maxsize=10, cache_key=lambda x: str(x)
        )
        cached(1)
        cached.cache_clear()
        cached(1)
        assert call_count == 2

    def test_lru_custom_key_cache_info(self):
        def fn(x):
            return x

        cached = self.memoize_with_lru(
            fn, maxsize=5, cache_key=lambda x: str(x)
        )
        cached(1)
        cached(2)
        info = cached.cache_info()
        assert info["size"] == 2
        assert info["maxsize"] == 5


# ═══════════════════════════════════════════════════════════════════════════════
#  token_estimate
# ═══════════════════════════════════════════════════════════════════════════════

class TestTokenEstimate:
    """Tests for packages.agnt_utils.token_estimate."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.token_estimate")
        self.rough = mod.rough_token_estimate
        self.bpt_for_file = mod.bytes_per_token_for_file_type
        self.rough_file = mod.rough_token_estimate_for_file_type
        self.rough_block = mod.rough_token_estimate_for_block
        self.rough_content = mod.rough_token_estimate_for_content
        self.rough_message = mod.rough_token_estimate_for_message
        self.rough_messages = mod.rough_token_estimate_for_messages
        self.from_usage = mod.get_token_count_from_usage
        self.with_estimation = mod.token_count_with_estimation
        self.IMAGE_MAX = mod.IMAGE_MAX_TOKEN_SIZE

    # ── rough_token_estimate ──────────────────────────────────────────────

    def test_rough_empty(self):
        assert self.rough("") == 0

    def test_rough_default_ratio(self):
        # 100 chars / 4 = 25
        assert self.rough("a" * 100) == 25

    def test_rough_custom_ratio(self):
        # 100 chars / 2 = 50
        assert self.rough("a" * 100, bytes_per_token=2) == 50

    def test_rough_rounding(self):
        # 5 chars / 4 = 1.25 → rounds to 1
        assert self.rough("hello") == 1
        # 7 chars / 4 = 1.75 → rounds to 2
        assert self.rough("goodbye") == 2

    # ── file-type-aware ───────────────────────────────────────────────────

    def test_bpt_json(self):
        assert self.bpt_for_file("json") == 2
        assert self.bpt_for_file("jsonl") == 2
        assert self.bpt_for_file("jsonc") == 2
        assert self.bpt_for_file("JSON") == 2

    def test_bpt_non_json(self):
        assert self.bpt_for_file("py") == 4
        assert self.bpt_for_file("ts") == 4
        assert self.bpt_for_file("md") == 4

    def test_rough_file_json(self):
        content = '{"key": "value"}'
        assert self.rough_file(content, "json") == self.rough(content, 2)

    def test_rough_file_prose(self):
        content = "The quick brown fox jumps over the lazy dog."
        assert self.rough_file(content, "md") == self.rough(content, 4)

    # ── block-level ───────────────────────────────────────────────────────

    def test_block_string(self):
        assert self.rough_block("hello world") == self.rough("hello world")

    def test_block_text_type(self):
        block = {"type": "text", "text": "hello world"}
        assert self.rough_block(block) == self.rough("hello world")

    def test_block_image(self):
        block = {"type": "image", "source": {"data": "base64..."}}
        assert self.rough_block(block) == self.IMAGE_MAX

    def test_block_document(self):
        block = {"type": "document", "source": {"data": "base64..."}}
        assert self.rough_block(block) == self.IMAGE_MAX

    def test_block_tool_use(self):
        block = {"type": "tool_use", "name": "read_file", "input": {"path": "/foo"}}
        expected = self.rough("read_file" + '{"path": "/foo"}')
        assert self.rough_block(block) == expected

    def test_block_tool_result_none(self):
        block = {"type": "tool_result", "content": None}
        assert self.rough_block(block) == 0

    def test_block_tool_result_string(self):
        block = {"type": "tool_result", "content": "result text"}
        assert self.rough_block(block) == self.rough("result text")

    def test_block_thinking(self):
        block = {"type": "thinking", "thinking": "I need to consider..."}
        assert self.rough_block(block) == self.rough("I need to consider...")

    def test_block_redacted_thinking(self):
        block = {"type": "redacted_thinking", "data": "ABC123"}
        assert self.rough_block(block) == self.rough("ABC123")

    def test_block_unknown_type(self):
        block = {"type": "custom_block", "data": "stuff"}
        import json
        assert self.rough_block(block) == self.rough(json.dumps(block))

    # ── content-level ─────────────────────────────────────────────────────

    def test_content_none(self):
        assert self.rough_content(None) == 0

    def test_content_string(self):
        assert self.rough_content("hello") == self.rough("hello")

    def test_content_list(self):
        blocks = [
            {"type": "text", "text": "hello"},
            {"type": "text", "text": "world"},
        ]
        expected = self.rough("hello") + self.rough("world")
        assert self.rough_content(blocks) == expected

    # ── message-level ─────────────────────────────────────────────────────

    def test_message_assistant(self):
        msg = {"type": "assistant", "message": {"content": "Hello!"}}
        assert self.rough_message(msg) == self.rough("Hello!")

    def test_message_user(self):
        msg = {"type": "user", "message": {"content": "How are you?"}}
        assert self.rough_message(msg) == self.rough("How are you?")

    def test_message_attachment_with_text(self):
        msg = {"type": "attachment", "attachment": {"text": "file contents"}}
        assert self.rough_message(msg) == self.rough("file contents")

    def test_message_attachment_no_text(self):
        msg = {"type": "attachment", "attachment": {"binary": True}}
        assert self.rough_message(msg) == 0

    def test_message_unknown_type(self):
        msg = {"type": "system", "data": "foo"}
        assert self.rough_message(msg) == 0

    # ── messages aggregate ────────────────────────────────────────────────

    def test_messages_aggregate(self):
        messages = [
            {"type": "user", "message": {"content": "Hello"}},
            {"type": "assistant", "message": {"content": "Hi there!"}},
        ]
        expected = self.rough("Hello") + self.rough("Hi there!")
        assert self.rough_messages(messages) == expected

    def test_messages_empty(self):
        assert self.rough_messages([]) == 0

    # ── usage-based counting ──────────────────────────────────────────────

    def test_usage_basic(self):
        usage = {"input_tokens": 100, "output_tokens": 50}
        assert self.from_usage(usage) == 150

    def test_usage_with_cache(self):
        usage = {
            "input_tokens": 100,
            "cache_creation_input_tokens": 200,
            "cache_read_input_tokens": 50,
            "output_tokens": 75,
        }
        assert self.from_usage(usage) == 425

    def test_usage_missing_fields(self):
        assert self.from_usage({}) == 0

    # ── token_count_with_estimation (walk-back) ───────────────────────────

    def test_with_estimation_uses_last_usage(self):
        messages = [
            {"type": "user", "message": {"content": "q1"}},
            {"type": "assistant", "message": {
                "content": "a1",
                "usage": {"input_tokens": 1000, "output_tokens": 200},
            }},
            {"type": "user", "message": {"content": "q2"}},
        ]
        base = 1000 + 200
        remaining_estimate = self.rough("q2")
        assert self.with_estimation(messages) == base + remaining_estimate

    def test_with_estimation_no_usage_falls_back(self):
        messages = [
            {"type": "user", "message": {"content": "Hello"}},
            {"type": "assistant", "message": {"content": "Hi"}},
        ]
        expected = self.rough("Hello") + self.rough("Hi")
        assert self.with_estimation(messages) == expected

    def test_with_estimation_empty(self):
        assert self.with_estimation([]) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  truncate
# ═══════════════════════════════════════════════════════════════════════════════

class TestTruncate:
    """Tests for packages.agnt_utils.truncate."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.truncate")
        self.string_width = mod.string_width
        self.truncate_to_width = mod.truncate_to_width
        self.truncate_start_to_width = mod.truncate_start_to_width
        self.truncate_to_width_no_ellipsis = mod.truncate_to_width_no_ellipsis
        self.truncate_path_middle = mod.truncate_path_middle
        self.truncate = mod.truncate
        self.wrap_text = mod.wrap_text

    # ── string_width ──────────────────────────────────────────────────────

    def test_width_ascii(self):
        assert self.string_width("hello") == 5

    def test_width_empty(self):
        assert self.string_width("") == 0

    def test_width_cjk(self):
        # CJK characters are width 2
        assert self.string_width("漢字") == 4

    def test_width_mixed(self):
        # "A漢" → 1 + 2 = 3
        assert self.string_width("A漢") == 3

    def test_width_ansi_stripped(self):
        assert self.string_width("\x1b[31mred\x1b[0m") == 3

    # ── truncate_to_width ─────────────────────────────────────────────────

    def test_truncate_no_op(self):
        assert self.truncate_to_width("hello", 10) == "hello"

    def test_truncate_exact_fit(self):
        assert self.truncate_to_width("hello", 5) == "hello"

    def test_truncate_adds_ellipsis(self):
        result = self.truncate_to_width("hello world", 6)
        assert result.endswith("…")
        assert self.string_width(result) <= 6

    def test_truncate_max_width_1(self):
        assert self.truncate_to_width("hello", 1) == "…"

    # ── truncate_start_to_width ───────────────────────────────────────────

    def test_truncate_start_no_op(self):
        assert self.truncate_start_to_width("hello", 10) == "hello"

    def test_truncate_start_keeps_tail(self):
        result = self.truncate_start_to_width("hello world", 6)
        assert result.startswith("…")
        assert result.endswith("world")

    def test_truncate_start_max_1(self):
        assert self.truncate_start_to_width("hello", 1) == "…"

    # ── truncate_to_width_no_ellipsis ─────────────────────────────────────

    def test_no_ellipsis_no_op(self):
        assert self.truncate_to_width_no_ellipsis("hello", 10) == "hello"

    def test_no_ellipsis_truncates(self):
        result = self.truncate_to_width_no_ellipsis("hello world", 5)
        assert result == "hello"
        assert "…" not in result

    def test_no_ellipsis_zero_width(self):
        assert self.truncate_to_width_no_ellipsis("hello", 0) == ""

    # ── truncate_path_middle ──────────────────────────────────────────────

    def test_path_no_truncation(self):
        path = "src/main.py"
        assert self.truncate_path_middle(path, 50) == path

    def test_path_middle_truncation(self):
        path = "src/components/deeply/nested/folder/MyComponent.tsx"
        result = self.truncate_path_middle(path, 30)
        assert "…" in result
        assert result.endswith("/MyComponent.tsx")
        assert self.string_width(result) <= 30

    def test_path_very_short_max(self):
        result = self.truncate_path_middle("src/main.py", 3)
        assert self.string_width(result) <= 3

    def test_path_zero_max(self):
        assert self.truncate_path_middle("src/main.py", 0) == "…"

    def test_path_no_slashes(self):
        result = self.truncate_path_middle("verylongfilename.tsx", 10)
        assert self.string_width(result) <= 10

    # ── truncate (general) ────────────────────────────────────────────────

    def test_general_no_truncation(self):
        assert self.truncate("hello", 10) == "hello"

    def test_general_truncates(self):
        result = self.truncate("hello world", 6)
        assert result.endswith("…")

    def test_single_line_truncates_at_newline(self):
        result = self.truncate("hello\nworld", 50, single_line=True)
        assert result == "hello…"
        assert "\n" not in result

    def test_single_line_no_newline(self):
        result = self.truncate("hello", 50, single_line=True)
        assert result == "hello"

    def test_single_line_with_width_limit(self):
        result = self.truncate("hello world\nsecond line", 6, single_line=True)
        assert self.string_width(result) <= 6

    # ── wrap_text ─────────────────────────────────────────────────────────

    def test_wrap_basic(self):
        lines = self.wrap_text("abcdefghij", 5)
        assert lines == ["abcde", "fghij"]

    def test_wrap_short_text(self):
        lines = self.wrap_text("abc", 10)
        assert lines == ["abc"]

    def test_wrap_empty(self):
        lines = self.wrap_text("", 10)
        assert lines == []

    def test_wrap_cjk(self):
        # Each CJK char is width 2; 3 chars = width 6, wrap at 4
        lines = self.wrap_text("漢字漢", 4)
        assert len(lines) == 2
        assert lines[0] == "漢字"
        assert lines[1] == "漢"
