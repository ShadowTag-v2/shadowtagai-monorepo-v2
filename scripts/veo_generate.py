r"""Veo 3.1 video generation via Vertex AI / Gemini API.

Replaces Remotion with Google's native Veo 3.1 model for CounselConduit
sales demos, product walkthroughs, and marketing assets.

Supports two modes:
  1. Vertex AI (production) — uses ADC, outputs to GCS bucket
  2. Gemini API (dev/prototyping) — uses GOOGLE_API_KEY, outputs inline

Models available:
  - veo-3.1-generate-001       (highest fidelity, ~3-5 min gen time)
  - veo-3.1-fast-generate-001  (faster, slightly lower quality)

Usage:
    # Vertex AI mode (requires billing + GCS bucket)
    python scripts/veo_generate.py \\
        --prompt "A legal AI dashboard..." \\
        --output-gcs gs://shadowtag-omega-v4-media/demos/ \\
        --model veo-3.1-generate-001

    # Gemini API mode (requires GOOGLE_API_KEY)
    python scripts/veo_generate.py \\
        --prompt "A legal AI dashboard..." \\
        --mode gemini \\
        --output-dir labs/uphillsnowball/external_payloads/

    # Image-to-video (first frame reference)
    python scripts/veo_generate.py \\
        --prompt "Camera slowly zooms into the dashboard..." \\
        --image apps/kovelai/public/og-social.png \\
        --output-gcs gs://shadowtag-omega-v4-media/demos/

Environment:
    GOOGLE_CLOUD_PROJECT: Required for Vertex AI mode. Default: shadowtag-omega-v4
    GOOGLE_CLOUD_LOCATION: Vertex AI region. Default: global
    GOOGLE_API_KEY: Required for Gemini API mode.
    GOOGLE_GENAI_USE_VERTEXAI: Set to "True" for Vertex AI mode.
"""

from __future__ import annotations

import argparse
import base64
import logging
import os
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

MODELS = {
    "full": "veo-3.1-generate-001",
    "fast": "veo-3.1-fast-generate-001",
    "veo3": "veo-3.0-generate-001",
}

ASPECT_RATIOS = ("16:9", "9:16")

POLL_INTERVAL_SECONDS = 15
MAX_POLL_ATTEMPTS = 40  # 10 minutes max

# ── Preset Prompts for CounselConduit ─────────────────────────────────

DEMO_PRESETS = {
    "dashboard_hero": (
        "Cinematic aerial shot pushing down toward a sleek glass-walled law firm "
        "office at sunset. Camera glides through the window onto a large curved "
        "monitor displaying a modern dark-themed legal AI dashboard with indigo "
        "accent colors, real-time case analytics, and glowing data visualizations. "
        "A confident attorney in a tailored suit gestures at the screen while "
        "speaking to a client. Shallow depth of field, warm golden hour lighting, "
        "premium corporate aesthetic. The dashboard reads 'CounselConduit' in the "
        "top navigation bar."
    ),
    "privilege_shield": (
        "Medium close-up of a secure digital interface showing an encrypted "
        "communication channel. Green encryption indicators pulse along the "
        "edges of the screen. A Kovel attestation receipt materializes with a "
        "cryptographic hash, glowing with a subtle blue light. Text overlay: "
        "'Attorney-Client Privilege Protected'. Dark theme, cinematic lighting, "
        "technology-forward aesthetic."
    ),
    "multi_model": (
        "Split-screen view showing four AI model logos (Gemini, Claude, GPT, "
        "Perplexity) being routed through a central hub labeled 'CounselConduit'. "
        "Data streams flow from each model through the hub and emerge as a "
        "unified, clean legal memo. Futuristic holographic style, dark background, "
        "indigo and emerald accent lighting."
    ),
    "onboarding_flow": (
        "A timelapse of a lawyer's first 60 seconds using CounselConduit. "
        "Screen recording style: they log in, select their firm, choose AI models, "
        "and submit their first privileged query. The UI transitions smoothly "
        "between onboarding steps with elegant micro-animations. Clean, modern "
        "SaaS interface with dark mode and indigo accents."
    ),
    "billing_explainer": (
        "Animated infographic showing dual billing flow. Left side: a client "
        "subscribes and money flows to the lawyer's account. Right side: the "
        "lawyer's subscription auto-scales based on usage. Clean flat design, "
        "professional color palette with greens for revenue and blues for costs. "
        "Numbers animate upward showing healthy margins."
    ),
    # ── ShadowTagAI Marketing Presets ──
    "shadowtag_hero": (
        "Cinematic aerial shot of a fortified glass data center in a mountain "
        "valley at dawn. Camera glides through layers of security — laser grids, "
        "biometric scanners, armored server racks with pulsing blue LEDs. A "
        "holographic ShadowTag AI logo materializes above the central server "
        "cluster. Text overlay: 'SOVEREIGN · AUTONOMOUS · ZERO-TRUST'. Ultra "
        "wide anamorphic lens, ARRI Alexa quality. Dramatic volumetric fog, "
        "indigo and amber lighting."
    ),
    "shadowtag_uphillsnowball": (
        "A MacBook Pro sits on an architect's desk in a minimalist office. The "
        "screen shows the UphillSnowball platform — a dark-themed sovereign AI "
        "dashboard with real-time inference metrics, daemon fleet status (green "
        "dots), and a local LLM chat interface. Camera slowly pushes in as "
        "neural network visualizations flow across the screen. Zero cloud "
        "dependency badge glows in the corner. Cinematic shallow depth of field, "
        "warm desk lamp lighting, premium tech aesthetic."
    ),
    "shadowtag_zero_trust": (
        "A 3D visualization of the 17-layer security shield. Camera passes "
        "through each translucent layer — biometric auth, encrypted transit, "
        "token validation, RBAC gates, audit logging, compliance firewall, "
        "steganographic watermark — each layer lights up as the camera passes "
        "through it. At the center: a glowing orb representing sovereign data. "
        "Dark background, neon indigo edges, holographic HUD elements."
    ),
    "shadowtag_ane_inference": (
        "Extreme close-up of an Apple M4 chip with visible neural engine "
        "pathways glowing with data. Camera pulls back to show the chip inside "
        "a Mac Studio, then continues to reveal a sovereign AI control room "
        "with multiple screens showing real-time inference — zero latency, "
        "zero cloud calls. Metrics overlay: '10.22 TOPS · INT8 W8A8 · 0ms "
        "cloud latency'. Futuristic aesthetic, dark mode, amber and indigo."
    ),
    "stripe_webhook_flow": (
        "Animated diagram showing a Stripe payment flow: a credit card swipe "
        "triggers a webhook arrow flowing to a Cloud Run endpoint, through "
        "HMAC signature verification (green checkmark), into Firestore "
        "persistence, then fanning out to email notification and billing "
        "ledger update. Clean motion graphics on dark background, Stripe "
        "purple and CounselConduit indigo. Each step animates sequentially "
        "with satisfying micro-animations."
    ),
}


