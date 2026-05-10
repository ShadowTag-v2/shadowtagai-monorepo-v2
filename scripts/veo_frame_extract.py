r"""Extract frames from Veo 3.1 generated videos for scroll animations.

Replaces the Kling 3.0 → manual frame extraction workflow with a
fully automated Veo 3.1 → ffmpeg pipeline.

The scroll animation pattern (from the Antigravity + Nano Banana 2 workflow):
  1. Generate image with Imagen 3 / Nano Banana 2 via Google Flow
  2. Generate video from that image via Veo 3.1 (image-to-video)
  3. Extract frames from video at controlled intervals
  4. Use frames in website for scroll-triggered animation

Why frames instead of video?
  - Scroll-synced video playback is choppy and unreliable
  - Individual frames give precise control over scroll position
  - Preloading frames = buttery smooth scroll animation
  - Works with any framework (vanilla JS, React, GSAP, etc.)

Usage:
    # Basic extraction (30 fps → all frames)
    python scripts/veo_frame_extract.py \\
        --input labs/uphillsnowball/external_payloads/hero_drift.mp4 \\
        --output public/frames/hero/

    # Extract specific frame count (optimized for scroll)
    python scripts/veo_frame_extract.py \\
        --input labs/uphillsnowball/external_payloads/hero_drift.mp4 \\
        --output public/frames/hero/ \\
        --frame-count 120

    # With quality/size optimization for web
    python scripts/veo_frame_extract.py \\
        --input labs/uphillsnowball/external_payloads/hero_drift.mp4 \\
        --output public/frames/hero/ \\
        --frame-count 90 \\
        --format webp \\
        --quality 85 \\
        --max-width 1920

    # Full pipeline: Veo generate + extract in one shot
    python scripts/veo_frame_extract.py \\
        --veo-prompt "A matte black Porsche 911 GT3 RS drifts..." \\
        --veo-image apps/kovelai/public/hero-car.png \\
        --output public/frames/hero/ \\
        --frame-count 120
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

SUPPORTED_FORMATS = ("png", "jpg", "webp")
DEFAULT_FRAME_COUNT = 120  # Good balance for 8s video scroll
DEFAULT_QUALITY = 85
DEFAULT_MAX_WIDTH = 1920


# ── Cinematic Scroll Presets ──────────────────────────────────────────

SCROLL_PRESETS = {
  "hero_drift": {
    "description": "Car drifting out of frame (replaces Kling 3.0 workflow)",
    "veo_prompt": (
      "A matte black Porsche 911 GT3 RS begins a controlled drift on "
      "a wet, dimly-lit industrial road at dusk. Rear tires spin, smoke "
      "forms beneath the chassis, the car slides sideways with precision. "
      "Camera follows in a smooth tracking shot. The car accelerates out "
      "of frame to the right. Lights dim, ending on a pure black screen. "
      "Cinematic atmosphere, dramatic volumetric lighting, rain-slicked "
      "asphalt reflections. No sharp cuts, no visible driver, smooth "
      "continuous motion. Shot on ARRI Alexa, anamorphic lens, 24fps."
    ),
    "frame_count": 120,
    "aspect_ratio": "16:9",
  },
  "product_reveal": {
    "description": "Slow reveal of a product (SaaS dashboard, device, etc.)",
    "veo_prompt": (
      "Extreme close-up of a sleek dark-themed software dashboard on a "
      "curved ultrawide monitor. Camera slowly pulls back to reveal the "
      "full interface glowing with indigo accent lights in a premium "
      "glass-walled office. Shallow depth of field transitions to deep "
      "focus. Ambient blue-purple lighting, reflections on the desk "
      "surface. Cinematic, corporate, premium aesthetic. Smooth "
      "continuous camera pullback. No cuts."
    ),
    "frame_count": 90,
    "aspect_ratio": "16:9",
  },
  "counselconduit_hero": {
    "description": "CounselConduit legal AI dashboard hero scroll",
    "veo_prompt": (
      "A confident attorney in a tailored dark suit sits at a mahogany "
      "desk with a curved monitor displaying 'CounselConduit' legal AI "
      "dashboard. The camera slowly pushes in from a wide establishing "
      "shot of the glass-walled law office at golden hour. Data "
      "visualizations animate on screen — case analytics, privilege "
      "shields, and multi-model routing flows. Warm, professional "
      "lighting with indigo accent glows from the monitor. Camera "
      "continues pushing in until the dashboard fills the frame. "
      "Shallow depth of field, bokeh background, cinematic 24fps. "
      "No cuts, continuous motion."
    ),
    "frame_count": 100,
    "aspect_ratio": "16:9",
  },
}


# ── Frame Extraction ──────────────────────────────────────────────────


def check_ffmpeg() -> bool:
  """Verify ffmpeg is available."""
  return shutil.which("ffmpeg") is not None


def get_video_info(video_path: str) -> dict:
  """Get video duration, fps, and resolution via ffprobe."""
  cmd = [
    "ffprobe",
    "-v",
    "quiet",
    "-print_format",
    "json",
    "-show_format",
    "-show_streams",
    video_path,
  ]
  try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    video_stream = next(
      (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
      {},
    )
    duration = float(data.get("format", {}).get("duration", 0))
    fps_str = video_stream.get("r_frame_rate", "30/1")
    num, den = fps_str.split("/")
    fps = float(num) / float(den)
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    return {
      "duration": duration,
      "fps": fps,
      "width": width,
      "height": height,
      "total_frames": int(duration * fps),
    }
  except (subprocess.CalledProcessError, ValueError, StopIteration) as e:
    logger.warning("ffprobe failed: %s", e)
    return {
      "duration": 8.0,
      "fps": 30.0,
      "width": 1920,
      "height": 1080,
      "total_frames": 240,
    }


def extract_frames(
  video_path: str,
  output_dir: str,
  frame_count: int = DEFAULT_FRAME_COUNT,
  fmt: str = "webp",
  quality: int = DEFAULT_QUALITY,
  max_width: int | None = DEFAULT_MAX_WIDTH,
) -> list[str]:
  """Extract evenly-spaced frames from a video for scroll animation.

  Args:
      video_path: Path to the input video file.
      output_dir: Directory to save extracted frames.
      frame_count: Number of frames to extract (evenly distributed).
      fmt: Output format (png, jpg, webp).
      quality: Compression quality (1-100, for jpg/webp).
      max_width: Maximum width to resize frames to (None = original).

  Returns:
      List of paths to extracted frame files.

  """
  if not check_ffmpeg():
    logger.error("ffmpeg not found. Install: brew install ffmpeg")
    return []

  video_path = str(Path(video_path).resolve())
  output_dir = str(Path(output_dir).resolve())
  Path(output_dir).mkdir(parents=True, exist_ok=True)

  info = get_video_info(video_path)
  logger.info(
    "Video: %.1fs @ %.0ffps, %dx%d (%d total frames)",
    info["duration"],
    info["fps"],
    info["width"],
    info["height"],
    info["total_frames"],
  )

  # Calculate the extraction fps to get the desired frame count
  extract_fps = frame_count / info["duration"]
  logger.info("Extracting %d frames (%.2f fps)", frame_count, extract_fps)

  # Build ffmpeg filter chain
  filters = [f"fps={extract_fps}"]

  if max_width and info["width"] > max_width:
    filters.append(f"scale={max_width}:-1")

  vf = ",".join(filters)

  # Format-specific quality args
  quality_args = []
  if fmt == "webp":
    quality_args = ["-quality", str(quality)]
  elif fmt == "jpg":
    quality_args = ["-q:v", str(math.ceil((100 - quality) * 31 / 100))]
  # png is lossless, no quality setting needed

  output_pattern = os.path.join(output_dir, f"frame_%04d.{fmt}")

  cmd = [
    "ffmpeg",
    "-i",
    video_path,
    "-vf",
    vf,
    *quality_args,
    "-y",  # Overwrite existing
    output_pattern,
  ]

  logger.info("Running: %s", " ".join(cmd))
  result = subprocess.run(cmd, capture_output=True, text=True)

  if result.returncode != 0:
    # Auto-fallback: webp encoder may not be compiled in ffmpeg
    if fmt == "webp" and "encoder" in (result.stderr or "").lower():
      logger.warning("webp encoder unavailable, falling back to jpg")
      return extract_frames(
        video_path,
        output_dir,
        frame_count,
        fmt="jpg",
        quality=quality,
        max_width=max_width,
      )
    logger.error(
      "ffmpeg failed: %s", result.stderr[-500:] if result.stderr else "unknown"
    )
    return []

  # Collect output files
  frames = sorted(Path(output_dir).glob(f"frame_*.{fmt}"))
  logger.info("Extracted %d frames to %s", len(frames), output_dir)

  return [str(f) for f in frames]


def generate_scroll_manifest(
  output_dir: str,
  frames: list[str],
  total_scroll_height: int = 5000,
) -> str:
  """Generate a JSON manifest for the scroll animation controller.

  The manifest maps scroll positions to frame indices, enabling
  smooth scroll-synced frame swapping in the browser.
  """
  manifest = {
    "version": 1,
    "generator": "veo_frame_extract",
    "totalFrames": len(frames),
    "scrollHeight": total_scroll_height,
    "pixelsPerFrame": total_scroll_height / max(len(frames), 1),
    "frames": [
      {
        "index": i,
        "filename": Path(f).name,
        "scrollStart": int(i * total_scroll_height / max(len(frames), 1)),
        "scrollEnd": int((i + 1) * total_scroll_height / max(len(frames), 1)),
      }
      for i, f in enumerate(frames)
    ],
  }

  manifest_path = os.path.join(output_dir, "scroll_manifest.json")
  with open(manifest_path, "w") as fh:
    json.dump(manifest, fh, indent=2)

  logger.info("Scroll manifest: %s", manifest_path)
  return manifest_path


def generate_scroll_js(output_dir: str, frames: list[str]) -> str:
  """Generate a minimal vanilla JS scroll controller.

  Drop-in scroll animation: preloads all frames, swaps them
  based on scroll position. No framework dependencies.
  """
  frame_names = [Path(f).name for f in frames]

  js = f"""// Auto-generated scroll animation controller
