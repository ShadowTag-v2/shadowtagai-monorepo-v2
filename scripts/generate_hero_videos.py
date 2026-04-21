#!/usr/bin/env python3
"""Veo 3.1 Hero Video Generator — Full Design-to-Video Pipeline
Generates Fluid Kinetic Aura (ShadowTag) and Legal Data Architecture (KovelAI)
background loops using brand colors extracted from Stitch MCP design tokens.
"""

import os
import sys
import time

# Must use google-genai SDK
from google import genai
from google.genai import types

# Load .env if present (GEMINI_API_KEY lives there)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    sys.exit(1)

client = genai.Client(api_key=api_key)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "apps")

# ─── ShadowTag AI: Fluid Kinetic Aura ───
# Brand colors from Stitch: primary=#d2bbff, secondary=#0df274, bg=#09090b
SHADOWTAG_PROMPT = (
    "A seamless 8-second looping 4K background video of a 'Fluid Kinetic Aura.' "
    "Soft, overlapping mesh gradient blobs in deep violet (#7c3aed), "
    "electric green (#0df274), and cool lavender (#d2bbff) slowly shift and undulate "
    "against an ultra-dark obsidian background (#09090b). "
    "The motion is slow, organic, and hypnotic — like a living energy field. "
    "No text, no UI elements, no objects — only abstract flowing gradients. "
    "The camera has a subtle, slow forward-push creating a sense of progress. "
    "Professional B2B aesthetic. Calm, sophisticated, premium feel. "
    "Think high-end SaaS subscription website hero background. "
    "4K resolution, 24fps, seamless loop."
)

# ─── KovelAI: Abstract Data Architecture ───
# Brand colors from Stitch: primary=#e6c487 (gold), secondary=#aac7ff (steel blue), bg=#071325
KOVELAI_PROMPT = (
    "A seamless 8-second looping 4K background video of 'Abstract Data Architecture.' "
    "Deep navy (#071325) and slate grey tones with fine, glowing gold (#c9a96e) lines "
    "that connect and pulse like a digital neural network or legal document hierarchy. "
    "Interspersed with cool steel blue (#aac7ff) data streams flowing through the network. "
    "The aesthetic must feel stable, prestigious, and secure — not chaotic. "
    "No text, no UI elements, no objects — only abstract connected geometric lines and nodes. "
    "A slow 'forward-push' camera motion creates a sense of progress and authority. "
    "Legal-tech aesthetic: order, security, processing massive data. "
    "4K resolution, 24fps, seamless loop."
)


def generate_video(prompt: str, output_path: str, label: str) -> bool | None:
    """Generate a video with Veo 3.1 and save it."""
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                resolution="720p",  # Use 720p for faster generation; upscale later
            ),
        )

        # Poll until done
        poll_count = 0
        while not operation.done:
            poll_count += 1
            poll_count * 15
            time.sleep(15)
            operation = client.operations.get(operation)

        # Download
        if operation.response and operation.response.generated_videos:
            video = operation.response.generated_videos[0]
            client.files.download(file=video.video)
            video.video.save(output_path)
            return True
        if hasattr(operation, "error") and operation.error:
            pass
        return False

    except Exception:
        return False


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "both"

    results = {}

    if target in ("shadowtag", "both"):
        st_path = os.path.join(OUTPUT_DIR, "shadowtagai", "public", "fluid-kinetic-aura.mp4")
        results["shadowtag"] = generate_video(SHADOWTAG_PROMPT, st_path, "ShadowTag AI — Fluid Kinetic Aura")

    if target in ("kovelai", "both"):
        kv_path = os.path.join(OUTPUT_DIR, "kovelai", "public", "legal-data-arch.mp4")
        results["kovelai"] = generate_video(KOVELAI_PROMPT, kv_path, "KovelAI — Legal Data Architecture")

    for _name, _success in results.items():
        pass

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