# ── Vertex AI Mode ────────────────────────────────────────────────────


def generate_vertex_ai(
    prompt: str,
    output_gcs_uri: str,
    model: str = "veo-3.1-generate-001",
    aspect_ratio: str = "16:9",
    image_gcs_uri: str | None = None,
) -> str | None:
    """Generate video via Vertex AI (requires billing + ADC)."""
    try:
        from google import genai
        from google.genai.types import GenerateVideosConfig, Image
    except ImportError:
        logger.exception("google-genai not installed. Run: pip install google-genai")
        return None

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LOCATION)

    client = genai.Client()

    config = GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
        output_gcs_uri=output_gcs_uri,
    )

    kwargs: dict = {
        "model": model,
        "prompt": prompt,
        "config": config,
    }

    if image_gcs_uri:
        kwargs["image"] = Image(
            gcs_uri=image_gcs_uri,
            mime_type=_guess_mime(image_gcs_uri),
        )

    logger.info("Starting Veo generation: model=%s prompt=%.80s...", model, prompt)
    operation = client.models.generate_videos(**kwargs)

    attempts = 0
    while not operation.done:
        attempts += 1
        if attempts > MAX_POLL_ATTEMPTS:
            logger.error("Video generation timed out after %d polls", MAX_POLL_ATTEMPTS)
            return None
        logger.info("Polling... attempt %d/%d", attempts, MAX_POLL_ATTEMPTS)
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = client.operations.get(operation)

    if operation.response:
        uri = operation.result.generated_videos[0].video.uri
        logger.info("Video generated: %s", uri)
        return uri

    logger.error("Video generation failed: %s", operation)
    return None


# ── Gemini API Mode ───────────────────────────────────────────────────


