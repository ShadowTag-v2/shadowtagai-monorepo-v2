# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for agnt_utils Batch 3 modules.

Tests: json_utils, set_ops, signal, diff_utils, treeify,
       combined_abort, generators, format_utils, array_utils
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time

import pytest
from datetime import UTC


# ═══════════════════════════════════════════════════════════════════════
# json_utils
# ═══════════════════════════════════════════════════════════════════════
class TestJsonUtils:
    """Tests for packages.agnt_utils.json_utils."""

    def test_safe_parse_json_valid(self):
        from packages.agnt_utils.json_utils import safe_parse_json

        assert safe_parse_json('{"a": 1}') == {"a": 1}

    def test_safe_parse_json_null(self):
        from packages.agnt_utils.json_utils import safe_parse_json

        assert safe_parse_json(None) is None
        assert safe_parse_json("") is None

    def test_safe_parse_json_invalid(self):
        from packages.agnt_utils.json_utils import safe_parse_json

        assert safe_parse_json("{bad json}") is None

    def test_safe_parse_json_bom(self):
        from packages.agnt_utils.json_utils import safe_parse_json

        assert safe_parse_json('\ufeff{"x": 42}') == {"x": 42}

    def test_safe_parse_json_cache_boundary(self):
        from packages.agnt_utils.json_utils import clear_parse_cache, safe_parse_json

        clear_parse_cache()
        small = '{"s": 1}'
        assert safe_parse_json(small) == {"s": 1}
        # Same input should hit cache
        assert safe_parse_json(small) == {"s": 1}
        # Large input should bypass cache
        big = json.dumps({"k": "x" * 10000})
        assert safe_parse_json(big)["k"] == "x" * 10000

    def test_safe_parse_json_null_literal(self):
        from packages.agnt_utils.json_utils import safe_parse_json

        assert safe_parse_json("null") is None

    def test_safe_parse_jsonc(self):
        from packages.agnt_utils.json_utils import safe_parse_jsonc

        jsonc = '{"a": 1} // comment'
        assert safe_parse_jsonc(jsonc) == {"a": 1}

    def test_safe_parse_jsonc_block_comment(self):
        from packages.agnt_utils.json_utils import safe_parse_jsonc

        jsonc = '{"a": /* inline */ 1}'
        assert safe_parse_jsonc(jsonc) == {"a": 1}

    def test_safe_parse_jsonc_none(self):
        from packages.agnt_utils.json_utils import safe_parse_jsonc

        assert safe_parse_jsonc(None) is None

    def test_parse_jsonl(self):
        from packages.agnt_utils.json_utils import parse_jsonl

        data = '{"a":1}\n{"b":2}\n'
        result = parse_jsonl(data)
        assert result == [{"a": 1}, {"b": 2}]

    def test_parse_jsonl_skips_malformed(self):
        from packages.agnt_utils.json_utils import parse_jsonl

        data = '{"a":1}\nnot json\n{"b":2}\n'
        result = parse_jsonl(data)
        assert result == [{"a": 1}, {"b": 2}]

    def test_parse_jsonl_bytes(self):
        from packages.agnt_utils.json_utils import parse_jsonl

        data = b'{"x":1}\n{"y":2}\n'
        result = parse_jsonl(data)
        assert result == [{"x": 1}, {"y": 2}]

    def test_parse_jsonl_bom_bytes(self):
        from packages.agnt_utils.json_utils import parse_jsonl

        data = b'\xef\xbb\xbf{"x":1}\n'
        result = parse_jsonl(data)
        assert result == [{"x": 1}]

    def test_read_jsonl_file(self):
        from packages.agnt_utils.json_utils import read_jsonl_file

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"a":1}\n{"b":2}\n')
            f.flush()
            path = f.name
        try:
            result = read_jsonl_file(path)
            assert result == [{"a": 1}, {"b": 2}]
        finally:
            os.unlink(path)

    def test_strip_bom(self):
        from packages.agnt_utils.json_utils import strip_bom

        assert strip_bom("\ufeffhello") == "hello"
        assert strip_bom("hello") == "hello"

    def test_add_item_to_jsonc_array_empty(self):
        from packages.agnt_utils.json_utils import add_item_to_jsonc_array

        result = add_item_to_jsonc_array("", "new_item")
        assert json.loads(result) == ["new_item"]

    def test_add_item_to_jsonc_array_existing(self):
        from packages.agnt_utils.json_utils import add_item_to_jsonc_array

        result = add_item_to_jsonc_array("[1, 2]", 3)
        assert json.loads(result) == [1, 2, 3]


