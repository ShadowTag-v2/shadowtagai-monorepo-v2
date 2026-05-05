# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for agnt_utils batch 2 — 7 new modules ported from Claude Code v2.1.91.

Modules tested:
  - sequential:     async sequential execution wrapper
  - sanitization:   Unicode hidden-character attack mitigation
  - errors:         structured error hierarchy + utilities
  - string_utils:   accumulators, formatting, truncation
  - hash_utils:     djb2 + SHA-256 hashing
  - xml_escape:     XML/HTML entity escaping
  - sleep_utils:    cancellable async sleep + timeout
"""

from __future__ import annotations

import asyncio
import errno
import importlib

import pytest


def _import(path: str):
    return importlib.import_module(path)


# ═══════════════════════════════════════════════════════════════════════════════
#  sequential
# ═══════════════════════════════════════════════════════════════════════════════


class TestSequential:
    """Tests for packages.agnt_utils.sequential."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.sequential")
        self.sequential = mod.sequential

    @pytest.mark.asyncio
    async def test_single_call(self):
        @self.sequential
        async def add(a, b):
            return a + b

        assert await add(1, 2) == 3

    @pytest.mark.asyncio
    async def test_fifo_ordering(self):
        order = []

        @self.sequential
        async def track(label):
            order.append(label)
            await asyncio.sleep(0.01)
            return label

        results = await asyncio.gather(track("a"), track("b"), track("c"))
        assert results == ["a", "b", "c"]
        assert order == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_exception_isolation(self):
        call_count = 0

        @self.sequential
        async def maybe_fail(fail: bool):
            nonlocal call_count
            call_count += 1
            if fail:
                raise ValueError("boom")
            return "ok"

        with pytest.raises(ValueError, match="boom"):
            await maybe_fail(True)

        assert await maybe_fail(False) == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_preserves_return_values(self):
        @self.sequential
        async def double(x):
            await asyncio.sleep(0.005)
            return x * 2

        results = await asyncio.gather(double(1), double(2), double(3))
        assert results == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_pending_count(self):
        @self.sequential
        async def slow():
            await asyncio.sleep(0.05)

        assert slow.pending() == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  sanitization
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitization:
    """Tests for packages.agnt_utils.sanitization."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = _import("packages.agnt_utils.sanitization")
        self.sanitize = mod.partially_sanitize_unicode
        self.recursive = mod.recursively_sanitize_unicode

    def test_clean_text_unchanged(self):
        assert self.sanitize("hello world") == "hello world"

    def test_strips_zero_width_spaces(self):
        assert self.sanitize("he\u200bllo") == "hello"

    def test_strips_directional_overrides(self):
        assert self.sanitize("a\u202ab\u202ec") == "abc"

    def test_strips_bom(self):
        assert self.sanitize("\ufeffhello") == "hello"

    def test_strips_bmp_private_use(self):
        assert self.sanitize("a\ue000b\uf8ffc") == "abc"

    def test_strips_directional_isolates(self):
        assert self.sanitize("x\u2066y\u2069z") == "xyz"

    def test_nfkc_normalization(self):
        # ﬁ (U+FB01) normalizes to "fi" under NFKC
        assert self.sanitize("\ufb01le") == "file"

    def test_preserves_emoji(self):
        assert self.sanitize("hello 🌍") == "hello 🌍"

    def test_preserves_cjk(self):
        assert self.sanitize("日本語テスト") == "日本語テスト"

    def test_recursive_string(self):
        assert self.recursive("he\u200bllo") == "hello"

    def test_recursive_list(self):
        result = self.recursive(["he\u200bllo", "wo\u200brld"])
        assert result == ["hello", "world"]

    def test_recursive_dict(self):
        result = self.recursive({"ke\u200by": "va\u200blue"})
        assert result == {"key": "value"}

    def test_recursive_nested(self):
        data = {"items": [{"name": "te\u200bst"}], "count": 42}
        result = self.recursive(data)
        assert result == {"items": [{"name": "test"}], "count": 42}

    def test_recursive_primitives_unchanged(self):
        assert self.recursive(42) == 42
        assert self.recursive(True) is True
        assert self.recursive(None) is None


# ═══════════════════════════════════════════════════════════════════════════════
#  errors
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrors:
    """Tests for packages.agnt_utils.errors."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _import("packages.agnt_utils.errors")

    def test_agnt_error_base(self):
        e = self.mod.AgntError("test")
        assert str(e) == "test"
        assert isinstance(e, Exception)

    def test_abort_error(self):
        e = self.mod.AbortError("cancelled")
        assert isinstance(e, self.mod.AgntError)

    def test_config_parse_error(self):
        e = self.mod.ConfigParseError("bad json", "/etc/config.json", {"key": "default"})
        assert e.file_path == "/etc/config.json"
        assert e.default_config == {"key": "default"}

    def test_shell_error(self):
        e = self.mod.ShellError("out", "err", 1, interrupted=True)
        assert e.stdout == "out"
        assert e.stderr == "err"
        assert e.return_code == 1
        assert e.interrupted is True

    def test_telemetry_safe_error(self):
        e = self.mod.TelemetrySafeError("full msg", "safe msg")
        assert str(e) == "full msg"
        assert e.telemetry_message == "safe msg"

    def test_telemetry_safe_error_default(self):
        e = self.mod.TelemetrySafeError("same msg")
        assert e.telemetry_message == "same msg"

    def test_to_error_exception(self):
        orig = ValueError("x")
        assert self.mod.to_error(orig) is orig

    def test_to_error_string(self):
        result = self.mod.to_error("oops")
        assert isinstance(result, Exception)
        assert str(result) == "oops"

    def test_error_message(self):
        assert self.mod.error_message(ValueError("x")) == "x"
        assert self.mod.error_message(42) == "42"

    def test_is_abort_error(self):
        assert self.mod.is_abort_error(self.mod.AbortError()) is True
        assert self.mod.is_abort_error(asyncio.CancelledError()) is True
        assert self.mod.is_abort_error(ValueError()) is False

    def test_has_exact_message(self):
        assert self.mod.has_exact_message(ValueError("abc"), "abc") is True
        assert self.mod.has_exact_message(ValueError("abc"), "xyz") is False
        assert self.mod.has_exact_message("not error", "not error") is False

    def test_get_errno_code(self):
        e = OSError(errno.ENOENT, "no such file")
        assert self.mod.get_errno_code(e) == errno.ENOENT
        assert self.mod.get_errno_code(ValueError()) is None

    def test_is_enoent(self):
        assert self.mod.is_enoent(FileNotFoundError(errno.ENOENT, "no such file")) is True
        assert self.mod.is_enoent(PermissionError(errno.EACCES, "denied")) is False

    def test_is_fs_inaccessible(self):
        assert self.mod.is_fs_inaccessible(FileNotFoundError(errno.ENOENT, "no such file")) is True
        assert self.mod.is_fs_inaccessible(PermissionError(errno.EACCES, "denied")) is True
        assert self.mod.is_fs_inaccessible(ValueError()) is False

    def test_short_error_stack_non_exception(self):
        assert self.mod.short_error_stack("oops") == "oops"

    def test_short_error_stack_exception(self):
        try:
            raise ValueError("test error")
        except ValueError as e:
            result = self.mod.short_error_stack(e, max_frames=2)
            assert "ValueError: test error" in result

    def test_classify_http_error_auth(self):
        class FakeResp:
            status_code = 401

        class FakeErr(Exception):
            response = FakeResp()

        result = self.mod.classify_http_error(FakeErr("auth fail"))
        assert result["kind"] == "auth"
        assert result["status"] == 401

    def test_classify_http_error_other(self):
        result = self.mod.classify_http_error(ValueError("nope"))
        assert result["kind"] == "other"


