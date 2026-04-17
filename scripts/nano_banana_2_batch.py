#!/usr/bin/env python3
"""
Nano Banana 2 — Batch Image Regeneration
Model: gemini-3.1-flash-image-preview
Regenerates ALL website graphics + pitch deck assets.
"""

import os
import sys
import time
from io import BytesIO

import PIL.Image
from google import genai

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.1-flash-image-preview"

MONO = "/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"

# ── Image Generation Manifest ──
IMAGES = [
    # ── KovelAI Website ──
    {
        "name": "kovelai_hero",
        "path": f"{MONO}/apps/kovelai/public/img/hero.png",
        "prompt": (
            "Ultra-premium law office interior at night, floor-to-ceiling windows "
            "overlooking a glowing city skyline. A massive curved monitor displays "
            "encrypted data visualizations with golden circuit patterns. Dark ambient "
            "lighting with deep obsidian walls and warm gold accent LEDs. Cinematic "
            "wide-angle, 8K quality, photorealistic, no text overlays."
        ),
    },
    {
        "name": "kovelai_shield",
        "path": f"{MONO}/apps/kovelai/public/img/shield.png",
        "prompt": (
            "A luminous golden digital shield floating in dark space, embedded with "
            "the scales of justice hologram at its center. Intricate circuit board "
            "encryption patterns radiate outward. Flowing blue and gold data streams "
            "orbit the shield like protective rings. Dark obsidian background, "
            "cinematic lighting, photorealistic 8K render, no text."
        ),
    },
    {
        "name": "kovelai_risk_layers",
        "path": f"{MONO}/apps/kovelai/public/img/risk-layers.png",
        "prompt": (
            "Abstract concentric rings of golden light on a pure black background, "
            "showing 5 layers of digital protection. The outermost ring is fragmented "
            "and glitching, representing exposed data. Each inner ring becomes more "
            "solid and luminous, with the innermost core glowing brilliant gold, "
            "representing full attorney-client privilege. Particle effects between "
            "layers. Minimalist, futuristic, 8K, no text."
        ),
    },
    {
        "name": "kovelai_og_image",
        "path": f"{MONO}/apps/kovelai/public/images/og-image.png",
        "prompt": (
            "Social media preview card design: dark obsidian background with a "
            "central golden shield icon surrounded by subtle circuit patterns. "
            "Premium legal technology aesthetic. Clean, modern, 1200x630 aspect "
            "ratio composition. Warm gold and steel blue accents on dark background. "
            "Photorealistic, no text."
        ),
    },
    {
        "name": "kovelai_product_mockup",
        "path": f"{MONO}/apps/kovelai/public/images/product-mockup.png",
        "prompt": (
            "Floating MacBook Pro and iPhone showing a dark-themed legal AI dashboard "
            "with golden accent UI elements. The screens display real-time risk "
            "analytics charts and encrypted document previews. Devices float against "
            "a subtle gradient background (obsidian to dark navy). Reflections on a "
            "polished dark surface below. Studio lighting, 8K photorealistic, no text."
        ),
    },
    # ── ShadowTagAI Website ──
    {
        "name": "shadowtagai_hero_bg",
        "path": f"{MONO}/apps/shadowtagai/public/hero-bg.png",
        "prompt": (
            "Dark futuristic command center environment with massive holographic "
            "displays showing AI neural network visualizations. Deep blue and purple "
            "lighting with electric cyan accents. Abstract geometric shapes float in "
            "the background. Atmospheric fog and volumetric lighting create depth. "
            "Wide cinematic composition, 8K, photorealistic, no text."
        ),
    },
    {
        "name": "shadowtagai_product_bg",
        "path": f"{MONO}/apps/shadowtagai/public/product-bg.png",
        "prompt": (
            "Abstract dark technology environment with flowing data streams in "
            "electric blue and purple. A central glowing orb represents an AI core, "
            "surrounded by orbiting geometric shapes and particle effects. Dark "
            "obsidian background transitioning to deep space blue. Ethereal, "
            "minimalist, photorealistic 8K quality, no text."
        ),
    },
    {
        "name": "shadowtagai_logo",
        "path": f"{MONO}/apps/shadowtagai/public/logo.png",
        "prompt": (
            "Minimalist premium tech company logo icon: a stylized abstract 'S' "
            "formed from two interlocking geometric shapes, one in electric blue and "
            "one in deep purple. The shapes create a sense of security and "
            "intelligence. Clean edges, transparent background style on pure white, "
            "modern tech aesthetic. Simple, bold, iconic, 1024x1024."
        ),
    },
    # ── KovelAI Pitch Deck Assets ──
    {
        "name": "pitch_cover",
        "path": f"{MONO}/apps/kovelai/public/images/pitch-cover.png",
        "prompt": (
            "Ultra-premium investor pitch deck cover slide visual: sweeping aerial "
            "view of a modern glass courthouse at twilight, with golden light "
            "streaming through the architecture. A translucent AI neural network "
            "overlay connects the building to a glowing digital horizon. The "
            "composition conveys legal authority meeting cutting-edge technology. "
            "Cinematic, aspirational, 8K photorealistic, no text or logos."
        ),
    },
    {
        "name": "pitch_tam_market",
        "path": f"{MONO}/apps/kovelai/public/images/pitch-tam.png",
        "prompt": (
            "Elegant data visualization: a massive golden sphere representing a "
            "$300 billion legal tech market, floating above a dark reflective "
            "surface. Smaller glowing spheres orbit it representing market segments. "
            "Thin golden lines connect the spheres. Dark obsidian background with "
            "subtle grid lines. Futuristic, clean, infographic aesthetic, "
            "photorealistic 8K, no text or numbers."
        ),
    },
    {
        "name": "pitch_product_vision",
        "path": f"{MONO}/apps/kovelai/public/images/pitch-product.png",
        "prompt": (
            "Split-screen composition: on the left, a photorealistic hand holding "
            "a smartphone showing a sleek dark-themed legal AI app with gold accents. "
            "On the right, a desktop monitor showing the same platform's enterprise "
            "dashboard with rich data visualizations. Both screens connected by "
            "flowing golden particle streams. Dark studio background, premium "
            "product photography, 8K, no text."
        ),
    },
    {
        "name": "pitch_team",
        "path": f"{MONO}/apps/kovelai/public/images/pitch-team.png",
        "prompt": (
            "Abstract team visualization: five distinct glowing silhouettes standing "
            "in a semi-circle, each emanating a different color of light (gold, blue, "
            "cyan, purple, silver). They stand on a reflective dark surface with a "
            "subtle city skyline behind them. The light beams from each figure "
            "converge at a central point above, forming a unified golden star. "
            "Cinematic, inspirational, 8K, no text."
        ),
    },
]


def generate_image(item):
    """Generate a single image and save it."""
    print(f"\n🎨 Generating: {item['name']}...")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[item["prompt"]],
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                os.makedirs(os.path.dirname(item["path"]), exist_ok=True)
                image = PIL.Image.open(BytesIO(part.inline_data.data))
                image.save(item["path"])
                print(f"   ✅ Saved: {item['path']}")
                return True
            elif part.text is not None:
                print(f"   📝 Model note: {part.text[:100]}")
        print(f"   ⚠️  No image data returned for {item['name']}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🍌 NANO BANANA 2 — BATCH IMAGE REGENERATION")
    print(f"   Model: {MODEL}")
    print(f"   Total images: {len(IMAGES)}")
    print("=" * 60)

    success = 0
    failed = 0
    for i, item in enumerate(IMAGES, 1):
        print(f"\n[{i}/{len(IMAGES)}]", end="")
        if generate_image(item):
            success += 1
        else:
            failed += 1
        # Rate limit: 15 RPM for image gen
        if i < len(IMAGES):
            print("   ⏳ Cooling 5s (rate limit)...")
            time.sleep(5)

    print("\n" + "=" * 60)
    print(f"🎉 COMPLETE: {success} succeeded, {failed} failed")
    print("=" * 60)