# ═══════════════════════════════════════════════════════════════════════
# set_ops
# ═══════════════════════════════════════════════════════════════════════
class TestSetOps:
    """Tests for packages.agnt_utils.set_ops."""

    def test_difference(self):
        from packages.agnt_utils.set_ops import difference

        assert difference({1, 2, 3}, {2, 3, 4}) == {1}

    def test_difference_empty(self):
        from packages.agnt_utils.set_ops import difference

        assert difference(set(), {1, 2}) == set()
        assert difference({1, 2}, set()) == {1, 2}

    def test_intersects_true(self):
        from packages.agnt_utils.set_ops import intersects

        assert intersects({1, 2}, {2, 3}) is True

    def test_intersects_false(self):
        from packages.agnt_utils.set_ops import intersects

        assert intersects({1, 2}, {3, 4}) is False

    def test_intersects_empty(self):
        from packages.agnt_utils.set_ops import intersects

        assert intersects(set(), {1}) is False
        assert intersects({1}, set()) is False

    def test_every(self):
        from packages.agnt_utils.set_ops import every

        assert every({1, 2}, {1, 2, 3}) is True
        assert every({1, 4}, {1, 2, 3}) is False

    def test_union(self):
        from packages.agnt_utils.set_ops import union

        assert union({1, 2}, {3, 4}) == {1, 2, 3, 4}

    def test_intersection(self):
        from packages.agnt_utils.set_ops import intersection

        assert intersection({1, 2, 3}, {2, 3, 4}) == {2, 3}

    def test_symmetric_difference(self):
        from packages.agnt_utils.set_ops import symmetric_difference

        assert symmetric_difference({1, 2, 3}, {2, 3, 4}) == {1, 4}

    def test_unique(self):
        from packages.agnt_utils.set_ops import unique

        assert unique([3, 1, 2, 1, 3]) == [3, 1, 2]


