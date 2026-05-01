# agnt_utils API Reference

> **Version:** 3.0 (Batch 1 + 2 + 3) | **Source:** `packages/agnt_utils/`
> **Origin:** Ported from Claude Code v2.1.91 `utils/` directory

## Module Index

| # | Module | Origin | Category |
|---|--------|--------|----------|
| 1 | `token_budget` | `budget.ts` | Context Management |
| 2 | `circular_buffer` | `circular-buffer.ts` | Data Structures |
| 3 | `activity_manager` | `activity-tracking.ts` | Session |
| 4 | `memoize` | `memoize.ts` | Performance |
| 5 | `token_estimate` | `token-estimation.ts` | Context Management |
| 6 | `truncate` | `truncate.ts` | Display |
| 7 | `sequential` | `sequential.ts` | Concurrency |
| 8 | `sanitization` | `sanitization.ts` | Security |
| 9 | `errors` | `errors.ts` | Error Handling |
| 10 | `string_utils` | `string.ts` | Text Processing |
| 11 | `hash_utils` | `hash.ts` | Cryptography |
| 12 | `xml_escape` | `xml-escape.ts` | Security |
| 13 | `sleep_utils` | `sleep.ts` | Concurrency |
| 14 | `json_utils` | `json.ts` | Serialization |
| 15 | `set_ops` | `set.ts` | Data Structures |
| 16 | `signal` | `signal.ts` | Events |
| 17 | `diff_utils` | `diff.ts` | Code Analysis |
| 18 | `treeify` | `treeify.ts` | Display |
| 19 | `combined_abort` | `combined-abort.ts` | Cancellation |
| 20 | `generators` | `generators.ts` | Async |
| 21 | `format_utils` | `format.ts` | Display |
| 22 | `array_utils` | `array.ts` | Data Structures |

---

## Batch 1 — Core Infrastructure

### `token_budget`
Parse human-readable token budget directives like `"+500k"` or `"use 2M tokens"`.

```python
from agnt_utils import parse_token_budget, get_budget_continuation_message

budget = parse_token_budget("+500k")       # → 500_000
msg = get_budget_continuation_message(budget)
```

### `circular_buffer`
Fixed-size ring buffer with O(1) add and O(k) get_recent.

```python
from agnt_utils import CircularBuffer

buf = CircularBuffer(max_size=100)
buf.add("event-1")
recent = buf.get_recent(5)
```

### `memoize`
TTL + LRU memoization with write-through refresh.

```python
from agnt_utils import memoize_with_ttl, memoize_with_lru

@memoize_with_ttl(ttl_seconds=60)
def fetch_data(key): ...

@memoize_with_lru(max_size=128)
def compute(x, y): ...
```

### `token_estimate`
Heuristic token counting for context window management (calibrated against tiktoken).

```python
from agnt_utils import rough_token_estimate, token_count_with_estimation

tokens = rough_token_estimate("Hello, world!")  # ~3
total = token_count_with_estimation(messages)
```

### `truncate`
Width-aware text truncation for terminal UI.

```python
from agnt_utils import truncate, truncate_to_width, string_width

text = truncate("Very long text...", max_len=20)
path = truncate_path_middle("/very/long/path/to/file.py", width=30)
```

---

## Batch 2 — Security & Resilience

### `sequential`
Async sequential execution wrapper (race condition guard).

```python
from agnt_utils import sequential

@sequential
async def critical_update(data): ...
```

