# Universal Google Generative Pipeline — HeadFade + KovelAI

**Version**: 3.0 (Professional + Maximized Google Integration)  
**Date**: May 6, 2026

## Architecture Overview

This pipeline maximizes the use of Google’s generative ecosystem by coordinating:

- **Jules** — Autonomous code generation & orchestration
- **Stitch MCP** — Multi-agent orchestration fabric
- **Nano Banana 2** (via Whisk / Flow) — Advanced image generation
- **ImageFX / VideoFX** — Core generative tools at AI Test Kitchen
- **Pomelli Onboarding** — https://labs.google.com/u/0/pomelli/onboarding
- **chrome-devtools-mcp** — Native browser automation (Meatware Bridge Eviction)

## Full Pipeline Flow

1. **Jules** receives high-level task via MCP
2. **Stitch** coordinates between Jules, Browser Subagent, and terminal
3. **Browser Subagent** navigates Google Labs tools autonomously
4. **Nano Banana 2 / Whisk / Flow** generates premium assets
5. **Universal Extract Script** processes video into frames
6. **Codebase Update** + `omega-sync` commit

## How to Trigger (Professional Way)

### Option A: Via Jules (Recommended)

Use this master prompt in Jules:

```
Coordinate the full generative asset pipeline for both HeadFade and KovelAI using the Universal Google Pipeline v3.0.

Use:
- Stitch MCP for orchestration
- Nano Banana 2 via Whisk/Flow for premium generation
- https://labs.google.com/u/0/pomelli/onboarding for advanced access
- Universal extract script for frame processing

Execute the robust Meatware Bridge Eviction prompt for both projects, then run:
./scripts/extract_frames_universal.sh headfade ...
./scripts/extract_frames_universal.sh kovelai ...

End with full confirmation of asset integration.
```

### Option B: Direct Script Execution

```bash
# HeadFade
./scripts/extract_frames_universal.sh headfade external_payloads/headfade/veo_output/gavel_descent.mp4 apps/headfade/public/frames 30

# KovelAI
./scripts/extract_frames_universal.sh kovelai labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4 apps/kovelai/public/frames 30
```

## Professional Best Practices

- Always use **16:9 aspect ratio**
- Enable **high detail** mode in all Google tools
- Use **visual polling loops** (never assume timing)
- Log everything to `pipeline_logs/`
- Commit via `omega-sync` after every successful run

## File Structure

```
scripts/
├── extract_frames_universal.sh
├── HEADFADE_ROBUST_MEATWARE_EVICTION_PROMPT.md
├── ROBUST_MEATWARE_EVICTION_PROMPT.md
external_payloads/
├── HEADFADE_PROMPT_SPECS.md
├── PROMPT_SPECS.md
docs/
└── UNIVERSAL_GOOGLE_PIPELINE_README.md
```

---

**Status**: Production-Grade | Maximized Google Integration | Fully Autonomous
```