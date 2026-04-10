# BEADS_SCHEMA.md

## Purpose

This document defines the canonical bead schema for pnkln.

The goals are:

- durable institutional memory
- atomic entries
- explicit supersession
- clean retrieval
- separation of active truth from historical sludge

## Storage model

Primary store:

- `.beads/issues.jsonl`

Optional supporting files:

- `.beads/archive.jsonl`
- `.beads/index.json`

## Record format

Each line in `.beads/issues.jsonl` is one JSON object.

Required fields:

- `id` — unique stable identifier
- `timestamp` — ISO 8601 timestamp
- `type` — one of the allowed bead types
- `title` — short human-readable name
- `status` — one of the allowed statuses
- `source` — where it came from
- `tags` — array of tags
- `supersedes` — array of bead IDs replaced by this bead
- `content` — payload
- `description` — short explanation

Recommended fields:

- `format` — `text`, `json`, `markdown`, `python`, `yaml`, `shell`, `prompt`, etc.
- `path_hint` — intended file path if relevant
- `family` — logical grouping name
- `priority` — `low`, `medium`, `high`, `critical`
- `author` — human or agent label

## Canonical schema

```json
{
  "id": "string",
  "timestamp": "2026-03-16T01:55:39-07:00",
  "type": "system_directive",
  "title": "Cor Rules Master Prompt",
  "status": "active",
  "source": "thread",
  "format": "xml-like-prompt",
  "tags": ["security", "architecture"],
  "supersedes": [],
  "path_hint": "",
  "family": "cor_rules",
  "priority": "high",
  "content": "string or object",
  "description": "short summary"
}
```

Allowed statuses

- active: Current truth. Returned by default.
- historical: Past but still meaningful context.
- reference_only: Keep for intent or background, not for direct execution.
- superseded: Replaced by a newer bead. Never returned by default.
- quarantined: Unsafe, low-trust, malformed, or contradictory material.
- archived: Moved out of the active working set.

Allowed types

- system_directive
- control_plane_operation
- code_artifact
- workflow_definition
- decision
- assumption
- risk
- supersession
- thread_recovery_finding
- product_constraint
- runtime_config
- file_manifest
- merge_status
- prompt_template

Retrieval precedence

Default retrieval order:

1. active
2. historical
3. reference_only

Never return by default:

- superseded
- quarantined
- archived

Supersession rules

A bead may supersede one or more older beads.

Rules:

1. New truth must explicitly list old bead IDs in supersedes.
2. Superseded beads should have status changed to superseded.
3. Query results must prefer the newest active bead in a family.
4. Do not delete superseded beads unless separately archived.

Atomicity rules

One bead should contain one coherent unit of memory.

Good:

- one prompt
- one decision
- one config artifact
- one merge finding

Bad:

- giant mixed blob containing prose, code, shell, strategy, and deployment notes all at once

Ingestion rules

When new thread material arrives:

1. split large content into atomic units
2. classify each bead
3. set status
4. attach tags
5. mark supersession if applicable
6. quarantine unsafe or malformed material
7. append to `.beads/issues.jsonl`

Query rules

All query tools should support:

- filter by status
- filter by type
- filter by tags
- filter by family
- latest active in family
- supersession resolution

pnkln policy

- `AGENTS.md` outranks imported prompt packs
- `monorepo_manifest.yaml` is workspace truth
- `antigravity-mcp-config.json` is MCP truth
- beads are memory and recovery infrastructure, not a second control plane
