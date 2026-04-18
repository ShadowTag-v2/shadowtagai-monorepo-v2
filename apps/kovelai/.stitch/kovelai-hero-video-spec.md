# KovelAI Hero Video Specification
> Version 1.0 | Generated: 2026-04-16 | Status: PRODUCTION

## Asset Location
| Env | Path |
|-----|------|
| GCS (CDN) | `gs://shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4` |
| Public URL | `https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4` |
| Local | `apps/kovelai/public/hero-videos/legal-data-arch.mp4` (gitignored) |
| Poster | `apps/kovelai/public/images/hero-poster.jpg` |
| Fallback | `.webm` variant at same GCS path |

## Generation Spec
| Property | Value |
|----------|-------|
| Model | `veo-3.1-generate-preview` |
| SDK | `google-genai` ≥ 1.66.0 |
| Python | 3.13 via `uv` |
| Duration | 8 seconds |
| Loop | Seamless (first frame = last frame) |
| Resolution | 4K cinematic |
| Script | `scripts/gen_kovelai_hero_video.py` |

## Visual Identity
| Token | Value |
|-------|-------|
| Background | Deep navy `#0a0f1e` |
| Mid-layer | Slate grey `#1e2a3a` |
| Lines | Glowing gold `#c9a96e` |
| Highlights | Warm white `#f5ede0` at 67% opacity |
| Camera | Imperceptibly slow forward push |
| Depth | 3D parallax — foreground lattice faster than background |
| Mood | Prestigious · Stable · Secure · Sovereign |

## Canonical Prompt
```
Abstract digital neural network infrastructure visualization. Thousands of fine,
luminous golden-white lines intersect and pulse across a deep navy-black void,
forming geometric lattice patterns that suggest data flow and legal precision.
Glowing amber and pale gold nodes pulse softly where lines converge, like synapses
firing through a secure private network. The structure is crystalline and ordered,
not chaotic — every line connects with purpose, evoking encrypted judicial records,
secure attorney-client privilege, and institutional trust.

Camera: imperceptibly slow forward push, as if moving through infinite corridors
of encrypted legal data. The foreground lattice moves slightly faster than the
background, creating subtle 3D depth parallax. The overall palette is deep navy
(#0a0f1e), slate grey (#1e2a3a), with fine glowing gold (#c9a96e) and warm white
(#f5ede0aa) line highlights.

Mood: prestigious, stable, secure, sovereign. Like the interior of a digital vault
inside a white-shoe law firm. No chaos, no consumer aesthetics — only precision
engineering for the legal profession.

The animation loops seamlessly: the final frame visually matches the first frame.
Duration: 8 seconds. 4K resolution. Cinematic, photorealistic render quality.
```

## Regeneration Instructions
```bash
# From monorepo root
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
set -a && source .env && set +a
~/.local/bin/uv run --python 3.13 python scripts/gen_kovelai_hero_video.py
# Then deploy:
bash scripts/deploy_kovelai_hero_video.sh
```

## Schedule
- Regenerate quarterly or when Veo model upgrades to 4.0+
- Always generate `.webm` variant after `.mp4` generation (use `ffmpeg -i *.mp4 -c:v libvpx-vp9 *.webm`)
- Upload both formats to GCS before redeploying

## Integration in HTML
```html
<video class="hero-video-bg" id="heroVideo"
       autoplay loop muted playsinline
       preload="none"
       poster="/images/hero-poster.jpg"
       onloadeddata="this.classList.add('loaded')">
  <source src="https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4" type="video/mp4">
  <source src="https://storage.googleapis.com/shadowtag-omega-v4-archive/hero-videos/legal-data-arch.webm" type="video/webm">
</video>
```

## Performance Characteristics
- GCS CDN → sub-50ms TTFB (global)
- `preload="none"` → zero impact on LCP
- Scroll-triggered `preload="auto"` swap at hero entry
- `content-visibility: auto` on non-hero sections
- `Cache-Control: public, max-age=31536000` (1 year immutable)
