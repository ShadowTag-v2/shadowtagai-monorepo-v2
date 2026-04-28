# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from __future__ import annotations

"""Veo 3.1 Pipeline — Cinematic Video Generation for ShadowTag.

Uses the google-genai SDK to generate video via Gemini API / Vertex AI Veo 3.1,
extract frames for scroll animations, and manage presets.

Supports:
  - Text-to-video generation (Veo 3.1, 3.1 Fast, 3.1 Lite, 3.0, 2.0)
  - Image-to-video (first frame / first+last frame interpolation)
  - Video extension (extend Veo-generated videos by 7s, up to 20x)
  - Reference images (subject/style/composition, Veo 3.1 only)
  - Resolution control (720p, 1080p, 4K depending on model)
  - Frame extraction via ffmpeg

Usage:
    python scripts/veo_pipeline.py --preset hero_drift
    python scripts/veo_pipeline.py --preset counselconduit_hero --model veo-3.1-fast-generate-preview
    python scripts/veo_pipeline.py --extend path/to/veo_video.mp4 --prompt "Continue the scene..."
    python scripts/veo_pipeline.py --image path/to/first_frame.png --prompt "Animate this scene"
    python scripts/veo_pipeline.py --extract path/to/video.mp4 --fps 30
    python scripts/veo_pipeline.py --list
"""

import argparse  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------
MODELS = {
    "veo-3.1": "veo-3.1-generate-001",
    "veo-3.1-fast": "veo-3.1-fast-generate-001",
    "veo-3.1-lite": "veo-3.1-lite-generate-001",
    "veo-3": "veo-3.0-generate-001",
    "veo-3-fast": "veo-3.0-fast-generate-001",
    "veo-2": "veo-2.0-generate-001",
}

DEFAULT_MODEL = "veo-3.1-generate-001"

