# Rule 35 — Continuous Learning & Instinct System

Source: `everything-claude-code` continuous-learning-v2 (v2.1.0)

## Architecture

The instinct system turns sessions into reusable knowledge through atomic "instincts" — small learned behaviors with confidence scoring.

### Why Hooks > Skills for Observation
- Skills fire **50-80%** of the time (probabilistic, based on model judgment)
- Hooks fire **100%** of the time (deterministic)
- Hooks capture every tool call → no missed patterns

### Data Flow
```
Session Activity (in a git repo)
      │  Hooks capture prompts + tool use (100% reliable)
      │  + detect project context (git remote / repo path)
      ▼
observations.jsonl (project-scoped)
      │  Observer reads (background agent)
      ▼
PATTERN DETECTION
  * User corrections → instinct
  * Error resolutions → instinct
  * Repeated workflows → instinct
  * Scope decision: project or global?
      │
      ▼
instincts/personal/ (per-project or global)
      │  /evolve clusters + /promote
      ▼
evolved/ (skills, commands, agents)
```

## The Instinct Model

An instinct is an atomic learned behavior:

```yaml
id: prefer-functional-style
trigger: "when writing new functions"
confidence: 0.7
domain: "code-style"
source: "session-observation"
scope: project                      # or "global"
project_id: "a1b2c3d4e5f6"
project_name: "my-react-app"
```

### Properties
- **Atomic** — one trigger, one action
- **Confidence-weighted** — 0.3 (tentative) to 0.9 (near-certain)
- **Domain-tagged** — code-style, testing, git, debugging, workflow
- **Evidence-backed** — tracks source observations
- **Scope-aware** — project (default) or global

## Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

### Confidence Evolution
**Increases** when:
- Pattern repeatedly observed
- User doesn't correct suggested behavior
- Similar instincts from other sources agree

**Decreases** when:
- User explicitly corrects behavior
- Pattern not observed for extended periods
- Contradicting evidence appears

## Scope Decision Guide

| Pattern Type | Scope | Examples |
|-------------|-------|---------|
| Language/framework conventions | **project** | "Use React hooks", "Django REST" |
| File structure preferences | **project** | "Tests in `__tests__`/" |
| Code style | **project** | "Use functional style" |
| Error handling strategies | **project** | "Use Result type" |
| Security practices | **global** | "Validate user input" |
| General best practices | **global** | "Write tests first" |
| Tool workflow preferences | **global** | "Grep before Edit" |
| Git practices | **global** | "Conventional commits" |

## Promotion: Project → Global

Auto-promotion criteria:
- Same instinct ID in **2+ projects**
- Average confidence >= **0.8**

Manual promotion via `/promote [id]` command.

## File Structure

```
~/.claude/homunculus/
├── identity.json           # Profile, technical level
├── projects.json           # Registry: hash → name/path/remote
├── observations.jsonl      # Global observations (fallback)
├── instincts/
│   ├── personal/           # Global auto-learned
│   └── inherited/          # Global imported
├── evolved/
│   ├── agents/             # Generated agents
│   ├── skills/             # Generated skills
│   └── commands/           # Generated commands
└── projects/
    └── <hash>/             # Per-project isolation
        ├── project.json
        ├── observations.jsonl
        ├── instincts/personal/
        └── evolved/
```

## Project Detection Priority
1. `CLAUDE_PROJECT_DIR` env var (highest)
2. `git remote get-url origin` → hashed for portable project ID
3. `git rev-parse --show-toplevel` → fallback (machine-specific)
4. Global fallback if no project detected

## Integration with Dream Cycle (Rule 20)

During nightly `/dream` consolidation:
1. Review accumulated instincts with confidence < 0.5
2. Promote qualifying instincts (2+ projects, avg >= 0.8)
3. Cluster related instincts → evolve into skills/commands
4. Deduplicate overlapping instincts (conservative merge)
5. Apply Rule 20 team memory rules for shared environments

## Integration with Antigravity

In the Antigravity environment, continuous learning maps to:
- **LanceDB RAG pipeline** — observations feed the semantic memory store
- **Knowledge Items** — evolved instincts become curated KIs
- **Skills** — high-confidence global instincts become Antigravity skills
- **Rules** — crystallized patterns become `.claude/rules/*.md` entries
