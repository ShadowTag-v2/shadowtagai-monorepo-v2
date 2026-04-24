---
name: "TACSOP 0 — Building Websites (Unified SOP)"
description: >
  Master operational procedure that chains all website-building skills into
  a single execution flow. This is the meta-skill that orchestrates:
  Stitch design → Cognitive Structural Synthesis → AG-UI frontend protocol →
  Firestore pipeline → Firebase deployment → Security audit → Lighthouse.
  Use when: "build a website", "create landing page", "redesign site",
  "full website pipeline", or any task requiring end-to-end website delivery.
version: "1.0.0"
---

# TACSOP 0 — Building Websites (Unified SOP)

**Source:** Cor.Antigravity TACSOP 0 (2026-04-24)
**Scope:** All ShadowTag/KovelAI web properties
**Prerequisite Skills:** All 24 component skills listed in the Dependency Map below

---

## Dependency Map

```
TACSOP 0 (this skill — orchestrator)
├── Phase 0: Research & Planning
│   ├── hybrid-osint-router          (research routing)
│   ├── sequential-attention-selector (codebase analysis)
│   ├── spec-driven-vibe-coding      (requirements → design → tasks)
│   └── 11x_browser_extractor.py     (Google AI Mode extraction)
│
├── Phase 1: Design
│   ├── stitch-first-websites        (mandatory Stitch-first protocol)
│   ├── stitch-design                (design system + screen generation)
│   ├── stitch-design-md             (DESIGN.md synthesis)
│   ├── stitch-design-spec           (design specification)
│   ├── cognitive-structural-synthesis (design archaeology)
│   └── website-cloner               (reference extraction)
│
├── Phase 2: Architecture
│   ├── agentic-website-construction (6-skill architecture doctrine)
│   ├── a2a-agent-card-publisher     (agent discovery)
│   ├── a2ui-generative-blueprint    (declarative UI JSON)
│   ├── ag-ui-frontend-protocol      (CopilotKit AG-UI)
│   ├── agui-sse-transport           (SSE adapter)
│   └── cloud-api-registry-mcp-binder (dynamic tool discovery)
│
├── Phase 3: Implementation
│   ├── cor-build-websites           (Stitch → Veo → Code → Deploy)
│   ├── dynamic-tool-acquisition     (npx skills on demand)
│   ├── firestore-pipeline-architect (server-side aggregations)
│   └── epistemic-memory-kernel      (typed knowledge atoms)
│
├── Phase 4: Security & Quality
│   ├── omni-security-engine         (Gitleaks/Bandit gate)
│   ├── headless-cli-protocol        (PTY trap prevention)
│   └── prompt-repetition-boost      (accuracy for non-reasoning models)
│
├── Phase 5: Deployment
│   ├── developer-connect-cicd       (Cloud Build triggers)
│   ├── agent-config-ruler           (Ruler single source of truth)
│   └── firebase-mcp-deploy-doctrine (Firebase Hosting deploy)
│
└── ADRs (Architecture Decision Records)
    ├── ADR-003: CopilotKit AG-UI Frontend
    ├── ADR-004: SSE Over WebSocket
    └── ADR-005: Backend Encryption Default
```

---

## Execution Protocol

### Phase 0: Research & Planning (15-30 min)

1. **Classify intent** using `hybrid-osint-router`:
   - Internal IP → `rg`/`sg` against repo
   - Public IP → `google-developer-knowledge` MCP
   - Hybrid → internal first, then public

2. **Run Sequential Attention** on existing codebase:
   - `sequential-attention-selector` profiles the codebase
   - Identifies reusable components, dead code, patterns

3. **Create spec** using `spec-driven-vibe-coding`:
   - `requirements.md` → WHAT (EARS syntax)
   - `design.md` → HOW (architecture)
   - `tasks.md` → STEPS (checklist)

4. **Optional: Extract reference** using `11x_browser_extractor.py`:
   ```bash
   python3 scripts/11x_browser_extractor.py "modern SaaS landing page design 2026"
   ```

### Phase 1: Design (30-60 min)

5. **MANDATORY: Stitch First** — `stitch-first-websites` enforces:
   - Check/create design system via `list_design_systems` / `create_design_system`
   - Generate screens via `generate_screen_from_text`
   - Iterate variants via `generate_variants`
   - Export approved design

6. **Synthesize DESIGN.md** using `stitch-design-md`:
   - Extract tokens from Stitch project
   - Create semantic design specification
   - Document color roles, typography scale, component specs