# ═══════════════════════════════════════════════════════════════════════
# signal
# ═══════════════════════════════════════════════════════════════════════
class TestSignal:
    """Tests for packages.agnt_utils.signal."""

    def test_create_signal(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        assert sig.listener_count == 0

    def test_subscribe_and_emit(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        results = []
        sig.subscribe(lambda: results.append("fired"))
        sig.emit()
        assert results == ["fired"]

    def test_emit_with_args(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        results = []
        sig.subscribe(lambda x, y: results.append((x, y)))
        sig.emit(1, 2)
        assert results == [(1, 2)]

    def test_unsubscribe(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        results = []
        unsub = sig.subscribe(lambda: results.append("x"))
        sig.emit()
        unsub()
        sig.emit()
        assert results == ["x"]

    def test_clear(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        sig.subscribe(lambda: None)
        sig.subscribe(lambda: None)
        assert sig.listener_count == 2
        sig.clear()
        assert sig.listener_count == 0

    def test_multiple_listeners(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        results = []
        sig.subscribe(lambda: results.append("a"))
        sig.subscribe(lambda: results.append("b"))
        sig.emit()
        assert set(results) == {"a", "b"}

    def test_repr(self):
        from packages.agnt_utils.signal import create_signal

        sig = create_signal()
        assert "Signal(listeners=0)" in repr(sig)


# ═══════════════════════════════════════════════════════════════════════
# diff_utils
# ═══════════════════════════════════════════════════════════════════════
class TestDiffUtils:
    """Tests for packages.agnt_utils.diff_utils."""

    def test_get_patch_from_contents(self):
        from packages.agnt_utils.diff_utils import get_patch_from_contents

        hunks = get_patch_from_contents("line1\nline2\n", "line1\nline3\n")
        assert len(hunks) > 0

    def test_get_patch_identical(self):
        from packages.agnt_utils.diff_utils import get_patch_from_contents

        hunks = get_patch_from_contents("same\n", "same\n")
        assert hunks == []

    def test_count_lines_changed(self):
        from packages.agnt_utils.diff_utils import (
            count_lines_changed,
            get_patch_from_contents,
        )

        hunks = get_patch_from_contents("a\nb\n", "a\nc\nd\n")
        changed = count_lines_changed(hunks)
        assert changed.additions > 0

    def test_count_lines_changed_new_file(self):
        from packages.agnt_utils.diff_utils import count_lines_changed

        changed = count_lines_changed([], "line1\nline2\nline3\n")
        assert changed.additions == 3
        assert changed.removals == 0

    def test_adjust_hunk_line_numbers(self):
        from packages.agnt_utils.diff_utils import Hunk, adjust_hunk_line_numbers

        hunks = [Hunk(old_start=1, old_length=3, new_start=1, new_length=4)]
        shifted = adjust_hunk_line_numbers(hunks, 10)
        assert shifted[0].old_start == 11
        assert shifted[0].new_start == 11

    def test_adjust_hunk_zero_offset(self):
        from packages.agnt_utils.diff_utils import Hunk, adjust_hunk_line_numbers

        hunks = [Hunk(old_start=5, old_length=1, new_start=5, new_length=1)]
        assert adjust_hunk_line_numbers(hunks, 0) is hunks

    def test_apply_edits(self):
        from packages.agnt_utils.diff_utils import apply_edits

        result = apply_edits(
            "hello world",
            [
                {"old_string": "hello", "new_string": "hi"},
            ],
        )
        assert result == "hi world"

    def test_apply_edits_replace_all(self):
        from packages.agnt_utils.diff_utils import apply_edits

        result = apply_edits(
            "aaa bbb aaa",
            [
                {"old_string": "aaa", "new_string": "xxx", "replace_all": True},
            ],
        )
        assert result == "xxx bbb xxx"

    def test_get_unified_diff(self):
        from packages.agnt_utils.diff_utils import get_unified_diff

        diff = get_unified_diff("a\nb\n", "a\nc\n")
        assert "-b" in diff
        assert "+c" in diff

    def test_escape_ampersand_in_diff(self):
        from packages.agnt_utils.diff_utils import get_patch_from_contents

        hunks = get_patch_from_contents("a & b\n", "a & c\n")
        # Ampersand should be preserved in the output lines
        for h in hunks:
            for line in h.lines:
                assert "AMPERSAND_TOKEN" not in line


# ═══════════════════════════════════════════════════════════════════════
# treeify
# ═══════════════════════════════════════════════════════════════════════
class TestTreeify:
    """Tests for packages.agnt_utils.treeify."""

    def test_empty(self):
        from packages.agnt_utils.treeify import treeify

        assert treeify({}) == "(empty)"

    def test_simple_tree(self):
        from packages.agnt_utils.treeify import treeify

        result = treeify({"a": "1", "b": "2"})
        assert "a" in result
        assert "b" in result

    def test_nested_tree(self):
        from packages.agnt_utils.treeify import treeify

        result = treeify({"root": {"child1": "v1", "child2": "v2"}})
        assert "root" in result
        assert "child1" in result

    def test_circular_reference(self):
        from packages.agnt_utils.treeify import treeify

        obj: dict = {"a": {}}
        obj["a"]["self"] = obj["a"]  # type: ignore[index]
        result = treeify(obj)
        assert "[Circular]" in result

    def test_show_values_false(self):
        from packages.agnt_utils.treeify import treeify

        result = treeify({"key": "val"}, show_values=False)
        assert "key" in result

    def test_array_handling(self):
        from packages.agnt_utils.treeify import treeify

        result = treeify({"items": [1, 2, 3]})
        assert "Array(3)" in result

    def test_tree_characters(self):
        from packages.agnt_utils.treeify import treeify

        result = treeify({"a": "1", "b": "2"})
        assert "├" in result or "└" in result

    def test_max_depth(self):
        from packages.agnt_utils.treeify import treeify

        deep = {"l1": {"l2": {"l3": {"l4": "v"}}}}
        result = treeify(deep, max_depth=2)
        assert "[max depth exceeded]" in result


# ═══════════════════════════════════════════════════════════════════════
# combined_abort
# ═══════════════════════════════════════════════════════════════════════
class TestCombinedAbort:
    """Tests for packages.agnt_utils.combined_abort."""

    def test_create_not_cancelled(self):
        from packages.agnt_utils.combined_abort import create_combined_abort

        ca = create_combined_abort()
        assert not ca.is_cancelled
        ca.cleanup()

    def test_already_set_event(self):
        from packages.agnt_utils.combined_abort import create_combined_abort

        ev = threading.Event()
        ev.set()
        ca = create_combined_abort(ev)
        assert ca.is_cancelled
        ca.cleanup()

    def test_timeout(self):
        from packages.agnt_utils.combined_abort import create_combined_abort

        ca = create_combined_abort(timeout_seconds=0.1)
        assert not ca.is_cancelled
        time.sleep(0.2)
        assert ca.is_cancelled
        ca.cleanup()

    def test_cleanup_clears_timer(self):
        from packages.agnt_utils.combined_abort import create_combined_abort

        ca = create_combined_abort(timeout_seconds=10.0)
        ca.cleanup()
        time.sleep(0.05)
        assert not ca.is_cancelled

    def test_event_triggers_combined(self):
        from packages.agnt_utils.combined_abort import create_combined_abort

        ev = threading.Event()
        ca = create_combined_abort(ev)
        assert not ca.is_cancelled
        ev.set()
        ca.wait(timeout=0.3)
        assert ca.is_cancelled
        ca.cleanup()


# ═══════════════════════════════════════════════════════════════════════
# generators
# ═══════════════════════════════════════════════════════════════════════
class TestGenerators:
    """Tests for packages.agnt_utils.generators."""

    @pytest.mark.asyncio
    async def test_last(self):
        from packages.agnt_utils.generators import from_array, last

        gen = from_array([1, 2, 3])
        result = await last(gen)
        assert result == 3

    @pytest.mark.asyncio
    async def test_last_empty(self):
        from packages.agnt_utils.generators import from_array, last

        gen = from_array([])
        with pytest.raises(ValueError, match="No items"):
            await last(gen)

    @pytest.mark.asyncio
    async def test_to_array(self):
        from packages.agnt_utils.generators import from_array, to_array

        gen = from_array([1, 2, 3])
        result = await to_array(gen)
        assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_to_array_empty(self):
        from packages.agnt_utils.generators import from_array, to_array

        gen = from_array([])
        result = await to_array(gen)
        assert result == []

    @pytest.mark.asyncio
    async def test_merge_concurrent(self):
        from packages.agnt_utils.generators import from_array, merge_concurrent, to_array

        gens = [from_array([1, 2]), from_array([3, 4])]
        result = await to_array(merge_concurrent(gens))
        assert sorted(result) == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_merge_concurrent_empty(self):
        from packages.agnt_utils.generators import merge_concurrent, to_array

        result = await to_array(merge_concurrent([]))
        assert result == []

    @pytest.mark.asyncio
    async def test_merge_concurrent_with_cap(self):
        from packages.agnt_utils.generators import from_array, merge_concurrent, to_array

        gens = [from_array([i]) for i in range(5)]
        result = await to_array(merge_concurrent(gens, concurrency_cap=2))
        assert sorted(result) == [0, 1, 2, 3, 4]


# ═══════════════════════════════════════════════════════════════════════
# format_utils
# ═══════════════════════════════════════════════════════════════════════
class TestFormatUtils:
    """Tests for packages.agnt_utils.format_utils."""

    def test_format_file_size_bytes(self):
        from packages.agnt_utils.format_utils import format_file_size

        assert format_file_size(500) == "500 bytes"

    def test_format_file_size_kb(self):
        from packages.agnt_utils.format_utils import format_file_size

        assert format_file_size(1536) == "1.5KB"

    def test_format_file_size_mb(self):
        from packages.agnt_utils.format_utils import format_file_size

        result = format_file_size(1_048_576)
        assert "MB" in result

    def test_format_file_size_gb(self):
        from packages.agnt_utils.format_utils import format_file_size

        result = format_file_size(2 * 1024 * 1024 * 1024)
        assert "GB" in result

    def test_format_seconds_short(self):
        from packages.agnt_utils.format_utils import format_seconds_short

        assert format_seconds_short(1234) == "1.2s"

    def test_format_duration_zero(self):
        from packages.agnt_utils.format_utils import format_duration

        assert format_duration(0) == "0s"

    def test_format_duration_seconds(self):
        from packages.agnt_utils.format_utils import format_duration

        assert format_duration(5000) == "5s"

    def test_format_duration_minutes(self):
        from packages.agnt_utils.format_utils import format_duration

        assert format_duration(90000) == "1m 30s"

    def test_format_duration_hours(self):
        from packages.agnt_utils.format_utils import format_duration

        result = format_duration(3661000)
        assert "1h" in result

    def test_format_duration_most_significant(self):
        from packages.agnt_utils.format_utils import format_duration

        assert format_duration(90000, most_significant_only=True) == "1m"

    def test_format_duration_hide_zeros(self):
        from packages.agnt_utils.format_utils import format_duration

        assert format_duration(3600000, hide_trailing_zeros=True) == "1h"

    def test_format_number(self):
        from packages.agnt_utils.format_utils import format_number

        assert format_number(1321) == "1.3k"
        assert format_number(900) == "900"

    def test_format_tokens(self):
        from packages.agnt_utils.format_utils import format_tokens

        result = format_tokens(1000)
        assert "k" in result

    def test_format_relative_time_past(self):
        from datetime import datetime, timedelta
        from packages.agnt_utils.format_utils import format_relative_time

        now = datetime.now(UTC)
        past = now - timedelta(hours=3)
        result = format_relative_time(past, now=now)
        assert result == "3h ago"

    def test_format_relative_time_future(self):
        from datetime import datetime, timedelta
        from packages.agnt_utils.format_utils import format_relative_time

        now = datetime.now(UTC)
        future = now + timedelta(days=2)
        result = format_relative_time(future, now=now)
        assert result == "in 2d"

    def test_format_relative_time_seconds(self):
        from datetime import datetime, timedelta
        from packages.agnt_utils.format_utils import format_relative_time

        now = datetime.now(UTC)
        recent = now - timedelta(seconds=30)
        result = format_relative_time(recent, now=now)
        assert result == "30s ago"


# ═══════════════════════════════════════════════════════════════════════
# array_utils
# ═══════════════════════════════════════════════════════════════════════
class TestArrayUtils:
    """Tests for packages.agnt_utils.array_utils."""

    def test_intersperse(self):
        from packages.agnt_utils.array_utils import intersperse

        assert intersperse([1, 2, 3], lambda i: 0) == [1, 0, 2, 0, 3]

    def test_intersperse_empty(self):
        from packages.agnt_utils.array_utils import intersperse

        assert intersperse([], lambda i: 0) == []

    def test_intersperse_single(self):
        from packages.agnt_utils.array_utils import intersperse

        assert intersperse([1], lambda i: 0) == [1]

    def test_count(self):
        from packages.agnt_utils.array_utils import count

        assert count([1, 2, 3, 4, 5], lambda x: x > 3) == 2

    def test_count_empty(self):
        from packages.agnt_utils.array_utils import count

        assert count([], lambda x: True) == 0

    def test_uniq(self):
        from packages.agnt_utils.array_utils import uniq

        assert uniq([1, 2, 1, 3, 2]) == [1, 2, 3]

    def test_uniq_empty(self):
        from packages.agnt_utils.array_utils import uniq

        assert uniq([]) == []

    def test_group_by(self):
        from packages.agnt_utils.array_utils import group_by

        result = group_by(["a", "bb", "c", "dd"], lambda x, i: len(x))
        assert result == {1: ["a", "c"], 2: ["bb", "dd"]}

    def test_group_by_empty(self):
        from packages.agnt_utils.array_utils import group_by

        result = group_by([], lambda x, i: x)
        assert result == {}


# ═══════════════════════════════════════════════════════════════════════
# Integration: import from __init__
# ═══════════════════════════════════════════════════════════════════════
class TestBatch3Integration:
    """Verify all Batch 3 symbols are importable from the package root."""

    def test_json_imports(self):
        from packages.agnt_utils import (
            safe_parse_json,
        )

        assert callable(safe_parse_json)

    def test_set_imports(self):
        from packages.agnt_utils import (
            difference,
        )

        assert callable(difference)

    def test_signal_imports(self):
        from packages.agnt_utils import create_signal

        assert callable(create_signal)

    def test_diff_imports(self):
        from packages.agnt_utils import (
            get_patch_from_contents,
        )

        assert callable(get_patch_from_contents)

    def test_treeify_import(self):
        from packages.agnt_utils import treeify

        assert callable(treeify)

    def test_combined_abort_imports(self):
        from packages.agnt_utils import create_combined_abort

        assert callable(create_combined_abort)

    def test_generator_imports(self):
        from packages.agnt_utils import last

        assert callable(last)

    def test_format_imports(self):
        from packages.agnt_utils import (
            format_duration,
        )

        assert callable(format_duration)

    def test_array_imports(self):
        from packages.agnt_utils import intersperse

        assert callable(intersperse)
