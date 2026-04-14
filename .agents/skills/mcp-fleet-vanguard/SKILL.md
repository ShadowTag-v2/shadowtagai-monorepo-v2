---
name: mcp-fleet-vanguard
description: "Verifies all MCP servers are installed, operational, and used on each tool call. Prevents raw terminal fallbacks. Self-healing loop for crashed servers. Use at session start and before EACH tool call involving Cloud Run, Firebase, Firestore, databases, browser devtools, GitHub, Stitch design, or Gemini API (Veo 3.1 / Nano Banana 2)."
---

# MCP Fleet Vanguard (v9.0)

Enforces strict "Zero-Blind Execution" rules. System tools, cloud deployments, database queries, design operations, and media generation route EXCLUSIVELY through the MCP fleet — never raw bash fallbacks.

## When to Use

- At the start of any conversation or new task
- **Before EACH tool call** involving Cloud Run (GCP), Firebase, Firestore, databases, browser devtools, GitHub, design tokens, screen generation, video generation, or image generation
- Whenever a terminal command fails or an MCP server appears crashed

## Pre-flight Integrity Check

Before proceeding, verify the MCP fleet is installed, ONLINE, and prioritized:

| # | Server | Transport | Purpose | Status |
|---|--------|-----------|---------|--------|
| 1 | `google-developer-knowledge` | Remote (serverUrl) | SDK docs, API references, developer knowledge | verify |
| 2 | `firebase` | Local (npx) | Hosting, Auth, Storage, Cloud Functions, App Hosting | verify |
| 3 | `firestore` | Remote (serverUrl) | Firestore CRUD, collection navigation, database management | verify |
| 4 | `chrome-devtools-mcp` | Local (npx) | Browser inspection, DOM queries, console, network | verify |
| 5 | `github-mcp` | Remote (serverUrl + OAuth) | PRs, issues, releases, repo management | verify |
| 6 | `stitch` | Local (npx) | Design tokens, screen generation, UI structure, brand assets | verify |
| 7 | `gemini` | Local (npx) | Veo 3.1 video generation, Nano Banana 2 image gen, Gemini API | verify |
| 8 | `gcloud-mcp` | Local (binary) | Cloud Run, IAM, Cloud Tasks, GCP services | verify |
| 9 | `mcp-toolbox-sdk-java` | Local (java) | Firestore Toolbox SDK, AlloyDB connectors | verify |

**Canonical config:** `antigravity-mcp-config.json`

## Strict Routing Rules (MANDATORY)

### Firebase & Hosting — Use `firebase` MCP, NOT CLI

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Deploy hosting | `bash: firebase deploy --only hosting` | Firebase MCP: "Deploy my web app to Firebase Hosting" |
| Init project | `bash: firebase init` | Firebase MCP: "Initialize Firebase for this project" |
| List projects | `bash: firebase projects:list` | Firebase MCP: list projects tool |
| Firestore rules | `bash: firebase deploy --only firestore:rules` | Firebase MCP: deploy rules tool |
| Auth config | `bash: firebase auth:export` | Firebase MCP: auth management tools |

### Firestore — Use `firestore` MCP, NOT CLI or raw SDK

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Read documents | `bash: gcloud firestore ...` | Firestore MCP: get/list documents |
| Write documents | Hand-coded `firebase-admin` SDK calls | Firestore MCP: add/update/delete tools |
| Query collections | Shell scripts with `curl` to REST API | Firestore MCP: query tools |
| Schema inspection | Guessing field names | Firestore MCP: navigate collections first |

### Design & Media — Use `stitch` + `gemini` MCP

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Pull design tokens | Hand-code colors/fonts | Stitch MCP: extract design context |
| Generate screens | Manual HTML/CSS from memory | Stitch MCP: generate/fetch screen code |
| Generate video (4K loops) | External download or placeholder | Gemini MCP: Veo 3.1 generate_videos |
| Generate images | Built-in `generate_image` (low quality) | Gemini MCP: Nano Banana 2 (gemini-3.1-flash-image-preview) |
| Edit/iterate designs | Rewrite entire files | Stitch MCP: edit screen, apply tokens |

### Cloud & Infrastructure — Use `gcloud-mcp`, NOT CLI

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Deploy Cloud Run | `bash: gcloud run deploy ...` | GCloud MCP: deploy service |
| Manage IAM | `bash: gcloud iam ...` | GCloud MCP: IAM tools |
| Cloud Tasks | `bash: gcloud tasks ...` | GCloud MCP: tasks tools |
| Project config | `bash: gcloud config set ...` | GCloud MCP: project tools |

### GitHub — Use `github-mcp`, NOT CLI

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Create PR | `bash: gh pr create` | GitHub MCP: create pull request |
| List issues | `bash: gh issue list` | GitHub MCP: list issues |
| Create release | `bash: gh release create` | GitHub MCP: create release |

**Exception: `git push/pull/commit`** — These are local git operations and remain via terminal. Only GitHub API operations (PRs, issues, releases) route through GitHub MCP.

### Developer Knowledge — Use `google-developer-knowledge` MCP

| Action | ❌ FORBIDDEN | ✅ REQUIRED |
|--------|-------------|------------|
| Look up API docs | `search_web` for Google API docs | Developer Knowledge MCP: query documentation |
| Check SDK methods | Guessing from memory | Developer Knowledge MCP: search SDK |
| Verify model specs | Web search for Gemini model info | Developer Knowledge MCP: model information |

## The Self-Healing Loop

If any server is dead, missing, or unresponsive:

1. **HALT** — do NOT report failure or proceed with workaround
2. Identify the failure mode:
   - Remote server (serverUrl): Check network, auth credentials
   - Local server (npx): Check npm package availability, reinstall
   - Local binary (gcloud-mcp): Check PATH, binary existence
3. Repair:
   ```bash
   # Firebase
   npx -y firebase-tools@latest --version
   
   # Stitch
   npx -y stitch-mcp --help
   
   # Gemini (Veo 3.1 + Nano Banana 2)
   npx -y @houtini/gemini-mcp --help
   
   # GCloud
   which gcloud-mcp || echo "Install: gcloud components install gcloud-mcp"
   ```
4. Re-verify against the fleet table above
5. Only then proceed with the original task

## Terminal Commands — When They ARE Allowed

The following operations remain terminal-native (no MCP equivalent):

| Operation | Tool | Reason |
|-----------|------|--------|
| `git add/commit/push/pull` | `run_command` | Local git, not GitHub API |
| `python3 scripts/*.py` | `run_command` | Local script execution |
| `pytest / go test` | `run_command` | Local test runners |
| `ruff / vulture` | `run_command` | Local linting |
| `brew install` | `run_command` | System package management |
| File editing | `write_to_file` / `replace_file_content` | IDE-native tools |

## Design Workflow (Cor.Build)

The correct pipeline for all UI/visual work:

```
Stitch MCP (design tokens + screen structure)
  → Gemini MCP / Veo 3.1 (4K video backgrounds)
  → Gemini MCP / Nano Banana 2 (static image assets)
  → Code generation (React/HTML with pulled tokens)
```

**BANNED:** `dark-luxury-ui-orchestrator` skill — replaced by Stitch MCP + Gemini MCP pipeline.

## Infrastructure Ports

| Service | Port | Status |
|---------|------|--------|
| Temporal Server | 7233+8233 | verify |
| Chrome Debug | 9222 | verify |
| BCI Intent Daemon | ws://127.0.0.1:9090 | verify |
| Firebase Emulator Suite | 9099/8080/5001 | verify |
