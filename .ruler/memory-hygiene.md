# Memory Hygiene Protocol — Ruler Propagated Rule

## Freshness Order

When sources disagree on material facts, use this precedence:

1. **Current user message** — always wins
2. **Explicit repo state** — live code, configs, manifests
3. **Recent commits** — last 10 commits
4. **Open Beads issue** — active task context
5. **Active Memory atom** — `.memory/atoms/**` with `status: active`
6. **Current docs** — `docs/**`
7. **Code comments** — inline documentation
8. **Old handoff** — archived session notes, transfer packages

## Conflict Resolution

When two or more sources disagree on a material fact:

1. **STOP** synthesis immediately.
2. **CITE** the conflicting sources by name/path.
3. **CHOOSE** the highest-freshness source by this order, OR
4. **ESCALATE** to the user if the conflict is ambiguous.
5. **NEVER** blend contradictory instructions silently.
6. **NEVER** treat an old handoff as current without verifying against live code.

## Memory Triage (Surprise-Based)

| Event Type          | Action                                           |
|---------------------|--------------------------------------------------|
| Routine fact        | Evidence only                                    |
| Repeated pattern    | Create Memory atom                               |
| New failure mode    | Beads issue + fixture                            |
| High-surprise event | Memory atom + Beads issue + invariant candidate  |

## Contract

See: `tool_contracts/memory.resolve_conflict.yaml`

## Invariant

See: Invariant #125 (Stop On Memory Conflict)