// Generated by veo_frame_extract.py — Veo 3.1 pipeline
// Replaces Kling 3.0 frame sequence workflow
(function() {{
  'use strict';

  const FRAMES = {json.dumps(frame_names)};
  const FRAME_DIR = './frames/hero/';
  const SCROLL_HEIGHT = 5000; // px of scroll to play entire sequence

  const container = document.getElementById('scroll-animation');
  if (!container) return;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  container.appendChild(canvas);

  // Set container height for scroll
  container.style.height = SCROLL_HEIGHT + 'px';
  container.style.position = 'relative';

  // Fixed canvas overlay
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:sticky;top:0;width:100%;height:100vh;overflow:hidden;';
  container.insertBefore(wrapper, canvas);
  wrapper.appendChild(canvas);

  // Preload all frames
  const images = [];
  let loadedCount = 0;

  function resizeCanvas() {{
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drawFrame(currentFrame);
  }}

  let currentFrame = 0;

  function drawFrame(index) {{
    if (!images[index] || !images[index].complete) return;
    const img = images[index];
    const scale = Math.max(
      canvas.width / img.naturalWidth,
      canvas.height / img.naturalHeight
    );
    const w = img.naturalWidth * scale;
    const h = img.naturalHeight * scale;
    const x = (canvas.width - w) / 2;
    const y = (canvas.height - h) / 2;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, x, y, w, h);
  }}

  function onScroll() {{
    const rect = container.getBoundingClientRect();
    const scrolled = -rect.top;
    const progress = Math.max(0, Math.min(1, scrolled / (SCROLL_HEIGHT - window.innerHeight)));
    const frameIndex = Math.min(
      Math.floor(progress * FRAMES.length),
      FRAMES.length - 1
    );
    if (frameIndex !== currentFrame) {{
      currentFrame = frameIndex;
      drawFrame(currentFrame);
    }}
  }}

  // Preload
  FRAMES.forEach(function(name, i) {{
    const img = new Image();
    img.onload = function() {{
      loadedCount++;
      if (loadedCount === 1) drawFrame(0);
    }};
    img.src = FRAME_DIR + name;
    images[i] = img;
  }});

  window.addEventListener('scroll', onScroll, {{ passive: true }});
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();
}})();
"""

  js_path = os.path.join(output_dir, "scroll_animation.js")
  with open(js_path, "w") as fh:
    fh.write(js)

  logger.info("Scroll JS controller: %s", js_path)
  return js_path


# ── Full Pipeline (Veo + Extract) ─────────────────────────────────────


def run_full_pipeline(
  veo_prompt: str,
  output_dir: str,
  frame_count: int = DEFAULT_FRAME_COUNT,
  veo_image: str | None = None,
  veo_model: str = "veo-3.1-generate-001",
  aspect_ratio: str = "16:9",
  fmt: str = "webp",
  quality: int = DEFAULT_QUALITY,
  max_width: int | None = DEFAULT_MAX_WIDTH,
  output_gcs: str | None = None,
) -> dict:
  """Run the complete Nano Banana 2 → Veo 3.1 → Frames pipeline.

  This replaces the Kling 3.0 step in the original workflow:
    Old: Nano Banana 2 → Kling 3.0 → manual frame extract
    New: Nano Banana 2 → Veo 3.1 → automated frame extract + scroll JS
  """
  # Import Veo generator
  sys.path.insert(0, str(Path(__file__).parent))
  from veo_generate import generate_gemini_api, generate_vertex_ai

  results = {"video": None, "frames": [], "manifest": None, "scroll_js": None}

  # Step 1: Generate video
  logger.info("═" * 60)
  logger.info("  STEP 1: Veo 3.1 Video Generation")
  logger.info("═" * 60)

  if output_gcs:
    video_uri = generate_vertex_ai(
      prompt=veo_prompt,
      output_gcs_uri=output_gcs,
      model=veo_model,
      aspect_ratio=aspect_ratio,
      image_gcs_uri=veo_image if veo_image and veo_image.startswith("gs://") else None,
    )
    if video_uri:
      results["video"] = video_uri
      # Download from GCS for frame extraction
      local_video = _download_gcs(video_uri, output_dir)
    else:
      logger.error("Veo generation failed")
      return results
  else:
    local_video = generate_gemini_api(
      prompt=veo_prompt,
      output_dir=output_dir,
      model=veo_model,
      aspect_ratio=aspect_ratio,
      image_path=veo_image,
    )
    if local_video:
      results["video"] = local_video
    else:
      logger.error("Veo generation failed")
      return results

  if not local_video:
    logger.error("No local video file available for frame extraction")
    return results

  # Step 2: Extract frames
  logger.info("═" * 60)
  logger.info("  STEP 2: Frame Extraction")
  logger.info("═" * 60)

  frames_dir = os.path.join(output_dir, "frames")
  frames = extract_frames(
    video_path=local_video,
    output_dir=frames_dir,
    frame_count=frame_count,
    fmt=fmt,
    quality=quality,
    max_width=max_width,
  )
  results["frames"] = frames

  # Step 3: Generate scroll animation assets
  logger.info("═" * 60)
  logger.info("  STEP 3: Scroll Animation Assets")
  logger.info("═" * 60)

  if frames:
    results["manifest"] = generate_scroll_manifest(frames_dir, frames)
    results["scroll_js"] = generate_scroll_js(frames_dir, frames)

  logger.info("═" * 60)
  logger.info("  PIPELINE COMPLETE")
  logger.info("  Video: %s", results["video"])
  logger.info("  Frames: %d extracted", len(results["frames"]))
  logger.info("  Manifest: %s", results["manifest"])
  logger.info("  Scroll JS: %s", results["scroll_js"])
  logger.info("═" * 60)

  return results


def _download_gcs(gcs_uri: str, output_dir: str) -> str | None:
  """Download a file from GCS to local directory."""
  try:
    local_path = os.path.join(output_dir, Path(gcs_uri).name)
    subprocess.run(
      ["gsutil", "cp", gcs_uri, local_path],
      check=True,
      capture_output=True,
      text=True,
    )
    return local_path
  except (subprocess.CalledProcessError, FileNotFoundError) as e:
    logger.exception("GCS download failed: %s", e)
    return None


# ── CLI ───────────────────────────────────────────────────────────────


def main() -> int:
  parser = argparse.ArgumentParser(
    description=(
      "Extract frames from Veo 3.1 videos for scroll animations.\nReplaces the Kling 3.0 step in the Antigravity + Nano Banana 2 workflow."
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Pipeline (replaces Kling 3.0):
  Old: Nano Banana 2 → Kling 3.0 → manual frame extract → website
  New: Nano Banana 2 → Veo 3.1 → auto frame extract → scroll JS → website

Presets:
  --preset hero_drift           Car drifting out of frame
  --preset product_reveal       SaaS dashboard reveal
  --preset counselconduit_hero  CounselConduit hero scroll

Examples:
  # Extract frames from existing video
  python scripts/veo_frame_extract.py \\
      --input hero_video.mp4 --output public/frames/hero/

  # Full pipeline with preset
  python scripts/veo_frame_extract.py \\
      --preset hero_drift \\
      --veo-image reference/porsche.png \\
      --output public/frames/hero/ \\
      --output-gcs gs://shadowtag-omega-v4-media/demos/

  # Custom prompt pipeline
  python scripts/veo_frame_extract.py \\
      --veo-prompt "A car drifts through smoke..." \\
      --output public/frames/hero/ \\
      --frame-count 120 --format webp --quality 85
        """,
  )

  # Input sources (mutually exclusive)
  input_group = parser.add_mutually_exclusive_group(required=True)
  input_group.add_argument("--input", help="Existing video file to extract frames from")
  input_group.add_argument(
    "--veo-prompt", help="Generate video with Veo 3.1 first, then extract"
  )
  input_group.add_argument(
    "--preset", choices=list(SCROLL_PRESETS), help="Use a preset"
  )

  # Output
  parser.add_argument("--output", required=True, help="Output directory for frames")

  # Frame extraction options
  parser.add_argument(
    "--frame-count",
    type=int,
    default=DEFAULT_FRAME_COUNT,
    help=f"Number of frames to extract (default: {DEFAULT_FRAME_COUNT})",
  )
  parser.add_argument(
    "--format",
    choices=SUPPORTED_FORMATS,
    default="webp",
    help="Output frame format (default: webp)",
  )
  parser.add_argument(
    "--quality",
    type=int,
    default=DEFAULT_QUALITY,
    help=f"Compression quality 1-100 (default: {DEFAULT_QUALITY})",
  )
  parser.add_argument(
    "--max-width",
    type=int,
    default=DEFAULT_MAX_WIDTH,
    help=f"Max frame width in px (default: {DEFAULT_MAX_WIDTH})",
  )

  # Veo options (for pipeline mode)
  parser.add_argument("--veo-image", help="Reference image for Veo image-to-video")
  parser.add_argument(
    "--veo-model",
    default="veo-3.1-generate-001",
    help="Veo model (default: veo-3.1-generate-001)",
  )
  parser.add_argument("--aspect-ratio", default="16:9", choices=("16:9", "9:16"))
  parser.add_argument("--output-gcs", help="GCS URI for Veo output (Vertex AI mode)")

  # Misc
  parser.add_argument(
    "--no-scroll-js", action="store_true", help="Skip generating scroll JS controller"
  )
  parser.add_argument("--list-presets", action="store_true", help="List presets")
  parser.add_argument("-v", "--verbose", action="store_true")

  args = parser.parse_args()

  logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
  )

  if args.list_presets:
    for preset in SCROLL_PRESETS.values():  # noqa: B007
      pass
    return 0

  # Mode 1: Extract from existing video
  if args.input:
    if not Path(args.input).exists():
      return 1

    frames = extract_frames(
      video_path=args.input,
      output_dir=args.output,
      frame_count=args.frame_count,
      fmt=args.format,
      quality=args.quality,
      max_width=args.max_width,
    )

    if frames and not args.no_scroll_js:
      generate_scroll_manifest(args.output, frames)
      generate_scroll_js(args.output, frames)

    if frames:
      return 0
    return 1

  # Mode 2: Full Veo pipeline
  preset = SCROLL_PRESETS.get(args.preset, {})
  prompt = args.veo_prompt or preset.get("veo_prompt")
  frame_count = (
    args.frame_count
    if args.frame_count != DEFAULT_FRAME_COUNT
    else preset.get("frame_count", DEFAULT_FRAME_COUNT)
  )
  aspect = args.aspect_ratio or preset.get("aspect_ratio", "16:9")

  if not prompt:
    return 1

  results = run_full_pipeline(
    veo_prompt=prompt,
    output_dir=args.output,
    frame_count=frame_count,
    veo_image=args.veo_image,
    veo_model=args.veo_model,
    aspect_ratio=aspect,
    fmt=args.format,
    quality=args.quality,
    max_width=args.max_width,
    output_gcs=args.output_gcs,
  )

  if results["frames"]:
    return 0

  return 1


if __name__ == "__main__":
  sys.exit(main())
