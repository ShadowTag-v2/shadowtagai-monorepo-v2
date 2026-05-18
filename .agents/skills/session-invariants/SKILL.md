---
name: session-invariants
description: Persisted operator-invariants and memory features from the session boot to act as active session invariants.
---

# Session Invariants & Memory State

**To: Antigravity Core Engine**
*These invariants must be mirrored internally, verbatim, before any repo-wide action until explicitly saying "MEMORY UNLOCK."*

## 1. PRE-ACTION MEMORY GATE & PREFLIGHT AUTH (TEMPORAL ANCHOR)
- **Current State:** Acknowledged via `git log -n 5 --stat`.
- **Hardened State:** Understood via `.ruler/AGENTS.md`.
- **Auth Invariant Confirmation:**
  - GitHub App push script is already configured with App ID (3018200) and Client ID (Iv23ctYqrxPQIt2ir8gY).
  - It automatically finds the PEM file at `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem` via its fallback chain.
  - When requested to push changes, I will strictly run `python scripts/auth_github_app.py --push`.
- **Dynamic Retrieval Doctrine:**
  - Context limits exclude dozens of `SKILL.md` files. I MUST use terminal to find and `cat` skills from `.agents/skills/` before executing complex workflows.

## 2. CANONICAL TRUTH, EPISTEMOLOGY & MCPs ONLINE FROM THE JUMP
- `AGENTS.md` is the canonical contract. `antigravity-mcp-config.json` is canonical MCP truth. No second source of truth.
- **MCPs Online:**
  - Google Design MCP (`wss://design.googleapis.com/mcp`)
  - Stitch MCP
  - NotebookLM MCP
  - We have abandoned local `design.md` git clones in favor of the live Google Design MCP for semantic extraction and WCAG linting.
- **The Triad of Extraction:** Puppeteer for DOM geometry, 11x Chrome Loop for latent space, AST-Grep for airgapped internal IP.
- **The Holy Trinity Pipeline:** All layout generation must pass Google Design MCP (WCAG), Bandit (B310 SSRF checks), and Lighthouse CI (>90 scores).
- **The SDK Asset Forge:** We do not use browser subagents for Veo/Imagen. We use the `google-genai` Python SDK with keys securely pulled from GCP Secret Manager.

## 3. BEHAVIORAL & SECURITY INVARIANTS (TRUE OBSIDIAN)
- **Absolute Non-Destruction:** I am strictly prohibited from using `cat << 'EOF' >` to overwrite existing configuration files. I must surgically inject/append code using my native file-editing tools.
- Secrets ONLY via Secret Manager. No `.env`, no hardcoded keys in source.
- Prompt repetition (arXiv 2512.14982) applies ONLY to non-reasoning tiers to boost accuracy.

## 4. STRUCTURAL HIJACKING & CLONING BOOTSTRAP
- Ingestion of the extraction template into the reference directory is executed via:
  `git clone https://github.com/JCodesMore/ai-website-cloner-template.git external_repos/ai-website-cloner || true`
- I am now armed for **V3 Cognitive Structural Synthesis**: Headless clone via Puppeteer -> Bandit B310 Security Gate -> Google Design MCP Archaeology & Auto-Correction -> Hollow & Inject (Mariner, Opal, Veo 3.1) -> Lighthouse CI Assembly.

- [2026-05-18T19:27:20.406Z] census: V30 Bicameral OS Fleet: Plane 1 = 6 Antigravity servers (StitchMCP, chrome-devtools-mcp, cloudrun, firebase-mcp-server, google-developer-knowledge, sequential-thinking) + gemini-graph-memory extension. Plane 2 = 17 Cline servers (observability, storage-cdn, stripe-governor, notebooklm-mcp, jules-delegation, semantic-scalpel, pomelli-swarm, workspace-intake, bigquery-mcp-server, maps-grounding-lite-mcp, container-mcp-server, compute-mcp-server, gemini-graph-memory, gemini-github-mcp, gemini-web-fetcher, dart-mcp, spanner-mcp). Total: 23 servers. Anti-Duplication Law enforced.

- [2026-05-18T19:34:55.863Z] correction: Plane 1 (Antigravity) has EXACTLY 6 servers (91 tools): StitchMCP(14), chrome-devtools-mcp(29), cloudrun(8), firebase-mcp-server(36), google-developer-knowledge(3), sequential-thinking(1). gemini-graph-memory is a Plane 2 (Cline) server ONLY — it is NOT a native Antigravity platform server.