# ---------------------------------------------------------------------------
# Preset library
# ---------------------------------------------------------------------------
PRESETS = {
    "hero_drift": {
        "prompt": (
            "Cinematic aerial tracking shot of a sleek matte-black sports car powersliding "
            "through rain-slicked neon-lit city streets at night. Tire smoke billows in "
            "volumetric clouds illuminated by cyan and teal neon signs. The car is a generic "
            "mid-engine supercar with sharp aggressive lines — NOT a branded vehicle, no logos, "
            "no badges, no recognizable brand design. Camera follows from a low three-quarter "
            "rear angle. Sparks fly from the rear wheels. Wet pavement reflects neon colors. "
            "Dark moody cyberpunk atmosphere. Shot on ARRI Alexa with 50mm anamorphic lens. "
            "No sharp cuts, continuous smooth tracking motion."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "generic_supercar_peelout": {
        "prompt": (
            "Dramatic close-up of a matte-black unbranded supercar doing a standing burnout "
            "on wet asphalt at night. Massive tire smoke clouds billow from the rear wheels, "
            "illuminated by teal and cyan neon underbody glow. The car has aggressive sharp "
            "body lines, large rear diffuser, and quad exhaust tips — but NO brand logos, "
            "NO badges, NO recognizable manufacturer design cues. Camera starts low behind "
            "the wheel arch, slowly panning to a dramatic rear three-quarter shot. Rain "
            "droplets on the bodywork catch neon reflections. Cinematic depth of field, "
            "shot on RED V-Raptor, 85mm lens. Continuous smooth motion."
        ),
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
    },
    "legal_shield_hero": {
        "prompt": (
            "Slow cinematic push into a holographic shield dome glowing in bright cyan "
            "and teal, protecting a futuristic server room. Digital data streams flow "
            "upward through the dome. Scales of justice rotate slowly overhead as a "
            "holographic projection. Rain falls outside the dome, wet reflections on "
            "dark pavement. Cyberpunk city skyline in background. No people, no vehicles. "
            "Volumetric lighting, premium tech aesthetic. Shot on RED V-Raptor, "
            "35mm lens, shallow depth of field."
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


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------
def _get_client():
    """Create a google-genai client.

    Uses Gemini API by default (API key from GEMINI_API_KEY or
    GOOGLE_API_KEY env var). Falls back to Vertex AI if
    USE_VERTEX_AI=1 is set.

    Returns:
        google.genai.Client instance.

    """
    try:
        from google import genai  # noqa: PLC0415
    except ImportError:
        sys.exit(1)

    if os.environ.get("USE_VERTEX_AI", "").strip() == "1":
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
        location = os.environ.get("VERTEX_LOCATION", "us-central1")
        return genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )

    # Gemini API path — requires GEMINI_API_KEY or GOOGLE_API_KEY
    return genai.Client()


def _load_image(image_path: str):
    """Load an image file and return it as a genai-compatible Image object.

    Uses types.Image.from_file() which handles raw bytes and MIME detection.

    Args:
        image_path: Path to the image file.

    Returns:
        google.genai.types.Image with inline data (raw bytes, not base64).

    """
    from google.genai import types  # noqa: PLC0415

    path = Path(image_path)
    if not path.exists():
        sys.exit(1)

    return types.Image.from_file(location=str(path))


# ---------------------------------------------------------------------------
# Frame extraction
# ---------------------------------------------------------------------------
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
        return 0

    return len(list(out.glob("frame_*.png")))


# ---------------------------------------------------------------------------
# Poll helper
# ---------------------------------------------------------------------------
def _poll_operation(client, operation, poll_interval: int = 10):
    """Poll a long-running operation until completion.

    Args:
        client: genai.Client instance.
        operation: The operation object from generate_videos().
        poll_interval: Seconds between polls.

    Returns:
        The completed operation.

    """
    elapsed = 0
    while not operation.done:
        time.sleep(poll_interval)
        elapsed += poll_interval
        _mins, _secs = divmod(elapsed, 60)
        operation = client.operations.get(operation=operation)
    return operation


def _save_videos(client, operation, prefix: str) -> list[Path]:
    """Download and save generated videos from a completed operation.

    For Gemini API: downloads video bytes via client.files.download() first,
    then calls video.save() to write to disk.
    For Vertex AI: videos are in GCS at the output_gcs_uri; the URI is printed.

    Args:
        client: genai.Client instance (needed for files.download on Gemini API).
        operation: Completed operation with result.
        prefix: Filename prefix for saved videos.

    Returns:
        List of saved file paths.

    """
    if not operation.result or not operation.result.generated_videos:
        return []

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, gen_video in enumerate(operation.result.generated_videos):
        video = gen_video.video
        out_path = OUTPUT_DIR / f"{prefix}_{i}.mp4"

        if video.uri:
            pass

        # Gemini API returns a server-side URI; download bytes before saving.
        # Vertex AI stores videos in GCS (output_gcs_uri); bytes are not
        # available via files.download — the URI is the deliverable.
        if not video.video_bytes and not client.vertexai:
            client.files.download(file=video)

        if video.video_bytes:
            video.save(str(out_path))
            saved.append(out_path)
        else:
            pass
    return saved


# ---------------------------------------------------------------------------
# Core generation
# ---------------------------------------------------------------------------
def generate_video(
    preset_name: str,
    model: str = DEFAULT_MODEL,
    resolution: str = "720p",
    person_generation: str | None = None,
) -> list[Path]:
    """Generate video using Veo via google-genai SDK.

    Args:
        preset_name: Name of the preset to use from PRESETS dict.
        model: Model ID string.
        resolution: Output resolution (720p, 1080p, 4k).
        person_generation: Person generation policy (allow_all, allow_adult, dont_allow).

    Returns:
        List of saved video paths.

    """
    from google.genai import types  # noqa: PLC0415

    if preset_name not in PRESETS:
        sys.exit(1)

    preset = PRESETS[preset_name]
    client = _get_client()

    config_kwargs = {
        "number_of_videos": 1,
        "duration_seconds": preset["duration_seconds"],
        "aspect_ratio": preset["aspect_ratio"],
        "resolution": resolution,
    }
    if person_generation:
        config_kwargs["person_generation"] = person_generation

    # Vertex AI requires output_gcs_uri; Gemini API does not support it.
    if client.vertexai:
        gcs_prefix = os.environ.get(
            "VEO_OUTPUT_GCS",
            "gs://shadowtag-omega-v4-veo-output/videos/",
        )
        config_kwargs["output_gcs_uri"] = gcs_prefix

    config = types.GenerateVideosConfig(**config_kwargs)

    try:
        operation = client.models.generate_videos(
            model=model,
            prompt=preset["prompt"],
            config=config,
        )

        operation = _poll_operation(client, operation)
        return _save_videos(client, operation, preset_name)

    except Exception:
        sys.exit(1)


def generate_from_image(
    prompt: str,
    image_path: str,
    last_image_path: str | None = None,
    model: str = DEFAULT_MODEL,
    duration_seconds: int = 8,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
) -> list[Path]:
    """Generate video from a starting image (and optional last frame).

    Args:
        prompt: Text prompt describing the desired video.
        image_path: Path to the first frame image.
        last_image_path: Optional path to the last frame image (interpolation).
        model: Model ID string.
        duration_seconds: Video duration.
        aspect_ratio: Aspect ratio.
        resolution: Output resolution.

    Returns:
        List of saved video paths.

    """
    from google.genai import types  # noqa: PLC0415

    client = _get_client()
    first_image = _load_image(image_path)

    config = types.GenerateVideosConfig(
        number_of_videos=1,
        duration_seconds=duration_seconds,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
    )

    kwargs = {
        "model": model,
        "prompt": prompt,
        "image": first_image,
        "config": config,
    }

    if last_image_path:
        last_image = _load_image(last_image_path)
        config.last_frame = last_image
    else:
        pass

    # Vertex AI requires output_gcs_uri.
    if client.vertexai:
        gcs_prefix = os.environ.get(
            "VEO_OUTPUT_GCS",
            "gs://shadowtag-omega-v4-veo-output/videos/",
        )
        config.output_gcs_uri = gcs_prefix

    try:
        operation = client.models.generate_videos(**kwargs)
        operation = _poll_operation(client, operation)

        stem = Path(image_path).stem
        return _save_videos(client, operation, f"img2vid_{stem}")

    except Exception:
        sys.exit(1)


def extend_video(
    prompt: str,
    video_path: str,
    model: str = DEFAULT_MODEL,
    resolution: str = "720p",
) -> list[Path]:
    """Extend a previously Veo-generated video by ~7 seconds.

    Note: Only Veo-generated videos can be extended. The input video must
    be a video object from a previous generation, stored on the server
    for up to 2 days. For local files, load as bytes.

    Args:
        prompt: Text prompt for the extension.
        video_path: Path to the Veo-generated video to extend.
        model: Model ID (must be veo-3.1-generate-preview; Lite not supported).
        resolution: Output resolution.

    Returns:
        List of saved video paths.

    """
    from google.genai import types  # noqa: PLC0415

    client = _get_client()

    path = Path(video_path)
    if not path.exists():
        sys.exit(1)

    # Video.from_file handles raw bytes and MIME detection correctly.
    video_obj = types.Video.from_file(location=str(path))

    ext_config_kwargs = {
        "number_of_videos": 1,
        "resolution": resolution,
    }
    # Vertex AI requires output_gcs_uri.
    if client.vertexai:
        gcs_prefix = os.environ.get(
            "VEO_OUTPUT_GCS",
            "gs://shadowtag-omega-v4-veo-output/videos/",
        )
        ext_config_kwargs["output_gcs_uri"] = gcs_prefix

    try:
        operation = client.models.generate_videos(
            model=model,
            prompt=prompt,
            video=video_obj,
            config=types.GenerateVideosConfig(**ext_config_kwargs),
        )

        operation = _poll_operation(client, operation)

        stem = path.stem
        return _save_videos(client, operation, f"extended_{stem}")

    except Exception:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Preset listing
# ---------------------------------------------------------------------------
def list_presets() -> None:
    """Print all available presets and models."""
    for _preset in PRESETS.values():
        pass

    for _alias, _model_id in MODELS.items():
        pass


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Veo 3.1 Pipeline — Cinematic Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s --preset hero_drift
  %(prog)s --preset hero_drift --model veo-3.1-fast
  %(prog)s --image first.png --prompt "Animate this scene"
  %(prog)s --image first.png --last-image last.png --prompt "Interpolate"
  %(prog)s --extend video.mp4 --prompt "Continue the scene"
  %(prog)s --extract video.mp4 --fps 30
  %(prog)s --list
""",
    )

    # Generation modes
    gen = parser.add_argument_group("Generation")
    gen.add_argument("--preset", help="Generate video with named preset")
    gen.add_argument("--prompt", help="Text prompt (used with --image or --extend)")
    gen.add_argument("--image", help="First frame image for image-to-video")
    gen.add_argument("--last-image", help="Last frame image for interpolation (with --image)")
    gen.add_argument("--extend", help="Extend a Veo-generated video file")

    # Options
    opts = parser.add_argument_group("Options")
    opts.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model ID or alias (default: {DEFAULT_MODEL}). Aliases: {', '.join(MODELS.keys())}",
    )
    opts.add_argument("--resolution", default="720p", choices=["720p", "1080p", "4k"], help="Output resolution (default: 720p)")
    opts.add_argument("--duration", type=int, default=8, choices=[4, 5, 6, 8], help="Duration in seconds (default: 8)")
    opts.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16"], help="Aspect ratio (default: 16:9)")
    opts.add_argument("--person-generation", choices=["allow_all", "allow_adult", "dont_allow"], help="Person generation policy")

    # Frame extraction
    ext = parser.add_argument_group("Frame Extraction")
    ext.add_argument("--extract", help="Extract frames from video file")
    ext.add_argument("--fps", type=int, default=30, help="FPS for frame extraction (default: 30)")
    ext.add_argument("--output", help="Output directory for frames")

    # Info
    parser.add_argument("--list", action="store_true", help="List available presets and models")

    args = parser.parse_args()

    # Resolve model alias → full model ID
    model = MODELS.get(args.model, args.model)

    if args.list:
        list_presets()
    elif args.extract:
        output = args.output or f"public/frames/{Path(args.extract).stem}"
        extract_frames(args.extract, output, args.fps)
    elif args.preset:
        generate_video(
            args.preset,
            model=model,
            resolution=args.resolution,
            person_generation=args.person_generation,
        )
    elif args.image and args.prompt:
        generate_from_image(
            prompt=args.prompt,
            image_path=args.image,
            last_image_path=args.last_image,
            model=model,
            duration_seconds=args.duration,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
        )
    elif args.extend and args.prompt:
        extend_video(
            prompt=args.prompt,
            video_path=args.extend,
            model=model,
            resolution=args.resolution,
        )
    elif (args.extend and not args.prompt) or (args.image and not args.prompt):
        sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