# ═══════════════════════════════════════════════════════════════════════════════
#  string_utils
# ═══════════════════════════════════════════════════════════════════════════════


class TestStringUtils:
    """Tests for packages.agnt_utils.string_utils."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _import("packages.agnt_utils.string_utils")

    def test_capitalize_first(self):
        assert self.mod.capitalize_first("fooBar") == "FooBar"
        assert self.mod.capitalize_first("hello world") == "Hello world"
        assert self.mod.capitalize_first("") == ""

    def test_plural(self):
        assert self.mod.plural(1, "file") == "file"
        assert self.mod.plural(3, "file") == "files"
        assert self.mod.plural(2, "entry", "entries") == "entries"

    def test_first_line_of(self):
        assert self.mod.first_line_of("first\nsecond") == "first"
        assert self.mod.first_line_of("single") == "single"

    def test_count_char(self):
        assert self.mod.count_char("hello", "l") == 2
        assert self.mod.count_char("hello", "z") == 0
        assert self.mod.count_char("aaa", "a", 1) == 2

    def test_normalize_fullwidth_digits(self):
        assert self.mod.normalize_fullwidth_digits("１２３") == "123"
        assert self.mod.normalize_fullwidth_digits("abc") == "abc"

    def test_normalize_fullwidth_space(self):
        assert self.mod.normalize_fullwidth_space("a\u3000b") == "a b"

    def test_safe_join_lines_normal(self):
        assert self.mod.safe_join_lines(["a", "b", "c"]) == "a,b,c"

    def test_safe_join_lines_truncation(self):
        result = self.mod.safe_join_lines(["aaaa", "bbbb", "cccc"], max_size=10)
        assert "truncated" in result

    def test_truncate_to_lines(self):
        text = "line1\nline2\nline3\nline4"
        assert self.mod.truncate_to_lines(text, 2) == "line1\nline2…"
        assert self.mod.truncate_to_lines(text, 10) == text

    # ── EndTruncatingAccumulator ──────────────────────────────────────

    def test_accumulator_basic(self):
        acc = self.mod.EndTruncatingAccumulator(max_size=100)
        acc.append("hello ")
        acc.append("world")
        assert str(acc) == "hello world"
        assert acc.truncated is False

    def test_accumulator_truncation(self):
        acc = self.mod.EndTruncatingAccumulator(max_size=10)
        acc.append("x" * 20)
        assert acc.truncated is True
        assert acc.length == 10
        assert "truncated" in str(acc)

    def test_accumulator_clear(self):
        acc = self.mod.EndTruncatingAccumulator(max_size=100)
        acc.append("data")
        acc.clear()
        assert acc.length == 0
        assert acc.truncated is False
        assert acc.total_bytes == 0

    def test_accumulator_bytes_input(self):
        acc = self.mod.EndTruncatingAccumulator(max_size=100)
        acc.append(b"bytes data")
        assert str(acc) == "bytes data"

    def test_accumulator_total_bytes(self):
        acc = self.mod.EndTruncatingAccumulator(max_size=5)
        acc.append("1234567890")
        assert acc.total_bytes == 10
        assert acc.length == 5


# ═══════════════════════════════════════════════════════════════════════════════
#  hash_utils
# ═══════════════════════════════════════════════════════════════════════════════


class TestHashUtils:
    """Tests for packages.agnt_utils.hash_utils."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _import("packages.agnt_utils.hash_utils")

    def test_djb2_deterministic(self):
        assert self.mod.djb2_hash("hello") == self.mod.djb2_hash("hello")

    def test_djb2_different_strings(self):
        assert self.mod.djb2_hash("foo") != self.mod.djb2_hash("bar")

    def test_djb2_returns_int(self):
        result = self.mod.djb2_hash("test")
        assert isinstance(result, int)

    def test_djb2_empty_string(self):
        assert self.mod.djb2_hash("") == 0

    def test_hash_content_sha256(self):
        result = self.mod.hash_content("hello")
        assert len(result) == 64  # SHA-256 hex
        assert result == self.mod.hash_content("hello")

    def test_hash_content_different(self):
        assert self.mod.hash_content("a") != self.mod.hash_content("b")

    def test_hash_pair_deterministic(self):
        assert self.mod.hash_pair("a", "b") == self.mod.hash_pair("a", "b")

    def test_hash_pair_order_matters(self):
        assert self.mod.hash_pair("a", "b") != self.mod.hash_pair("b", "a")

    def test_hash_pair_distinguishes_boundaries(self):
        # ("ts", "code") vs ("tsc", "ode") must differ
        assert self.mod.hash_pair("ts", "code") != self.mod.hash_pair("tsc", "ode")


