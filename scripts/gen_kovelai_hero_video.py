#!/usr/bin/env python3
"""
Veo 3.1 Hero Video Generator — KovelAI Legal Tech
=================================================
Generates an 8-second Abstract Data Architecture loop for the
KovelAI hero section background. Deep navy + slate grey + glowing gold.

Output: apps/kovelai/public/hero-videos/legal-data-arch.mp4

Usage (via uv Python 3.13 venv):
    GEMINI_API_KEY=<key> ~/.local/bin/uv run --python 3.13 python scripts/gen_kovelai_hero_video.py
"""

import os
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from google import genai

# ─── Output Configuration ────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "apps", "kovelai", "public", "hero-videos"
)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "legal-data-arch.mp4")

# ─── Veo 3.1 Prompt ──────────────────────────────────────────────────────────
# "Abstract Data Architecture" — Legal Tech precision aesthetic
# Warm gold neural network on deep navy. Stable, prestigious, secure.
HERO_PROMPT = """
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
""".strip()

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable not set.\n"
            "Run: export GEMINI_API_KEY=your_key_here"
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    client = genai.Client(api_key=api_key)

    print("▶  Submitting Veo 3.1 generation request...")
    print(f"   Model  : veo-3.1-generate-preview")
    print(f"   Output : {OUTPUT_FILE}")
    print()

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=HERO_PROMPT,
    )

    print("⏳  Polling for completion (typical: 3–8 minutes)...")
    poll_count = 0
    while not operation.done:
        poll_count += 1
        elapsed = poll_count * 15
        print(f"   [{elapsed:>4}s] Still generating...", end="\r", flush=True)
        time.sleep(15)
        operation = client.operations.get(operation)

    print(f"\n✅  Generation complete after ~{poll_count * 15}s")

    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("No videos in response. Check API quota or prompt.")

    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(OUTPUT_FILE)

    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"💾  Saved: {OUTPUT_FILE} ({size_mb:.1f} MB)")
    print()
    print("━" * 60)
    print("Next steps:")
    print("  1. Review the video: open apps/kovelai/public/hero-videos/legal-data-arch.mp4")
    print("  2. Upload to GCS:  gsutil cp apps/kovelai/public/hero-videos/legal-data-arch.mp4")
    print("     gs://shadowtag-omega-v4-archive/hero-videos/legal-data-arch.mp4")
    print("  3. firebase deploy --only hosting:kovelai")
    print("━" * 60)

if __name__ == "__main__":
    main()