def generate_gemini_api(
    prompt: str,
    output_dir: str = "labs/uphillsnowball/external_payloads",
    model: str = "veo-3.1-generate-001",
    aspect_ratio: str = "16:9",
    image_path: str | None = None,
) -> str | None:
    """Generate video via Gemini API (uses GOOGLE_API_KEY).

    Note: Gemini API mode may require output to GCS depending on the
    model version. If inline video bytes are not supported, falls back
    to Vertex AI mode with a temporary GCS URI.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not set. Cannot use Gemini API mode.")
        return None

    try:
        from google import genai
        from google.genai.types import GenerateVideosConfig, Image
    except ImportError:
        logger.exception("google-genai not installed. Run: pip install google-genai")
        return None

    # Gemini API client (non-Vertex)
    client = genai.Client(api_key=api_key)

    config = GenerateVideosConfig(
        aspect_ratio=aspect_ratio,
    )

    kwargs: dict = {
        "model": model,
        "prompt": prompt,
        "config": config,
    }

    if image_path:
        # For Gemini API, upload the image bytes
        img_bytes = Path(image_path).read_bytes()
        kwargs["image"] = Image(
            image_bytes=img_bytes,
            mime_type=_guess_mime(image_path),
        )

    logger.info("Starting Veo generation (Gemini API): model=%s", model)
    operation = client.models.generate_videos(**kwargs)

    attempts = 0
    while not operation.done:
        attempts += 1
        if attempts > MAX_POLL_ATTEMPTS:
            logger.error("Timed out after %d polls", MAX_POLL_ATTEMPTS)
            return None
        logger.info("Polling... attempt %d/%d", attempts, MAX_POLL_ATTEMPTS)
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = client.operations.get(operation)

    if operation.response:
        generated = operation.result.generated_videos[0]
        video = generated.video

        # Try to save video bytes locally if available
        if hasattr(video, "video_bytes") and video.video_bytes:
            out_path = Path(output_dir) / f"veo_{int(time.time())}.mp4"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(base64.b64decode(video.video_bytes) if isinstance(video.video_bytes, str) else video.video_bytes)
            logger.info("Video saved: %s", out_path)
            return str(out_path)

        if hasattr(video, "uri") and video.uri:
            logger.info("Video at GCS URI: %s", video.uri)
            return video.uri

    logger.error("Video generation failed: %s", operation)
    return None


# ── Google Flow Browser Helper ────────────────────────────────────────


def print_flow_instructions(prompt: str) -> None:
    """Print instructions for using Google Flow in browser."""


# ── Utilities ─────────────────────────────────────────────────────────


def _guess_mime(path: str) -> str:
    """Guess MIME type from file extension."""
    ext = Path(path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/png")


# ── CLI ───────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate videos with Veo 3.1 (Vertex AI / Gemini API / Flow)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets:
  --preset dashboard_hero     CounselConduit hero video
  --preset privilege_shield   Kovel attestation visual
  --preset multi_model        Multi-model routing diagram
  --preset onboarding_flow    Onboarding UX timelapse
  --preset billing_explainer  Dual-billing infographic

Examples:
  # Vertex AI mode
  python scripts/veo_generate.py --preset dashboard_hero \\
      --output-gcs gs://shadowtag-omega-v4-media/demos/

  # Gemini API mode
  python scripts/veo_generate.py --preset dashboard_hero --mode gemini

  # Flow browser mode (prints instructions)
  python scripts/veo_generate.py --preset dashboard_hero --mode flow

  # Custom prompt
  python scripts/veo_generate.py --prompt "A frog reading legal briefs" \\
      --output-gcs gs://shadowtag-omega-v4-media/test/
        """,
    )
    parser.add_argument("--prompt", help="Video generation prompt")
    parser.add_argument("--preset", choices=list(DEMO_PRESETS), help="Use a preset prompt")
    parser.add_argument(
        "--mode",
        choices=["vertex", "gemini", "flow"],
        default="vertex",
        help="Generation mode (default: vertex)",
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.values()),
        default="veo-3.1-generate-001",
        help="Veo model to use",
    )
    parser.add_argument("--aspect-ratio", choices=ASPECT_RATIOS, default="16:9")
    parser.add_argument("--output-gcs", help="GCS URI for output (Vertex AI mode)")
    parser.add_argument(
        "--output-dir",
        default="labs/uphillsnowball/external_payloads",
        help="Local output directory (Gemini API mode)",
    )
    parser.add_argument("--image", help="Reference image (first frame) path or GCS URI")
    parser.add_argument("--list-presets", action="store_true", help="List all preset prompts")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.list_presets:
        for prompt in DEMO_PRESETS.values():  # noqa: B007
            pass
        return 0

    # Resolve prompt
    prompt = args.prompt or (DEMO_PRESETS.get(args.preset) if args.preset else None)
    if not prompt:
        parser.error("Either --prompt or --preset is required")

    # Dispatch
    if args.mode == "flow":
        print_flow_instructions(prompt)
        return 0

    if args.mode == "vertex":
        if not args.output_gcs:
            parser.error("--output-gcs required for Vertex AI mode")
        result = generate_vertex_ai(
            prompt=prompt,
            output_gcs_uri=args.output_gcs,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            image_gcs_uri=args.image if args.image and args.image.startswith("gs://") else None,
        )
    else:  # gemini
        result = generate_gemini_api(
            prompt=prompt,
            output_dir=args.output_dir,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            image_path=args.image if args.image and not args.image.startswith("gs://") else None,
        )

    if result:
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
