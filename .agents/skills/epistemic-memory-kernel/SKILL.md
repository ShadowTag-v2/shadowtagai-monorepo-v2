---
name: epistemic-memory-kernel
description: Replaces unstructured markdown memory with typed knowledge atoms (fact, belief, constraint) enforcing Confidence Scores and Time-to-Live (TTL). Adapted from mainion-ai/memory-kernel patterns.
---

# Epistemic Memory Architecture

## The Doctrine of Knowledge Atoms

All Knowledge Intelligence (KI) files must now act as "Atoms". An Atom is a Markdown file with strict YAML frontmatter that encodes **epistemic status** — not just _what_ you know but _how confident_ you are and _when you should forget_.

## Atom Types (9 Types)

| Type | TTL | Weight in Recall | Purpose |
|------|-----|------------------|---------|
| `fact` | ∞ (permanent) | High | Verified truths |
| `decision` | ∞ (permanent) | Highest | Architecture/design choices |
| `constraint` | ∞ (permanent) | Highest | Rules and boundaries |
| `belief` | 30 days | Medium | Hypotheses, not yet verified |
| `preference` | 180 days | Low | User/agent preferences |
| `open_question` | 90 days | Medium | Unresolved questions |
| `procedure` | ∞ (permanent) | Medium | How-to instructions |
| `entity_summary` | 180 days | Low | Descriptions of key things |
| `conflict` | 30 days | High (alert) | Contradicting information |

## Frontmatter Schema

Every KI artifact MUST include this YAML frontmatter:

```yaml
---
id: "TYPE-YYYY-MM-DD-SLUG-hash"
type: fact | decision | constraint | belief | preference | open_question | procedure | entity_summary | conflict
status: draft | active | archived | expired | superseded
confidence: 0.85  # Float 0.0–1.0
ttl_days: 0        # 0 = permanent, 30 = beliefs, 90 = questions
created: "2026-04-22T23:00:00Z"
updated: "2026-04-22T23:00:00Z"
scope:
  tags: ["counselconduit", "stripe", "billing"]
classification: PUBLIC | TEAM | PERSONAL | SECRET
relations:
  - type: extends | supports | contradicts | caused_by | supersedes | applied_to | related
    target: "FACT-2026-04-20-uuid7-fallback"
---
```

## Lifecycle Rules

### Confidence-Driven Promotion
- If a `belief` atom reaches confidence ≥ 0.9 AND is verified, **promote** it to a `fact` with TTL: 0.
- If a `belief` atom drops below confidence 0.3, **archive** it immediately.

### Temporal Decay
During Dream Consolidation nightly runs:
1. **Expire** atoms past their TTL → move to `ARCHIVE/` status.
2. **Dedup** identical content → merge (archive older).
3. **Detect conflicts** between overlapping atoms → create a `conflict` atom.

### Recall Ranking (when injecting KIs into context)
```
BM25 keyword match
  → Temporal decay: exp(-λ × age_days), half_life = 30d
    → Type weighting: constraint=2.0, decision=2.0, belief=0.8
      → Token budget enforcement (two-pass reservation)
```

## Anti-Patterns (PROHIBITED)

- Storing beliefs as facts (inflates confidence, resists self-correction).
- Setting TTL: 0 on debugging hypotheses (they become immortal noise).
- Skipping confidence scoring on new KIs (all atoms MUST have a score).
- Treating all knowledge equally regardless of age (apply temporal decay).

## Integration with Dream Consolidation

Update `scripts/dream_consolidation.py` to:
1. Parse YAML frontmatter from KI artifacts.
2. Apply TTL expiry (archive atoms past due).
3. Apply confidence decay (reduce confidence by 0.05/month for unverified beliefs).
4. Generate auto-views: `INDEX.md`, `HANDOFF.md`, `DECISIONS.md`, `CONSTRAINTS.md`.
5. Run spreading activation (wander) to find collision candidates before merging.

## Token Budget Allocation

When injecting KIs into agent context:
- **Pass 1 (Reserved):** `constraint` + `decision` atoms with confidence ≥ 0.9 get guaranteed slots.
- **Pass 2 (Ranked):** Remaining budget filled by BM25 + temporal decay ranking.
- **Budget ceiling:** Never inject more than 8,000 tokens of KI context.