### `sanitization`
Unicode smuggling defense (HackerOne #3086545).

```python
from agnt_utils import partially_sanitize_unicode, recursively_sanitize_unicode

safe = partially_sanitize_unicode(untrusted_input)
deep_safe = recursively_sanitize_unicode(nested_data)
```

### `errors`
Structured error hierarchy + stack truncation.

```python
from agnt_utils import AgntError, AbortError, ShellError, error_message, short_error_stack

try:
    ...
except Exception as e:
    msg = error_message(e)
    stack = short_error_stack(e, max_frames=5)
```

### `string_utils`
String accumulators, truncation, formatting helpers.

```python
from agnt_utils import capitalize_first, plural, first_line_of, EndTruncatingAccumulator

label = plural(3, "file")  # "3 files"
acc = EndTruncatingAccumulator(max_chars=1000)
```

### `hash_utils`
Deterministic djb2 + SHA-256 hashing.

```python
from agnt_utils import djb2_hash, hash_content, hash_pair

h = djb2_hash("key")           # int
sha = hash_content("data")     # hex string
combined = hash_pair("a", "b")
```

### `xml_escape`
XML/HTML entity escaping for prompt safety.

```python
from agnt_utils import escape_xml, escape_xml_attr

safe = escape_xml("<script>alert('xss')</script>")
attr = escape_xml_attr('value with "quotes"')
```

### `sleep_utils`
Cancellable async sleep + timeout guards.

```python
from agnt_utils import cancellable_sleep, with_timeout

await cancellable_sleep(5.0, cancel_event=event)
result = await with_timeout(coro, timeout=30.0)
```

---

## Batch 3 — Data Processing & Display

### `json_utils`
Safe JSON/JSONL parsing with LRU-bounded caching.

```python
from agnt_utils import safe_parse_json, safe_parse_jsonc, parse_jsonl

data = safe_parse_json('{"key": "value"}')     # dict or None
jsonc = safe_parse_jsonc('// comment\n{"k": 1}')
records = parse_jsonl(text)
```

### `set_ops`
Hot-path optimized set operations (imperative + native variants).

```python
from agnt_utils import difference, intersects, union, unique

diff = difference(set_a, set_b)
has_overlap = intersects(set_a, set_b)
combined = union(set_a, set_b)
deduped = unique([1, 2, 2, 3])  # [1, 2, 3]
```

**Benchmark results (native vs imperative):**

| Operation | 100 items | 1K items | 10K items | 100K items |
|-----------|-----------|----------|-----------|------------|
| difference | 3.2x native wins | 1.1x native | 1.5x native | 2.7x native |
| intersects | 3.4x native wins | 1.0x tie | 1.8x native | 5.2x native |
| union | 18.3x native wins | 3.3x native | 2.9x native | 3.3x native |

> **Recommendation:** Use native variants (`difference_native`, etc.) for all new code. Imperative variants exist only for upstream TypeScript parity.

### `signal`
Tiny listener-set primitive for pure event signals.

```python
from agnt_utils import Signal, create_signal

sig = create_signal()
disposer = sig.on(lambda: print("fired!"))
sig.fire()
disposer()  # unsubscribe
```

### `diff_utils`
Hunk-based structured diff processing.

```python
from agnt_utils import get_patch_from_contents, count_lines_changed, apply_edits

hunks = get_patch_from_contents(old, new, file_path="main.py")
changes = count_lines_changed(hunks)  # LinesChanged(additions=5, removals=2)
result = apply_edits(content, [{"old_string": "foo", "new_string": "bar"}])
```

### `treeify`
Recursive tree visualization for CLI output.

```python
from agnt_utils import treeify

tree = treeify({
    "src": {
        "main.py": "120 lines",
        "utils": {
            "helpers.py": "45 lines",
        },
    },
    "tests": "32 files",
})
# ├ src
# │ ├ main.py: 120 lines
# │ └ utils
# │   └ helpers.py: 45 lines
# └ tests: 32 files
```

### `combined_abort`
Combined cancellation signal with timeout cleanup.

```python
from agnt_utils import CombinedAbort, create_combined_abort

abort = create_combined_abort(timeout=30.0)
if abort.is_aborted:
    raise AbortError("Operation cancelled")
```

### `generators`
Async generator manipulation utilities.

```python
from agnt_utils import from_array, to_array, last, merge_concurrent

items = await to_array(async_gen)
final = await last(async_gen)
```

### `format_utils`
Human-readable display formatters.

```python
from agnt_utils import format_duration, format_file_size, format_tokens

print(format_duration(125.7))    # "2m 5.7s"
print(format_file_size(1_500_000))  # "1.43 MB"
print(format_tokens(150_000))    # "150K tokens"
```

### `array_utils`
Functional array utilities (intersperse, count, group_by).

```python
from agnt_utils import intersperse, count, group_by, uniq

items = intersperse([1, 2, 3], sep=0)  # [1, 0, 2, 0, 3]
n = count([1, 2, 3, 4], lambda x: x > 2)  # 2
groups = group_by(records, key=lambda r: r.type)
unique_items = uniq([1, 2, 2, 3])  # [1, 2, 3]
```

---

## Integration Modules

### `cli_diagnostics`
Pre-built diagnostic renderers using treeify.

```python
from agnt_utils.cli_diagnostics import render_diagnostic_report

print(render_diagnostic_report(
    test_results={"passed": 1559, "failed": 0, "skipped": 2},
))
```

### `telemetry/diff_telemetry`
OTel-backed diff instrumentation.

```python
from telemetry.diff_telemetry import DiffTelemetry

dt = DiffTelemetry(sink=my_sink)
hunks = dt.tracked_patch(old, new, file_path="main.py")
```
