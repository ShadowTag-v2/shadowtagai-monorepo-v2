# BEADS OPERATING MODEL

## System Objective
The `pnkln` Beads infrastructure provides an atomic, immutable, and strictly ordered ledger for agent memory across session lifetimes. By replacing sprawling, contradictory contextual blobs with explicit JSONL entries (`beads`), future agent invocations can instantly query the latest deterministic truth without hallucination.

## The Hierarchy of Truth
Within the `Monorepo-Uphillsnowball` context, truth is strictly gated in descending order:
1. **`AGENTS.md`**: Outranks all imported prompt packs.
2. **`monorepo_manifest.yaml`**: The physical disk/workspace truth.
3. **`antigravity-mcp-config.json`**: The canonical MCP configuration truth.
4. **`.beads/issues.jsonl`**: The historical memory and recovery footprint. 

_Note: Beads serve as a **memory and recovery infrastructure**, never as a second control plane that supersedes the physical `AGENTS.md`._

## The Two-Stage Thread Recovery Protocol
Whenever an agent enters a highly complex, historically fragmented environment, it MUST utilize the **Two-Stage Thread Recovery Protocol** (`/thread-recovery-2stage`):
1. **Stage 1 (Audit)**: Execute `/thread-audit`. Read all active beads. Identify all gaps, contradictions, and missing code paths without regenerating output.
2. **Stage 2 (Regenerate)**: Execute `/thread-regenerate`. Rebuild the plan natively, explicitly superseding old beads with new structural truth.

## Supersession Mechanics
Truth evolves. When assumptions change or artifacts are refactored, the older bead MUST NOT be deleted. It must be explicitly superseded.

- **Status Transition**: The old bead changes from `active` to `superseded` (or `archived`).
- **Traceability**: The new bead explicitly lists the old bead's ID in its `"supersedes": []` array.
- **Enforcement**: Agents must use `tools/beads_manager.py supersede --ids <old> --replacement-id <new>` to encode this matrix natively.

## Ingestion Discipline
When synthesizing thread logs or external findings into beads:
- **Atomicity**: One prompt, one decision, or one config per bead. Do not create mega-beads.
- **Classification**: Accurately tag the `type` (`decision`, `code_artifact`, `system_directive`, etc).
- **Quarantine**: If an assumption is highly risky or low-trust (e.g. untested God Mode scripts), tag it as `quarantined`. Agents must filter out quarantined beads from standard execution paths.

By rigorously adhering to this model, the agent swarm retains continuous, conflict-free memory across infinite session boundaries.
