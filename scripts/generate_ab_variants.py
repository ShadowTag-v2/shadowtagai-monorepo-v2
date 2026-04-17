#!/usr/bin/env python3
"""Generate A/B variant hero videos with alternate color palettes using Veo 3.1.

Usage:
    python3 scripts/generate_ab_variants.py [--variant warm|cool|monochrome]

Each variant produces a different color mood for multivariate testing:
- warm: Amber/copper tones (higher conversion for trust-heavy verticals)
- cool: Arctic blue/silver (tech authority, data sovereignty)
- monochrome: Grayscale with accent (minimalist premium)
"""

import argparse
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

VARIANTS = {
    "warm": {
        "shadowtag": (
            "A seamless 8-second loop of a fluid kinetic aura. "
            "Soft, overlapping blobs of warm amber (#D4A574), burnished copper (#B87333), "
            "and deep rust (#8B4513) slowly shift and undulate like a living energy field. "
            "The motion is organic, slow, and hypnotic. Camera: very slow push-in. "
            "Style: abstract, premium, cinematic. No text, no UI elements."
        ),
        "kovelai": (
            "A seamless 8-second loop of abstract data architecture in warm tones. "
            "Deep mahogany (#4A0E0E) and rich bronze (#CD7F32) with fine, glowing copper lines "
            "that connect and pulse like a digital neural network. "
            "Stable, prestigious, secure. Slow forward-push camera motion. "
            "Style: abstract, architectural, legal-tech. No text."
        ),
    },
    "cool": {
        "shadowtag": (
            "A seamless 8-second loop of a fluid kinetic aura. "
            "Soft, overlapping blobs of arctic blue (#A8D8EA), silver (#C0C0C0), "
            "and deep navy (#0C1445) slowly shift and undulate like frozen light. "
            "The motion is glacial, crystalline, and precise. Camera: very slow pull-back. "
            "Style: abstract, premium, data-sovereign. No text, no UI elements."
        ),
        "kovelai": (
            "A seamless 8-second loop of abstract data architecture in cool tones. "
            "Deep slate (#2F4F4F) and platinum (#E5E4E2) with fine, glowing ice-blue lines "
            "that connect and pulse like a secure blockchain network. "
            "Authoritative, clinical, trustworthy. Slow lateral pan camera motion. "
            "Style: abstract, institutional, legal-tech. No text."
        ),
    },
    "monochrome": {
        "shadowtag": (
            "A seamless 8-second loop of a fluid kinetic aura in grayscale. "
            "Soft, overlapping blobs of charcoal (#36454F), silver (#C0C0C0), "
            "and pure white (#FFFFFF) slowly shift with one accent of emerald (#00FFB3). "
            "The motion is minimal, elegant, and hypnotic. Camera: static with subtle drift. "
            "Style: abstract, minimalist, ultra-premium. No text, no UI elements."
        ),
        "kovelai": (
            "A seamless 8-second loop of abstract data architecture in monochrome. "
            "Deep black (#0A0A0A) and light grey (#D3D3D3) with fine, glowing gold (#FFD700) "
            "accent lines that connect and pulse like a precision instrument. "
            "Austere, powerful, unbreakable. Very slow zoom-in camera motion. "
            "Style: abstract, monochrome, legal-authority. No text."
        ),
    },
}


def generate_variant(prompt: str, output_path: str) -> str:
    """Generate a single video variant."""
    print(f"  Generating: {output_path}")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=8,
            resolution="720p",
        ),
    )
    while not operation.done:
        print("    Waiting for video generation...")
        time.sleep(10)
        operation = client.operations.get(operation)

    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)
    video.video.save(output_path)
    print(f"  ✅ Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate A/B hero video variants")
    parser.add_argument(
        "--variant",
        choices=["warm", "cool", "monochrome", "all"],
        default="all",
        help="Color palette variant to generate",
    )
    parser.add_argument(
        "--output-dir",
        default="/tmp/hero-variants",
        help="Output directory for generated videos",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    variants_to_gen = list(VARIANTS.keys()) if args.variant == "all" else [args.variant]

    for variant_name in variants_to_gen:
        prompts = VARIANTS[variant_name]
        print(f"\n=== Variant: {variant_name} ===")

        for platform, prompt in prompts.items():
            output_path = os.path.join(args.output_dir, f"{platform}-{variant_name}.mp4")
            generate_variant(prompt, output_path)

    print(f"\n✅ All variants saved to {args.output_dir}")
    print("Upload to GCS with:")
    print(f"  gcloud storage cp {args.output_dir}/*.mp4 gs://shadowtag-omega-v4-archive/hero-videos/variants/")


if __name__ == "__main__":
    main()
