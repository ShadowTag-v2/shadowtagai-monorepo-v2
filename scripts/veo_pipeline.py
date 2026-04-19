"""Veo 3.1 Pipeline — Cinematic Video Generation for ShadowTag.

Uses the google-genai SDK to generate video via Vertex AI Veo 3.1,
extract frames for scroll animations, and manage presets.

Usage:
    python scripts/veo_pipeline.py --preset hero_drift
    python scripts/veo_pipeline.py --preset counselconduit_hero
    python scripts/veo_pipeline.py --extract path/to/video.mp4 --fps 30
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Preset library
PRESETS = {
    "hero_drift": {
        "prompt": (
            "Cinematic aerial tracking shot of a sleek matte-black autonomous vehicle "
            "drifting through a rain-slicked neon-lit Tokyo intersection at golden hour. "
            "Camera follows from 45-degree angle, shallow depth of field, lens flare from "
            "brake lights reflecting on wet asphalt, volumetric fog, shot on ARRI Alexa "
            "with 85mm anamorphic lens. No sharp cuts, continuous smooth motion."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "counselconduit_hero": {
        "prompt": (
            "Cinematic close-up of a modern glass-walled law office at dusk. A holographic "
            "AI interface materializes above a mahogany desk, displaying legal document "
            "analysis with glowing teal data streams. Camera slowly dollies forward through "
            "warm ambient lighting, bokeh from city skyline through floor-to-ceiling windows. "
            "Professional, premium, trustworthy atmosphere. Shot on RED V-Raptor, 50mm lens, "
            "shallow depth of field. No people visible. Continuous smooth motion."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "shadowtagai_marketing": {
        "prompt": (
            "Dramatic establishing shot of a futuristic data center with blue-violet "
            "bioluminescent lighting. Camera cranes upward revealing rows of servers "
            "with flowing data particle effects. Sovereign AI infrastructure aesthetic. "
            "Cool tones, volumetric lighting, mist. Industrial yet elegant. "
            "Shot on Blackmagic URSA, 18mm wide-angle lens. Slow upward crane motion."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "onboarding_flow": {
        "prompt": (
            "Screen recording style animation of a premium SaaS dashboard loading. "
            "Clean dark-mode UI with teal accent colors materializes section by section. "
            "Cards slide in with spring physics, charts animate with smooth easing, "
            "navigation highlights pulse subtly. Professional, polished, premium feel. "
            "Flat camera, no depth of field. Smooth continuous animation."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "billing_explainer": {
        "prompt": (
            "Animated infographic showing a billing flow: credit card icon transforms "
            "into flowing particles that split into three streams labeled with pricing tiers. "
            "Clean white background with teal and dark-navy accents. Minimal, elegant "
            "motion graphics style. Numbers count up smoothly. Professional SaaS aesthetic. "
            "Flat 2D, smooth slow animation, no camera movement."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "stripe_webhook": {
        "prompt": (
            "Technical visualization: a webhook event travels as a glowing data packet "
            "from a Stripe logo through a secure tunnel into a server rack. The packet "
            "is inspected by a shield icon (HMAC verification), then splits into "
            "database writes and notification dispatches. Dark background, neon-teal "
            "accent lines, grid overlay. Cyberpunk-meets-enterprise aesthetic. "
            "Continuous smooth camera pan from left to right."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
}

OUTPUT_DIR = Path("labs/uphillsnowball/external_payloads/veo_output")


def extract_frames(video_path: str, output_dir: str, fps: int = 30) -> int:
    """Extract frames from a video file using ffmpeg.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save extracted frames.
        fps: Frames per second to extract.

    Returns:
        Number of frames extracted.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"fps={fps}",
        "-q:v",
        "2",
        str(out / "frame_%04d.png"),
        "-y",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
        return 0

    frame_count = len(list(out.glob("frame_*.png")))
    print(f"✅ Extracted {frame_count} frames to {output_dir}")
    return frame_count


def generate_video(preset_name: str) -> None:
    """Generate video using Veo 3.1 via google-genai SDK.

    Args:
        preset_name: Name of the preset to use from PRESETS dict.
    """
    if preset_name not in PRESETS:
        print(f"❌ Unknown preset: {preset_name}")
        print(f"Available presets: {', '.join(PRESETS.keys())}")
        sys.exit(1)

    preset = PRESETS[preset_name]

    try:
        from google import genai  # noqa: PLC0415
    except ImportError:
        print("❌ google-genai SDK not installed. Run: pip install google-genai")
        sys.exit(1)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")

    client = genai.Client(
        vertexai=True,
        project=project_id,
        location="us-central1",
    )

    print(f"🎬 Generating video with preset: {preset_name}")
    print(f"   Prompt: {preset['prompt'][:80]}...")

    try:
        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=preset["prompt"],
            config={
                "number_of_videos": 1,
                "duration_seconds": preset["duration_seconds"],
                "aspect_ratio": preset["aspect_ratio"],
            },
        )

        print("⏳ Waiting for generation (2-5 minutes)...")

        while not operation.done:
            import time  # noqa: PLC0415

            time.sleep(10)
            operation = client.operations.get(operation)

        if operation.result and operation.result.generated_videos:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for i, video in enumerate(operation.result.generated_videos):
                out_path = OUTPUT_DIR / f"{preset_name}_{i}.mp4"
                video.video.save(str(out_path))
                print(f"✅ Saved: {out_path}")
        else:
            print("❌ No videos generated. Check Vertex AI quotas and permissions.")

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print("   Ensure gcloud auth and Vertex AI API are configured.")
        sys.exit(1)


def list_presets() -> None:
    """Print all available presets."""
    print("Available Veo 3.1 Presets:")
    print("=" * 60)
    for name, preset in PRESETS.items():
        print(f"\n🎬 {name}")
        print(f"   Duration: {preset['duration_seconds']}s")
        print(f"   Aspect: {preset['aspect_ratio']}")
        print(f"   Prompt: {preset['prompt'][:100]}...")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Veo 3.1 Pipeline")
    parser.add_argument("--preset", help="Generate video with named preset")
    parser.add_argument("--extract", help="Extract frames from video file")
    parser.add_argument("--fps", type=int, default=30, help="FPS for frame extraction")
    parser.add_argument("--output", help="Output directory for frames")
    parser.add_argument("--list", action="store_true", help="List available presets")

    args = parser.parse_args()

    if args.list:
        list_presets()
    elif args.extract:
        output = args.output or f"public/frames/{Path(args.extract).stem}"
        extract_frames(args.extract, output, args.fps)
    elif args.preset:
        generate_video(args.preset)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
