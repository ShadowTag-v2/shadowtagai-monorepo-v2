# Media MCP Server — Nano Banana Pro + Veo 3.1

MCP server providing image and video generation tools via Google-native APIs.

## Architecture

```
Agent (ADK) → MCP Tool Call → MediaGenerators Server → Google GenAI API → GCS
```

## Tools

| Tool | Model | Capability |
|------|-------|-----------|
| `generate_image` | Gemini 3 Pro Image (Nano Banana Pro) | 4K image gen, i2i editing |
| `generate_video` | Veo 3.1 / 3.1-Fast / 3.1-Lite | 8s 4K video, native audio, i2v |

## Quick Start

```bash
# Install
pip install -e .

# Set up auth (ADC)
gcloud auth application-default login

# Run locally
python media_mcp_server.py

# Run the slides agent (in another terminal)
export MEDIA_MCP_URL=http://localhost:8080/mcp
python -m google.adk.cli web
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GCS_MEDIA_BUCKET` | `shadowtag-omega-v4-media` | GCS bucket for uploads |
| `PORT` | `8080` | Server port |
| `HOST` | `0.0.0.0` | Server host |
| `MEDIA_MCP_URL` | `http://localhost:8080/mcp` | MCP server URL (for agent) |

## Reference

Based on `devrel-demos/ai-ml/agent-factory-antigravity-nano-banana-pro/`
from [GoogleCloudPlatform/devrel-demos](https://github.com/GoogleCloudPlatform/devrel-demos).

## Video Pipeline (Google-Native Only)

> ⚠️ Kling 3.0 is BANNED. All video generation uses Veo 3.1 (Vertex AI).

```
Nano Banana 2 (image) → Veo 3.1 (i2v, 8s 4K) → ffmpeg (frames) → scroll-engine.js
```
