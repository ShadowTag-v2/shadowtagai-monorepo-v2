# 3-Layer Memory Architecture — Pointer Index Specification

> Source: Claude Code v2.1.91, Dream memory consolidation (v2.1.98), `src/memdir/`
> Intelligence classification: Adopted pattern for persistent agent memory

## Overview

Claude Code implements a **3-layer memory hierarchy** that separates concerns:
- **Index**: Pointer file (<25KB) — fast scan, one-line hooks
- **Topic files**: Domain-specific knowledge (<10KB each)
- **Archive**: Immutable session transcripts (JSONL)

This architecture solves the "memory dump" anti-pattern where agents store everything
in a flat text file and hit context limits.

## Layer 1: Index File

**Path**: `~/.claude/memory/INDEX.md`
**Format**: One-line pointers, max 150 chars per entry
**Size limit**: 25KB / INDEX_MAX_LINES (configurable, default ~200 lines)

```markdown
# Memory Index

## Active Projects
- shadowtag-omega-v4: CounselConduit legal AI platform → topic/counselconduit.md
- kovelai: Landing page + frontend → topic/kovelai.md
- uphillsnowball: Monorepo governance → topic/uphillsnowball.md

## Key Decisions (2026-04)
- 2026-04-18: Switched to CPython 3.14.3, venv rebuilt → topic/python_env.md
- 2026-04-18: Judge 6 BLOCK/ALLOW spec finalized → topic/Claude_Code_6.md
- 2026-04-17: Firebase MCP-first deployment doctrine → topic/firebase_deploy.md

## People & Accounts
- Erik (founder): Full context in topic/founder.md
- GitHub App ID 3018200, Stripe acct_1Syh9JEHnWpykeMi → topic/credentials.md

## Architecture Patterns
- 4-layer context compaction → topic/context_compaction.md
- KV Slab caching (Aegaeon) → topic/kv_caching.md
- Oracle Studio 7-stage pipeline → topic/oracle_studio.md
```

### Key Properties
1. **Pointer-only**: Index entries MUST link to topic files, never contain detail
2. **Absolute dates**: All dates are ISO-8601. NEVER use relative dates ("yesterday", "last week")
3. **One-line hooks**: Each entry ≤ 150 chars. If more context needed → topic file
4. **Pruning**: When index exceeds INDEX_MAX_LINES, oldest entries are migrated to archive

## Layer 2: Topic Files

**Path**: `~/.claude/memory/topic/<name>.md`
**Format**: Structured markdown with key-value pairs
**Size limit**: 10KB per topic file

```markdown
# CounselConduit

## Status: Phase 2 LIVE (v3.1.0)
## Cloud Run URL: https://counselconduit-767252945109.us-central1.run.app
## Service Account: counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com

## Architecture
- FastAPI + Uvicorn on Cloud Run
- 33 API modules
- LiteLLM multi-model routing (Gemini, Claude, GPT)
- Firestore persistence (shadowtag-engine database)
- Stripe Connect dual billing

## Key Decisions
- 2026-04-18: RBAC + HMAC webhooks + Cloud Armor WAF deployed
- 2026-04-15: Judge 6 process framework → .NET Semantic Kernel
- 2026-04-10: Oracle Studio 7-stage pipeline designed

## Open Items
- [ ] Phase 3: Sandboxed tool runners
- [ ] Phase 4: BYOC/BYOK + FedRAMP
```

### Key Properties
1. **Domain-scoped**: One topic per domain/concern. No cross-cutting topics.
2. **Living document**: Updated on every relevant interaction
3. **Contradiction resolution**: When new info contradicts old → UPDATE old, don't append
4. **Absolute dates**: Every date is absolute. Dream consolidation converts relative → absolute.

## Layer 3: Archive (Immutable Transcripts)

**Path**: `~/.claude/memory/archive/<date>.jsonl`
**Format**: JSONL (one JSON object per line)
**Retention**: Based on configured policy (default: 30 days)

```jsonl
{"ts":"2026-04-18T17:34:30Z","type":"decision","topic":"Claude_Code_6","content":"Finalized BLOCK/ALLOW spec with 16 BLOCK rules and 8 ALLOW exceptions"}
{"ts":"2026-04-18T16:46:17Z","type":"finding","topic":"cl4r1t4s","content":"Identified 6 adoptable patterns from Claude Code competitive analysis"}
{"ts":"2026-04-18T15:20:00Z","type":"action","topic":"infrastructure","content":"OpenTofu drift resolved: notification channel sync"}
```

### Key Properties
1. **Immutable**: Archive entries are NEVER modified after write
2. **Narrow search**: Dream process searches archives narrowly, never exhaustively
3. **Typed entries**: `decision`, `finding`, `action`, `error`, `learning`
4. **Topic-tagged**: Every entry links to a topic file for cross-reference

## Dream Consolidation Protocol (4-Phase)

**Trigger**: KAIROS daemon `/dream` cycle (nightly or on-demand)

### Phase 1: Orient
```
1. Read INDEX.md
2. list topic/ directory
3. Skim each topic file (first 20 lines only)
4. Build mental map of current state
```

### Phase 2: Gather
```
1. Read today's session transcript logs
2. grep archive/ for specific topics (narrow scope, NOT exhaustive)
3. Identify drifted memories (contradictions, stale info)
4. Collect raw material for consolidation
```

### Phase 3: Consolidate
```
1. Merge new learnings into existing topic files
2. Convert ALL relative dates → absolute dates
3. Resolve contradictions (new info wins, old is deleted)
4. Create new topic files for new domains
5. Update INDEX.md with new pointers
```

### Phase 4: Prune
```
1. If INDEX.md > INDEX_MAX_LINES → move oldest to archive
2. If any topic file > 10KB → split into sub-topics
3. Verify all index pointers have valid targets
4. Delete orphaned topic files with no index reference
```

## Our Equivalent: KI System Mapping

| CC Layer | Our Layer | Status |
|----------|----------|--------|
| INDEX.md | `knowledge/*/metadata.json` summaries | ✅ Functional |
| Topic files | `knowledge/*/artifacts/*.md` | ✅ Functional |
| Archive | `brain/<conversation-id>/.system_generated/logs/` | ✅ Functional |
| Dream consolidation | Session wrap-up + KI creation | 🟡 Manual only |

### Gaps
1. **Automated contradiction detection**: KIs don't auto-resolve contradictions
2. **Index pruning**: No automatic size limits on KI summaries
3. **Relative date conversion**: Not enforced
4. **Narrow archive search**: Brain logs are searched exhaustively, not narrowly
5. **Dream automation**: KAIROS daemon exists but doesn't run consolidation

### Recommendations
1. Implement automated Dream cycle in KAIROS daemon
2. Add KI size limits (25KB index, 10KB per artifact)
3. Enforce absolute date conversion in session-wrap-up skill
4. Add contradiction detection to KI creation workflow

---

*Document version: 1.0 | Source: Claude Code v2.1.98 Dream spec + src.zip memdir/*
*Last updated: 2026-04-18*
