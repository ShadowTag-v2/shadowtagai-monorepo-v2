# CounselConduit — Veo 3.1 & Nano Banana 2 Prompt Specifications

> Per `cor-build-websites` Phase 2 & Phase 3 + `veo3-flow-cinematic` prompt engineering guide.
> All assets are for the CounselConduit landing page hero section.

---

## 1. Hero Reference Frame — Nano Banana 2

**Platform:** Google Flow → Image mode → Nano Banana 2
**Aspect Ratio:** 16:9
**Outputs:** 4 (zero extra cost, same generation time)
**Download:** Watermark-free from Flow (Ultra tier)

### Prompt

```
Extreme macro lens photograph of a single obsidian gavel striking a translucent
glass routing table. The moment of impact frozen in time. Cryptographic blue
shockwaves ripple outward from the contact point across the glass surface,
revealing embedded circuit board traces beneath. Deep navy (#0A1628) background
with subtle gold (#C9A84C) light refracting through the glass edges. Volumetric
fog. Shot on ARRI Alexa with 100mm macro lens, extremely shallow depth of field.
Cinematic lighting, rim light on the gavel head, high-key highlights on
shockwave crests. Premium, prestigious, stable. No text.
```

### Prompt (Alternative — Abstract)

```
Abstract architectural visualization of parallel golden data streams flowing
through a deep navy void. The streams converge at a central crystalline node
that pulses with subtle blue-white energy. Minimal, clean, prestigious.
Shallow depth of field with volumetric fog. Shot on RED V-Raptor 8K,
50mm prime lens. No chaotic movement. No text. Navy (#0A1628), gold (#C9A84C),
slate (#2D3748).
```

---

## 2. Hero Video — Veo 3.1

**Platform:** Vertex AI SDK or Google Flow Scenebuilder
**Model:** `veo-3.1-generate-001`
**Resolution:** 4K
**Aspect Ratio:** 16:9
**Duration:** 8 seconds
**Loop:** Seamless (last-frame technique)

### Prompt (Gavel Descent)

```
Slow cinematic macro-lens descent toward an obsidian gavel head. The gavel
strikes a translucent glass surface, sending cryptographic blue shockwaves
rippling outward in concentric rings. Circuit board traces illuminate beneath
the glass as each wave passes. Gold light refracts through glass edges.
Deep navy background with volumetric fog. Extremely slow motion. Smooth,
continuous shot — no sharp cuts, no transitions, no text overlays.
8-second seamless loop. Stable, prestigious, precise.
With ambient low-frequency resonance and crystalline impact reverb.
```

### Prompt (Abstract Data Architecture — Aligned with cor-build-websites KovelAI spec)

```
Abstract Data Architecture on deep navy background. Fine glowing gold lines
connect and pulse like a digital neural network over slate grey topology.
Stable, prestigious, secure. Slow forward-push camera motion creating a sense
of progress. Circuit traces pulse with blue-white energy at intersection nodes.
8-second seamless loop, 4K, 16:9. No chaotic movement. No text overlays.
With deep ambient hum and subtle crystalline network pulse sounds.
```

### Python SDK Execution

```python
from google import genai
from google.genai import types
import time

client = genai.Client()  # Uses GEMINI_API_KEY from env

# Load reference frame from Nano Banana 2 output
reference_image = types.Image.from_file(
    "labs/uphillsnowball/external_payloads/nanobanana_images/hero_reference.png"
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt="""Slow cinematic macro-lens descent toward an obsidian gavel head.
    The gavel strikes a translucent glass surface, sending cryptographic blue
    shockwaves rippling outward. Gold refractions. Deep navy. Volumetric fog.
    Smooth continuous shot. 8-second seamless loop. Prestigious.""",
    image=reference_image,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="4k",
        last_frame=reference_image,  # Seamless loop
    ),
)

while not operation.done:
    print("Generating hero video...")
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4")
print("✅ Hero video saved. Run: ./scripts/extract_frames.sh hero_gavel.mp4")
```

---

## 3. Post-Generation Pipeline

```bash
# 1. Extract frames for scroll-canvas
./scripts/extract_frames.sh \
  labs/uphillsnowball/external_payloads/veo_output/hero_gavel.mp4 \
  apps/kovelai/public/frames \
  30

# 2. Verify frame count (expect ~240 frames for 8s @ 30fps)
ls apps/kovelai/public/frames/ | wc -l

# 3. The chassis-preview.html / GavelHero.tsx canvas engine
#    will automatically preload and render these frames on scroll.
```

---

## 4. Fallback Assets (Until Veo Generation)

While waiting for Veo 3.1 generation, the chassis uses:
- **CSS gradient placeholder**: Navy → slate gradient with grain overlay
- **Grain SVG**: 4% opacity noise texture for premium feel
- **No `<video>` elements**: Canvas-only with scroll-driven frame playback

---

## 5. Brand Palette Reference

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-navy` | `#0A1628` | Primary background |
| `--color-slate` | `#2D3748` | Secondary surfaces |
| `--color-gold` | `#C9A84C` | Accent, CTA, highlights |
| `--color-blue-energy` | `#4A90D9` | Shockwave, data streams |
| `--color-white-ice` | `#F7FAFC` | Primary text |
