# Nano Banana 2/Pro — Workflow Intelligence

**Captured**: 2026-04-20
**Updated**: 2026-04-21 (Kling purged → Veo 3.1 Google-native pipeline)
**Sources**:
- YouTube: `e6iVEZ6ws5Q` (Nano Banana 2 + Veo 3.1 + Antigravity)
- YouTube: `XCGbDx7aSks` (Agent Factory Podcast — Remik + Antigravity)
- Repo: `github.com/GoogleCloudPlatform/devrel-demos` (ai-ml directory)

## Model Identity

| Codename | Real Name | Access |
|----------|-----------|--------|
| **Nano Banana 2** | Gemini 3 Image Generation (standard) | Google Flow (`labs.google/fx/tools/flow`) |
| **Nano Banana Pro** | Gemini 3 Pro Image Generation | Google Flow (model selector) |

## Workflow 1: Cinematic Scroll-Stopping Website (100% Google-Native)

```
Nano Banana 2 (Image) → Veo 3.1 (Video, 8s 4K, native audio) → ffmpeg (Frames) → Antigravity (Website)
```

### Step-by-step:
1. **Google Flow** → New project → Image mode → 16:9 → 4 outputs → Nano Banana 2
2. **Prompt formula**: Camera angle + subject detail + lighting + environment + camera model
3. **Edit in Flow**: Select regions to inpaint (e.g., change car color)
4. **Download**: Watermark-free from Flow (unlike Gemini app)
5. **Veo 3.1** (via Vertex AI API or Google Labs FX): Upload as start frame (i2v) → describe motion → 8s → 4K → native audio
6. **Prompt constraints**: "No sharp cuts, no visible driver, smooth actions, continuous video"
7. **ffmpeg**: Extract frames → `public/frames/frame_%04d.png`
8. **Antigravity**: agent.md (design system + sections + animations + rules) → Planning Mode → Gemini 3.1 Pro
9. **Scroll effect**: Frames change on scroll (NOT video playback — video = choppy)
10. **3D models**: Free .glb from web → integrate with Three.js for feature section rotation

### Veo 3.1 Model Tiers
| Model | Quality | Speed | Use Case |
|-------|---------|-------|----------|
| **Veo 3.1** | 4K, native audio | Standard | Hero cinematic, showcase |
| **Veo 3.1-Fast** | 4K, native audio | 2x faster | Iteration, prototyping |
| **Veo 3.1-Lite** | 1080p | Fastest | Quick previews, drafts |
| **Veo 3.0** | 4K | Standard | Fallback |
| **Veo 2.0** | 1080p | Legacy | Budget-conscious |

## Workflow 2: Agent Starter Pack → Slides Agent

```
uvx agent-starter-pack → Antigravity modifies → MCP Media Server → Nano Banana Pro generates slides
```

### Step-by-step:
1. `uvx agent-starter-pack` (ADK base template, Cloud Run, Vertex AI sessions, Cloud Build)
2. Open in Antigravity workspace → Planning Mode → Gemini 3.1 Pro
3. Prompt: "Build slides agent using MCP server at [URL]"
4. Antigravity: reads Gemini.md + starter pack code → creates implementation plan
5. Comment on plan (skip automated tests, use browser plugin for testing)
6. Agent modifies: agent.py (MCP tool registration, agent instructions, rename)
7. `make playground` → ADK web UI → browser extension tests the agent
8. Media MCP server on Cloud Run: wraps Nano Banana Pro + saves to GCS

## Key Patterns

### agent.md Pattern
- Project description + design system (colors, typography, elements)
- Page sections (nav, hero, story, features, reviews, footer)
- Global animations + file structure + hard rules
- Referenced in prompt via `@agent.md`

### Planning Mode Best Practice
- Quality > Speed for complex projects
- Creates implementation plan + task list with checkboxes
- Comment system like Google Docs collaboration
- Agent adjusts plan before executing

### MCP Separation of Concerns
- Media MCP server owns image generation + GCS storage
- Agent only calls MCP tools (doesn't handle Nano Banana directly)
- Enables team ownership: DB team owns DB MCP, media team owns media MCP
- Connection pooling for database MCP servers

## Google External Cognitive Suite Budget
- **25,000 free credits/tokens** across: Mariner, Flow, Whisk, Opal, Labs FX
- Priority: maximize Flow (Nano Banana 2/Pro) + Whisk (remix inputs for Veo)
- Veo 3.1 via Vertex AI is separate billing (GCP project credits)
