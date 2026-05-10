# Component Spec: Typed Inter-Daemon Messaging

> **Source:** `external_repos/everything-claude-code/ecc2/src/comms/mod.rs` (157L Rust)
> **Target:** `packages/aiyou-core/messaging.py`
> **Priority:** P0 | **Effort:** 4 hours

## Problem

5-daemon fleet communicates via untyped JSON in `.beads/`. No schema enforcement, no priority routing, no conflict detection.

## Message Types (from ECC2)

- `TaskHandoff` — task + context + priority
- `Query` — question string
- `Response` — answer string  
- `Completed` — summary + files_changed list
- `Conflict` — file + description

## Priority Levels

LOW | NORMAL (default) | HIGH | CRITICAL

## Core Functions

- `send(from_, to, msg) -> str` — serialize + dispatch
- `parse(content) -> MessageVariant | None` — safe deser
- `preview(msg) -> str` — human-readable truncated summary
- `truncate(text, max_chars) -> str` — Unicode-safe ellipsis

## Storage

`.beads/messages/{timestamp}_{from}_{to}_{type}.json`

## Test Requirements: 21 tests minimum

## Dependencies: pydantic, uuid7, StrEnum (Python 3.14)
