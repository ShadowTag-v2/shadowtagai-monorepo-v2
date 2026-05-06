# Nano Banana Model Registry

**Canonical Location**: `.beads/nano_banana_registry.md`
**Last Updated**: 2026-04-21

> [!IMPORTANT]
> This file replaces any GEMINI.md model registry claims. GEMINI.md is an immutable zone — model data lives here.

## Image Generation Models

| Codename | Real Name | Access | Resolution | Outputs | Watermark |
|----------|-----------|--------|------------|---------|-----------|
| **Nano Banana 2** | Gemini 3 Image Generation | Google Flow | Up to 4K | 4 per prompt | None (Flow) |
| **Nano Banana Pro** | Gemini 3 Pro Image Generation | Google Flow | Up to 4K | 4 per prompt | None (Flow) |

### NB2 vs NB Pro Differences
| Feature | NB2 | NB Pro |
|---------|-----|--------|
| Reasoning | Basic | Advanced chain-of-thought |
| Search grounding | No | Yes (Google Search for reference) |
| Text rendering | Poor | High quality |
| Resolution cap | 4K | 4K |
| Speed | Fast | Slower (reasoning step) |
| Best for | Backgrounds, scenes, abstract | Text-heavy, accurate details |

## Video Generation Models (Google-Native Only)

| Model | Quality | Duration | Audio | Speed | Access |
|-------|---------|----------|-------|-------|--------|
| **Veo 3.1** | 4K | 8s | Native gen | Standard | Vertex AI / Labs FX |
| **Veo 3.1-Fast** | 4K | 8s | Native gen | 2x faster | Vertex AI |
| **Veo 3.1-Lite** | 1080p | 8s | Native gen | Fastest | Vertex AI |
| **Veo 3.0** | 4K | 8s | No | Standard | Vertex AI |
| **Veo 2.0** | 1080p | 8s | No | Legacy | Vertex AI |

> [!CAUTION]
> Kling 3.0 is **BANNED** from this architecture. All video generation goes through Veo (Google-native). Zero third-party video pipelines.

## External Cognitive Suite Budget

**25,000 free credits/tokens** across all tools:

| Tool | Access | Credit Category |
|------|--------|----------------|
| Google Flow | `labs.google/fx/tools/flow` | Image generation |
| Google Whisk | `labs.google/fx/tools/whisk` | Remix/style transfer |
| Google Mariner | Browser AI agent | Research |
| Google Opal | `labs.google` | Experimental |
| Google Labs FX | `labs.google/fx` | Multimodal sandbox |
| NotebookLM | `notebooklm.google.com` | Research/podcasts |

### Pipeline Flow
```
Flow (NB2/Pro) → [image]
  ├── Direct website use (hero, OG, assets)
  ├── Whisk (remix: subject + scene + style)
  └── Veo 3.1 (i2v: start frame → 8s 4K video)
        └── ffmpeg (frame extraction for scroll websites)
```

## Vertex AI SDK Reference
- Package: `google-genai` (≥1.66.0)
- GCS bucket: `gs://shadowtag-omega-v4-media`
- Frame extraction: `ffmpeg 8.1` (Homebrew)
