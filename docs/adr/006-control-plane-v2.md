# ADR-006: Antigravity Control Plane v2.0

**Status:** Accepted
**Date:** 2026-04-27
**Decision Makers:** Founder
**Supersedes:** N/A (new capability)

## Context

Antigravity was being used as "just another editor" — a VS Code fork with MCP tools bolted on.
This created several failure modes:

1. **Agent Theater** — Plans claiming files exist, scripts failing silently, false confidence reports.
2. **Auth Fragmentation** — Three independent auth channels (CLI, MCP, ADC) with no unified verification.
3. **Invisible Failures** — No structured audit trail for agent actions; success assumed rather than verified.
4. **Destructive Defaults** — No guardrails preventing `rm`, `unlink`, or other irreversible operations.

The question: Should Antigravity remain a VS Code fork with agent capabilities, or should it be
repositioned as a **control plane** that happens to use VS Code as its rendering surface?

## Decision

**Reposition Antigravity as a control plane.** The 5-pillar architecture:

| Pillar | Purpose | Implementation |
|--------|---------|----------------|
| 1. VS Code Base Stabilization | Stable rendering surface | `pnkln.code-workspace` as sole entry point |
| 2. Agent Loop Hardening | Anti-theater verification | MCP-first routing, post-edit validation loop |
| 3. Remote Compute First-Class | Sovereign + cloud compute | Local ANE/MLX + Cloud Run + Colab |
| 4. Observable Actions | Verifiable trace for every action | `.beads/` audit trail, MCP fleet status table |
| 5. Reversible Actions | No destructive operations | RULE 00 Immutable Infrastructure, temporal rollback |

Key architectural decisions within the control plane:

- **MCP-First Routing**: If an operation CAN be performed by an MCP server, it MUST be.
- **Firebase Tool Bridge**: All agent-initiated Firebase mutations route through the Client Action Truth layer (validate→gate→hooks→execute→evidence→return).
- **Pre-Action Memory Gate**: Before every action, check KI summaries, verify MCP server health, establish temporal anchor, confirm auth state.
- **Post-Edit Validation Loop**: After every file modification, run `ruff check --fix` + `ruff format` (Python) or `biome check --fix` (TypeScript).

## Consequences

### Positive

- Eliminates agent theater through mandatory verification at every checkpoint.
- Unified auth model with explicit 3-layer awareness (CLI, MCP, ADC).
- Full audit trail via `.beads/issues.jsonl` for every agent action.
- Reversibility via RULE 00 and temporal rollback protocol.
- Remote compute dispatch rules prevent wasteful local execution of heavy workloads.

### Negative

- Higher cognitive overhead per session (pre-flight checks, MCP fleet verification).
- Potential latency increase from mandatory MCP routing vs direct terminal commands.
- Firebase Tool Bridge adds indirection to Firebase operations (acceptable for safety guarantees).

### Neutral

- VS Code extension ecosystem remains fully available (extensions are additive, not replacements).
- Claude Code, Cline, Cursor remain secondary agents governed by AGENTS.md (not second control planes).

## References

- [ANTIGRAVITY_CONTROL_PLANE.md](../ANTIGRAVITY_CONTROL_PLANE.md) — Full specification
- [AGENTS.md Core Truth #19](../../.ruler/AGENTS.md) — Canonical registration
- [Firebase Tool Bridge](../../packages/firebase_tool_bridge/) — Client Action Truth implementation
- [RULE 00](../../.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md) — Immutable Infrastructure law