# ═══════════════════════════════════════════════════════════════════════════════
#  xml_escape
# ═══════════════════════════════════════════════════════════════════════════════


class TestXmlEscape:
    """Tests for packages.agnt_utils.xml_escape."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _import("packages.agnt_utils.xml_escape")

    def test_escape_xml_ampersand(self):
        assert self.mod.escape_xml("a&b") == "a&amp;b"

    def test_escape_xml_lt_gt(self):
        assert self.mod.escape_xml("<tag>") == "&lt;tag&gt;"

    def test_escape_xml_no_change(self):
        assert self.mod.escape_xml("hello world") == "hello world"

    def test_escape_xml_attr_quotes(self):
        assert self.mod.escape_xml_attr('a"b') == "a&quot;b"
        assert self.mod.escape_xml_attr("a'b") == "a&apos;b"

    def test_escape_xml_attr_full(self):
        result = self.mod.escape_xml_attr('<"test">&')
        assert "&lt;" in result
        assert "&quot;" in result
        assert "&amp;" in result


# ═══════════════════════════════════════════════════════════════════════════════
#  sleep_utils
# ═══════════════════════════════════════════════════════════════════════════════


class TestSleepUtils:
    """Tests for packages.agnt_utils.sleep_utils."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _import("packages.agnt_utils.sleep_utils")

    @pytest.mark.asyncio
    async def test_cancellable_sleep_normal(self):
        await self.mod.cancellable_sleep(0.01)

    @pytest.mark.asyncio
    async def test_cancellable_sleep_pre_aborted(self):
        event = asyncio.Event()
        event.set()
        await self.mod.cancellable_sleep(10, abort_event=event)

    @pytest.mark.asyncio
    async def test_cancellable_sleep_abort_raises(self):
        event = asyncio.Event()
        event.set()
        with pytest.raises(asyncio.CancelledError):
            await self.mod.cancellable_sleep(10, abort_event=event, raise_on_abort=True)

    @pytest.mark.asyncio
    async def test_cancellable_sleep_abort_during(self):
        event = asyncio.Event()

        async def abort_soon():
            await asyncio.sleep(0.01)
            event.set()

        asyncio.ensure_future(abort_soon())
        await self.mod.cancellable_sleep(5, abort_event=event)

    @pytest.mark.asyncio
    async def test_with_timeout_success(self):
        async def fast():
            return 42

        result = await self.mod.with_timeout(fast(), 1.0)
        assert result == 42

    @pytest.mark.asyncio
    async def test_with_timeout_expires(self):
        async def slow():
            await asyncio.sleep(10)

        with pytest.raises(TimeoutError, match="too slow"):
            await self.mod.with_timeout(slow(), 0.01, "too slow")
