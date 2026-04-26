---
name: kairos-zero-day-matrix
description: >
  Codifies the TACSOP 4 Kairos directive — the Tri-Partite Cognitive Architecture,
  session bootstrap checklist, and dynamic capability acquisition doctrine.
  This is the master cognitive routing reference for Antigravity agent awareness.
  Activates on session start as the cognitive bootstrap skill.
---

# Kairos Zero-Day Matrix — TACSOP 4

**Source:** Cor.Antigravity TACSOP 4 (Kairos), codified 2026-04-24
**Disposition:** 28 concepts verified active, 5 deferred (human-blocked)

---

## Tri-Partite Cognitive Architecture

The agent operates across three cognitive layers. All three must be engaged on every session:

### Layer 1: Brainstem (MCP Servers — Muscle Memory)
**Speed:** <100ms. **Trust:** Highest. **Always on.**

The 5 mandatory MCP servers form the agent's reflexive nervous system:

| Server | Function |
|--------|----------|
| `firebase-mcp-server` | Auth, Firestore, Hosting, Cloud Functions, Storage |
| `chrome-devtools-mcp` | Browser automation, screenshots, Lighthouse, performance |
| `StitchMCP` | Design system generation, screen creation, UI iteration |
| `google-developer-knowledge` | Google API docs, official guides, release notes |
| `sequential-thinking` | Structured reasoning, hypothesis verification |

**Rule:** If an MCP server CAN handle a task, it MUST. No terminal fallbacks for MCP-capable operations.

### Layer 2: Hippocampus (NotebookLM + Obsidian — Persistent Memory)
**Speed:** Seconds. **Trust:** High (curated). **Session-bridging.**

| Component | Purpose |
|-----------|---------|
| NotebookLM Orchestrator | Zero-token document analysis via CLI |
| Expert Agent Builder | DBS framework generation with Rule of Three (3x repetition) |
| Session Wrap-Up | Persistent memory injection into Master Brain notebook |
| Obsidian Formatter | WikiLink graph syntax for visual knowledge connections |
| NotebookLM Oracle | Mandatory architectural context retrieval before complex work |
| Obsidian Vault | `~/Antigravity-Vault/` with Zettelkasten, Auto-Dream, Logs |

**arXiv:2512.14982 Integration:** All NotebookLM queries use prompt repetition (2x for standard, 3x for deep retrieval) because NotebookLM uses non-reasoning inference.

### Layer 3: Motor Cortex (Dynamic Acquisition — Adaptive Skills)
**Speed:** Slower (download). **Trust:** Medium (community). **Gap-filling.**

The 3-Tier Capability Cascade:
```
Tier 1 (Muscle): MCP JSON tools — tried FIRST
  ↓ not available
Tier 2 (Brain): .agents/skills/ + ~/.gemini/antigravity/skills/ — check for procedural guidance
  ↓ no matching skill
Tier 3 (Discovery): npx skills CLI discovery → execute
```

**Skills:** `dynamic-tool-acquisition/SKILL.md`, `hybrid-capability-cascade/SKILL.md`

---

## Session Bootstrap Checklist

Run this mentally on every new session:

1. ☐ **Layer 1 verified:** All 5 MCP servers responding (use `firebase_get_environment`, snapshot, etc.)
2. ☐ **Layer 2 available:** NotebookLM CLI installed, Obsidian Vault at `~/Antigravity-Vault/`
3. ☐ **Layer 3 ready:** `npx -y skills` accessible
4. ☐ **Doctrine loaded:** GEMINI.md, AGENTS.md, monorepo_manifest.yaml all parsed
5. ☐ **KI summaries reviewed:** Check for relevant Knowledge Items before any research
6. ☐ **Execution state:** Default to STATE A (YOLO). Clutch to STATE B only for triggers defined in `execution_state_machine`

---

## TACSOP 4-Specific Patterns (Beyond TACSOP 2)

These patterns are unique to the Kairos directive and supplement the 6 patterns in `tacsop-operational-patterns/SKILL.md`:

### Pattern 7: Cognitive Layer Escalation
**When:** A task spans multiple cognitive layers.
**Rule:** Start at Layer 1 (Brainstem/MCP). If insufficient, escalate to Layer 2 (Hippocampus/NotebookLM). Only fall through to Layer 3 (Motor Cortex/npx) when Layers 1-2 cannot handle the request.

### Pattern 8: Zero-Day Bootstrap
**When:** Starting a fresh session or resuming after context loss.
**Rule:** Execute the Session Bootstrap Checklist above before any work. This prevents blind execution without cognitive infrastructure.

### Pattern 9: Persistent Memory Injection
**When:** Ending any significant work session.
**Rule:** Trigger `session-wrap-up` skill to persist architecture decisions and unresolved bugs into the Master Brain notebook. The agent's memory MUST survive context death.

---

## Daemon Fleet Integration

| Daemon | Script | Relationship |
|--------|--------|--------------|
| KAIROS | `scripts/kairos_daemon.py` | Background autonomous agent mode |
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly KI maintenance |
| Loop Steward | `scripts/loop_steward.py` | Autonomous task continuation |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Recursive self-improvement |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM lint+push |

---

## Human-Blocked Items (Deferred)

These require user intervention and cannot be automated by the agent:

| Item | Action Required |
|------|----------------|
| NotebookLM auth | Run `notebooklm login` in Mac Terminal |
| KAIROS daemon schedule | Configure launchd plist or cron |
| Master Brain notebook ID | Create notebook in NotebookLM, provide ID |
| pnkln-evolve activation | Manual start (R&D only) |
| Dream consolidation schedule | Configure launchd plist |

---

## Cross-References

- TACSOP 2 Patterns: `.agents/skills/tacsop-operational-patterns/SKILL.md`
- Capability Cascade: `.agents/skills/hybrid-capability-cascade/SKILL.md`
- Dynamic Acquisition: `.agents/skills/dynamic-tool-acquisition/SKILL.md`
- Epistemic Airgap: `.agents/skills/epistemic-airgap/SKILL.md`
- Obsidian Formatter: `.agents/skills/obsidian-formatter/SKILL.md`
- NotebookLM Orchestrator: `.agents/skills/notebooklm-orchestrator/SKILL.md`
- Expert Agent Builder: `.agents/skills/expert-agent-builder/SKILL.md`
- Session Wrap-Up: `.agents/skills/session-wrap-up/SKILL.md`
- NotebookLM Oracle: `.agents/skills/notebooklm-oracle/SKILL.md`
- Setup Workspace: `.agents/skills/setup-workspace/SKILL.md`
- Deep Think Consultation: `.agents/skills/deep-think-consultation/SKILL.md`
- Context Budget Discipline: `.agents/skills/context-budget-discipline/SKILL.md`
- Post-Edit Validation: `.agents/skills/post-edit-validation-loop/SKILL.md`
- Meatbridge Eviction: `.agents/skills/cor-meatbridge-eviction/SKILL.md`
- Visual Provenance: `.agents/skills/ban-native-image-gen/SKILL.md`
