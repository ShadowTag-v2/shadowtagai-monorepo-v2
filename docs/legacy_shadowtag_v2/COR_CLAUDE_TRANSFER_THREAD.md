# Cor.Claude Transfer Thread

**Comprehensive Context Handoff for Claude-Based AI Agents**

> **Purpose**: Single source of truth for continuing work across Claude sessions, compiling all conversation history and extracted business/code plans.
> **Created**: 2026-01-30
> **Status**: Active Compilation

---

## 1. Conversation History Sources

### 1.1 Claude Code CLI Sessions (Primary)

**Current User**: `/Users/pikeymickey/.claude/projects/-Users-pikeymickey/`

- **Active Session**: `367cc1c1-7469-41b4-b1c1-638bf6807436.jsonl` (55MB)
- **Previous Sessions**: 10+ session files totaling 150MB+

**Deleted Users Recovery**: `~/.claude/projects_imported/`

- **Largest Session**: `5a24baa6-fb10-4f13-808e-b36839f18f58.jsonl` (89MB)
- **Additional**: 45+ session files totaling 200MB+
- **Contains**: Nov 19-29 2025 intensive development period

### 1.2 Claude Desktop App

**Location**: `~/Library/Application Support/Claude/`

- `claude-code-sessions/` - Limited session data
- `config.json` - MCP server configurations
- `Claude Extensions/` - Browser extension data

### 1.3 ChatGPT Exports (Incomplete)

**Status**: Needs full export from https://chatgpt.com/settings
**Current Export**: `/Users/pikeymickey/Downloads/ChatGPT data/conversations.json` (1 conversation only)
**Action Required**:

1. Go to https://chatgpt.com/settings
2. Click "Export data"
3. Wait for email with download link
4. Extract to `/Users/pikeymickey/Downloads/ChatGPT data/`

### 1.4 Antigravity/Gemini Sessions

**Logs**: `~/Library/Application Support/Antigravity/logs/`
**Browser Profile**: `~/.gemini/antigravity-browser-profile/`

---

## 2. Extracted Business Plans (Keyword Analysis)

From Claude history keyword analysis:

| Keyword    | Mentions | Context                   |
| ---------- | -------- | ------------------------- |
| MVP        | 2000+    | Multiple MVP iterations   |
| Phase 1-7  | 3200+    | Detailed phase planning   |
| Revenue    | 900+     | Revenue model discussions |
| Valuation  | 700+     | Valuation analysis        |
| Pitch Deck | 330+     | Investor materials        |
| Launch     | 450+     | Launch planning           |
| Milestone  | 136+     | Project milestones        |

---

## 3. Business Documentation Index

### Core Plans (20+ documents)

Located at `/docs/`:

1. **BUSINESS_MASTER.md** - Synthesized master plan (ShadowTag Omega)
2. **BUSINESS_PLAN.md** - Original business plan
3. **BUSINESS_PLAN_12_MONTH.md** - 12-month execution plan
4. **INVESTOR_PITCH.md** - Investor presentation
5. **Pinkln-Ultrathink-Investor-Deck.md** - pnkln deck
6. **PINKLN_UNIFIED_PLAN.md** - Unified strategy
7. **COR_22_JUDGE6_REVENUE.md** - Judge6 revenue model
8. **cor8_master_plan.md** - Cor8 orchestration
9. **COST_REVENUE_ANALYSIS.md** - Financial analysis
10. **decaunicorn_plan.md** - Decaunicorn strategy
11. **INTEGRATION_ROADMAP.md** - Technical roadmap
12. **INEVITABLE_STACK_PLAN.md** - Stack architecture
13. **SHADOWTAGAI_MASTER_PLAN.md** - ShadowTag strategy

### Subdirectories

- `/docs/business/` - Business documents
- `/docs/business_plans/` - Plan versions
- `/docs/roadmap/` - Roadmap documents

---

## 4. Technical Context

### Product Stack

| Product          | Purpose                                   | Status               |
| ---------------- | ----------------------------------------- | -------------------- |
| **Pipeline**     | CI/CD + Agent orchestration               | Active               |
| **Core Swarm**   | https://github.com/karpathy/autoresearchs | 650 Agents           |
| **Governance**   | JudgeJura #6                              | ATP 5-19             |
| **Framework**    | ExToto                                    | ID/EGO/SUPEREGO      |
| **Code Quality** | CODEPMCS                                  | 50-Agent Remediation |
| **ShadowTag**    | Cryptographic watermarking                | Building             |

### Monorepo Structure

```
pnkln-stack-stack/ShadowTag-v2/
├── branches/           # 297 feature branches (29MB)
├── repos/              # 18 core repos
├── external_repos/     # 22+ external dependencies
├── docs/               # 320 documentation files
├── src/                # Source code
└── scripts/            # Automation scripts
```

### Repository Consolidation

- **424 symlinks** in Documents/GitHub pointing to monorepo
- **264 real repos** consolidated to `external_repos/github_consolidated/`
- **Total**: 688 repos organized

---

## 5. Session Continuity Checklist

When starting a new Claude session:

1. [ ] Read `/pnkln-stack-stack/ShadowTag-v2/CLAUDE.md` (project memory)
2. [ ] Check `git status` for uncommitted work
3. [ ] Review `/docs/BUSINESS_MASTER.md` for business context
4. [ ] Check `/docs/business_plans/` for latest plans

### Key Contacts & Credentials

- **GitHub**: ehanc69 / ShadowTag-v2
- **GCP Project**: shadowtagai-production
- **Domain**: shadowtagai.com

---

## 6. Immediate Action Items

### Completed (2026-01-30)

- [x] Extract 297 feature branches (29MB, 873K lines)
- [x] Close 6 conflicting PRs on ehanc69/pnkln-stack-fastapi-services
- [x] Consolidate 687 Documents/GitHub repos
- [x] Initialize git-lfs
- [x] Copy Deleted Users Claude history

### Pending

- [ ] Full ChatGPT export (manual action required)
- [ ] Verdict Systems TODOs (~20+ items in schiznit_engine.py)
- [ ] Claude web history extraction (limited API access)

---

## 7. Revenue Model Summary

From ANTIGRAVITY_HANDOFF.md:

```
Month 1-2 (Beachhead): 10M decisions/year = $3,000 MRR
Month 3-6 (Scale):     100M decisions/year = $30,000 MRR
Month 12+ (Revenue):   1B decisions/year = $300,000 MRR

Pricing:
- $0.0003/decision (Judge#6)
- $0.002/tag (ShadowTag)
- $499/mo + $0.01/decision (pnkln-stack)
- $5,000/mo + $50k setup (Enterprise)

Target: $2.1M ARR Y1 → $15M ARR Y3
```

---

## 8. Founder Profile

```
ERIK HANCOCK | SOLE FOUNDER | "TINY TEAMS" PHILOSOPHY
├─ AGE: 56
├─ CREDENTIALS: JD, BA History/German
├─ TRAITS: Neurodivergent | IQ-160 Lock Required
├─ PHILOSOPHY: $1B Revenue before first hire
├─ STRUCTURE: Perpetual Family Corp (Panama Foundation)
└─ URGENCY: NEED CASH IMMEDIATELY
```

---

_Last Updated: 2026-01-30 13:50 UTC_
_Next Session: Continue from this document_