7. **Optional: Design archaeology** using `cognitive-structural-synthesis`:
   - Clone reference site structure
   - Extract layout patterns and design tokens
   - Synthesize into your design system

### Phase 2: Architecture (15-30 min)

8. **Select architecture level** using `agentic-website-construction`:
   - Level 1: Static site (HTML/CSS/JS)
   - Level 2: Dynamic site (Next.js/Vite + API)
   - Level 3: Agentic site (AG-UI + CopilotKit)
   - Level 4: Multi-agent site (A2A protocol)
   - Level 5: Autonomous site (self-evolving)

9. **If Level 3+**: Configure AG-UI:
   - Install CopilotKit runtime
   - Configure SSE transport (ADR-004)
   - Set up AG-UI event handlers
   - Publish Agent Card (A2A)

### Phase 3: Implementation (1-4 hours)

10. **Execute** using `cor-build-websites`:
    - Pull design tokens from Stitch
    - Generate video backgrounds (Veo 3.1) if needed
    - Generate static assets (Nano Banana 2) if needed
    - Write code with Stitch tokens applied
    - Wire Firestore pipelines if needed

11. **Dynamic tools**: If missing capability, use `dynamic-tool-acquisition`:
    ```bash
    npx -y @anthropic/create-mcp-server@latest  # MCP server scaffolding
    npx -y shadcn@latest add button card        # UI components
    ```

### Phase 4: Security & Quality (15-30 min)

12. **Run security gate** using `omni-security-engine`:
    - Betterleaks scan (secrets)
    - Bandit scan (Python vulnerabilities)
    - `ruff check --select F401,F841 --fix` (dead code)

13. **Apply prompt repetition** (ADR: arXiv 2512.14982):
    - Only for non-reasoning model tiers
    - Repeat user instruction in context window

14. **Verify encryption** per ADR-005:
    - All Firestore writes encrypted
    - Session state encrypted
    - No raw privileged content in SSE stream

### Phase 5: Deployment (15-30 min)

15. **Deploy** using `firebase-mcp-deploy-doctrine`:
    - Verify MCP auth (`firebase_login`)
    - Verify CLI auth (`firebase login:list`)
    - Read hosting guide resource
    - Initialize with `firebase_init`
    - Build production bundle
    - Deploy with `firebase deploy --only hosting`

16. **Verify** using Chrome DevTools MCP:
    - `lighthouse_audit` on live URL
    - Check accessibility score ≥ 90
    - Check SEO score ≥ 90
    - Check best practices ≥ 90

17. **Update Ruler** using `agent-config-ruler`:
    - Sync any new configs to all agent instruction files
    - Run `ruler apply` to distribute

---

## Anti-Patterns (PROHIBITED)

- Writing HTML/CSS without Stitch prototype first
- Using WebSocket instead of SSE for agent streaming
- Deploying without Lighthouse audit
- Skipping security gate before push
- Guessing design tokens from memory (use Stitch MCP)
- Running `firebase deploy` without verifying both auth layers
- Using `npx firebase-tools` (ephemeral token loss)

---

## Quality Gates

| Gate | Tool | Threshold |
|------|------|-----------|
| Lighthouse Accessibility | `chrome-devtools-mcp` | ≥ 90 |
| Lighthouse SEO | `chrome-devtools-mcp` | ≥ 90 |
| Lighthouse Best Practices | `chrome-devtools-mcp` | ≥ 90 |
| Secret Scan | Betterleaks | 0 BLOCK findings |
| Dead Code | ruff F401/F841 | 0 violations |
| Design System | Stitch MCP | All tokens applied |

---

## Tri-Partite Cognitive Architecture Integration

This SOP engages all three layers per TACSOP 4 Kairos (Core Truth #12):

1. **Brainstem** (5 MCP Servers — <100ms):
   - Firebase MCP → deploy
   - Chrome DevTools MCP → audit
   - Stitch MCP → design
   - Developer Knowledge MCP → docs
   - Sequential Thinking MCP → reasoning

2. **Hippocampus** (NotebookLM + Obsidian — persistent memory):
   - `notebooklm-orchestrator` for document analysis
   - `obsidian-formatter` for research output
   - `epistemic-memory-kernel` for typed knowledge atoms

3. **Motor Cortex** (Kairos Zero-Day Matrix + npx skills):
   - `dynamic-tool-acquisition` for on-demand capabilities
   - `kairos-zero-day-matrix` for skill fleet management
