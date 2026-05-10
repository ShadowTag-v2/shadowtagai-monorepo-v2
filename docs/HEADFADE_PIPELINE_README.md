# HeadFade Generative Asset Pipeline

**Version**: 2.0  
**Date**: May 6, 2026

## Overview

This pipeline enables **Antigravity** to autonomously generate, extract, and integrate high-quality visual assets (images + videos) from Google AI Test Kitchen into the HeadFade platform.

## Pipeline Steps

1. **Image Generation** — ImageFX (Gavel Impact)
2. **Video Generation** — VideoFX (Gavel Descent)
3. **Frame Extraction** — `extract_frames_headfade.sh`
4. **Codebase Update** — Update `FRAME_COUNT` constants
5. **Synchronization** — `omega-sync` workflow

## Quick Start

```bash
# 1. Run the robust Meatware Eviction prompt in Antigravity
# 2. After assets are generated, run:
./scripts/extract_frames_headfade.sh

# 3. The script will:
#    - Extract frames at 30fps
#    - Count total frames
#    - Save frame_count.txt
```

## File Locations

- Generated Image: `apps/headfade/public/frames/gavel_impact.png`
- Generated Video: `external_payloads/headfade/veo_output/gavel_descent.mp4`
- Extracted Frames: `apps/headfade/public/frames/`
- Frame Count: `apps/headfade/public/frames/frame_count.txt`

## Error Handling

The pipeline includes:
- Visual polling loops
- Retry logic (up to 3 attempts)
- Graceful degradation (image-only fallback)
- Detailed logging

## Related Files

- `HEADFADE_PROMPT_SPECS.md`
- `HEADFADE_ROBUST_MEATWARE_EVICTION_PROMPT.md`
- `extract_frames_headfade.sh`

---

**Status**: Production Ready
```