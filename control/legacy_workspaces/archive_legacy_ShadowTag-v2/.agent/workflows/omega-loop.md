# Workflow: ShadowTag Omega Loop (V6 — Unified Memory + Gate 0)

**Trigger:** `/omega-loop`

---

## Session Preflight

```bash
export GCP_PROJECT_ID=shadowtag-omega-v4
export BRAIN_DIR=/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e5079
```

- If the UI prompts for `Tools Config Path`, use `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`.
- Prefer `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/.venv/bin/python`.
- Ensure `scripts/omega_auth_daemon.py` is alive before cloud operations.
- Persist notable actions to `.beads/`.

## Architecture

```
Pre-Commit (Gate 0)          Agent Loop (Gates 1-5)         Persistence
┌─────────────────┐    ┌──────────────────────────┐    ┌────────────────┐
│ Biome            │    │ Semi-Formal Reasoning     │    │ Beads (Cold)   │
│ Design Tokens    │───►│ CodePMCS Scan/Fix         │───►│ Git-tracked    │
│ Judge#6 Secrets  │    │ Judge#6 Verdict           │    │ Audit ledger   │
└─────────────────┘    └──────────────────────────┘    └────────────────┘
                              │                              ▲
                              ▼                              │
                       ┌──────────────────────────┐          │
                       │ MCP Memory (Hot)          │──promote─┘
                       │ GPTRAM Verdict Cache      │
                       └──────────────────────────┘
```

---

## Directives

### 1. Hydrate (Restore Context)

```bash
python3 tools/unified_memory.py hydrate
```

- Loads last 10 Beads entries into MCP hot store
- Agent now has institutional memory of previous sessions
- Context: "You are resuming from this state."

### 2. Scan (Structural Compliance — Gate 0)

```bash
# Biome: format + lint
npx @biomejs/biome check --write .

# Design tokens: enforce --st-* usage
node tools/design-system-lint.mjs src/
```

- If Gate 0 fails → fix violations before proceeding
- All fixes logged to Beads: `DESIGN_LINT` tag

### 3. Analyze (Semi-Formal Reasoning — Gate 1)

For each file with logic changes:

- **Premises:** State what the code should do (from tests/spec)
- **Traces:** Walk execution paths through the change
- **Conclusion:** Equivalent/Non-equivalent with evidence

```bash
# Log analysis result to unified memory
python3 tools/unified_memory.py remember "Semi-formal analysis: [file] — [verdict]" ANALYSIS
```

### 4. Execute (Apply Fixes — Gate 2)

For every error found:

- **Judge:** Validate fix against `src/governance/judge.py`
- **GPTRAM:** Check verdict cache before calling LLM
  ```python
  from tools.unified_memory import UnifiedMemory
  mem = UnifiedMemory()
  cached = mem.get_verdict(code_context)
  if cached:
      # Use cached verdict (p99 ≤ 90ms)
  else:
      verdict = judge_six.evaluate(code_context)
      mem.cache_verdict(code_context, verdict)
  ```
- **Action:** If Safe → OVERWRITE file
- **Promote:** Write decision to both stores:
  ```python
  mem.set("last_fix", {"file": filename, "verdict": "PASS"})
  mem.remember(f"Fixed {error_type} in {filename}", tag="FIX")
  ```

### 5. Verify (Test Execution — Gate 3)

```bash
# Run tests
python3 -m pytest tests/ -x --tb=short

# If tests pass → commit
git add .
git commit -m "omega: [summary of fixes]"
```

### 6. Persist (Memory Consolidation)

```bash
# Final status check
python3 tools/unified_memory.py status
```

- Hot store entries older than 1hr auto-expire (TTL)
- Critical findings promoted to Beads survive indefinitely
- GPTRAM verdict cache persists for repeat query acceleration

### 7. Recurse

Move to next task/tab. The loop continues.

---

## Memory Tier Decision Matrix

| Signal                     | Store In        | Reason                          |
| -------------------------- | --------------- | ------------------------------- |
| Current patch hash         | MCP Hot         | Ephemeral, session-scoped       |
| Judge#6 verdict result     | GPTRAM          | Cache for p99 ≤ 90ms           |
| Security fix applied       | Beads (promote) | Audit trail, compliance         |
| Design token violation     | Beads           | Institutional pattern tracking  |
| Semi-formal analysis cert  | Beads           | Evidence chain for code review  |
| API call result            | MCP Hot (TTL)   | Cache, auto-expire in 1hr      |
| Agent session start/stop   | Beads           | Session history for hydration   |

---

## File Locations

```
ShadowTag-v2/
├── biome.json                         # Biome config (Gate 0 structural)
├── tokens.css                         # Design system source of truth
├── tools/
│   ├── design-system-lint.mjs         # Custom token linter (Gate 0 visual)
│   └── unified_memory.py             # MCP + Beads + GPTRAM bridge
├── src/governance/
│   └── judge.py                       # Judge#6 (Gates 1-5)
├── .beads/
│   └── issues.jsonl                   # Cold store (git-tracked)
├── .mcp-memory/
│   └── store.json                     # Hot store (session-scoped)
├── .gptram/
│   └── verdicts.json                  # Verdict cache
├── .husky/
│   └── pre-commit                     # Gate 0 hook
└── .agent/workflows/
    └── omega-loop.md                  # This file
```
