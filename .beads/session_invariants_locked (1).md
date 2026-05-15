# Session Invariants — LOCKED (until MEMORY UNLOCK)

**Created**: 2026-04-21T04:59:00Z
**Status**: ACTIVE — mirror before any repo-wide action

## Operator Invariants (verbatim from GEMINI.md v9.6 + AGENTS.md v9.7)

### Canonical Truth Hierarchy
- `AGENTS.md` is the canonical contract.
- `CLAUDE.md` is a thin shim.
- `monorepo_manifest.yaml` is workspace truth.
- `antigravity-mcp-config.json` is MCP truth.
- `BUSINESS_CONTEXT_LOCKED.md` is pricing and architecture truth.
- `RISK_REGISTER.md` is operational risk truth.

### Mandatory MCP Server Usage
ALL 5 MCP servers MUST be used. If an operation CAN be performed by an MCP server, it MUST be. No terminal fallbacks for MCP-capable operations.

| Server | Required For |
|--------|-------------|
| **Firebase MCP** | All Firebase deployment, hosting, Firestore, auth, functions operations |
| **Chrome DevTools MCP** | Screenshots, page interaction, performance traces, lighthouse audits |
| **StitchMCP** | Design systems, screen generation, UI prototyping |
| **Google Developer Knowledge** | Google API documentation lookup (NEVER use search_web for Google docs) |
| **Sequential Thinking** | Multi-step architectural decisions, complex reasoning |

### Anti-Patterns (PROHIBITED)
- Defining routing tables in prose doctrine (GEMINI.md, AGENTS.md, skills)
- Using `search_web` for Google API documentation (use `google-developer-knowledge` MCP)
- Running `firebase deploy` in terminal (use `firebase-mcp-server` MCP)
- Taking screenshots with external tools (use `chrome-devtools-mcp` MCP)
- Hand-coding design tokens from memory (use `StitchMCP`)
- Ad-hoc reasoning lists for architecture (use `sequential-thinking` MCP)

### Execution State Machine
- **STATE A — Pure YOLO**: Repetitive UI work, standard logic, known patterns, low-ambiguity changes
- **STATE B — Clutch**: Git history rewrites, force-pushes, database migrations, auth/payment changes, architecture shifts >3 packages

### Physical Barriers
- FORBIDDEN: Writing SQL/database logic without querying live schema via MCP
- FORBIDDEN: Guessing API endpoints without Documentation MCP fetch
- FORBIDDEN: Kling 3.0 or any non-Google video pipeline (Veo 3.1 ONLY)
- FORBIDDEN: Destructive tools (`rm -rf`, `sudo`)

### Video Pipeline (Google-Native Only)
- **Image**: Nano Banana 2/Pro via Google Flow
- **Video**: Veo 3.1 / Veo 3.1-Fast / Veo 3.1-Lite via Vertex AI
- **Remix**: Google Whisk (subject + scene + style)
- **Frames**: ffmpeg (local extraction for scroll-driven websites)

### External Cognitive Suite Budget
- **25,000 free credits/tokens** across: Mariner, Flow, Whisk, Opal, Labs FX
- **Maximize**: Flow (NB2/Pro image gen) + Whisk (remix) + NotebookLM (research/podcasts)

### NotebookLM MCP Integration
- Tool: `notebooklm-mcp-cli` (v0.5.26, 3.8K stars, 35 MCP tools)
- Install: `uv tool install notebooklm-mcp-cli`
- CLI: `nlm` (notebook management, source add, audio/video gen, research)
- Auth: Cookie-based browser extraction (`nlm login`)
- Constraint: 50 queries/day free tier, cookie refresh every few weeks

### GitHub Doctrine
- SSH PRIMARY: `git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`
- App PEM: `$SHADOWTAG_PEM` (5-tier fallback chain)
- NEVER: `gh auth login`, PATs, deploy keys

### Nag Protocol
- End every response with EXACTLY 22 actionable prompts until thread resolved
