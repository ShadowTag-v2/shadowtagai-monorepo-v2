#!/usr/bin/env python3
"""extract_frames.py — Veo 3.1 video → frame sequence extractor.

Usage:
    python extract_frames.py <video_path> [--output-dir frames/] [--format png] [--fps 30]

Extracts individual frames from a Veo 3.1 generated video for use in
scroll-driven cinematic websites. Canvas-rendered frame sequences are
smoother than direct video playback on scroll.

Pipeline: Nano Banana 2 (image) → Veo 3.1 (video) → ffmpeg (frames) → scroll-engine.js
"""

import argparse
import subprocess
import sys
from pathlib import Path


def extract_frames(
    video_path: str,
    output_dir: str = "frames",
    fmt: str = "png",
    fps: int = 30,
) -> int:
    """Extract frames from a video file using ffmpeg.

    Args:
        video_path: Path to input video file.
        output_dir: Directory to write frame images.
        fmt: Output image format (png, webp, jpg).
        fps: Frames per second to extract.

    Returns:
        Number of frames extracted.
    """
    video = Path(video_path)
    if not video.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Validate ffmpeg is available
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install with: brew install ffmpeg", file=sys.stderr)
        sys.exit(1)

    # Build ffmpeg command
    output_pattern = str(out / f"frame_%04d.{fmt}")

    cmd = [
        "ffmpeg",
        "-i", str(video),
        "-vf", f"fps={fps}",
        "-q:v", "2",  # High quality
        output_pattern,
        "-y",  # Overwrite
    ]

    # Add format-specific flags
    if fmt == "webp":
        cmd = [
            "ffmpeg",
            "-i", str(video),
            "-vf", f"fps={fps}",
            "-c:v", "libwebp",
            "-quality", "90",
            "-compression_level", "4",
            output_pattern,
            "-y",
        ]

    print(f"Extracting frames: {video.name} → {output_dir}/")
    print(f"Format: {fmt}, FPS: {fps}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ffmpeg error:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Count extracted frames
    frame_count = len(list(out.glob(f"frame_*.{fmt}")))
    print(f"Extracted {frame_count} frames to {output_dir}/")

    return frame_count


def generate_placeholder_frames(
    output_dir: str = "frames",
    frame_count: int = 240,
    width: int = 1920,
    height: int = 1080,
    fmt: str = "png",
) -> int:
    """Generate gradient placeholder frames for scroll engine testing.

    Creates a sequence of frames with animated gradient backgrounds
    so the scroll engine can be tested without a real Veo video.

    Args:
        output_dir: Directory to write frame images.
        frame_count: Number of frames to generate.
        width: Frame width in pixels.
        height: Frame height in pixels.
        fmt: Output image format.

    Returns:
        Number of frames generated.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Error: Pillow is required for placeholder generation.", file=sys.stderr)
        print("Install with: pip install Pillow", file=sys.stderr)
        sys.exit(1)

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Generating {frame_count} placeholder frames ({width}×{height})...")

    for i in range(frame_count):
        progress = i / max(frame_count - 1, 1)

        # Animated gradient: hue shifts from deep blue → purple → magenta
        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        for y in range(height):
            row_progress = y / height
            # Mix two color stops based on frame progress
            r = int(20 + 80 * progress + 60 * row_progress)
            g = int(10 + 20 * (1 - progress) * row_progress)
            b = int(80 + 120 * (1 - progress) + 40 * row_progress)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Add frame counter text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
        except (OSError, IOError):
            font = ImageFont.load_default()

        text = f"Frame {i + 1:04d}/{frame_count}"
        draw.text((width // 2 - 150, height // 2 - 30), text, fill=(255, 255, 255, 200), font=font)

        # Progress bar at bottom
        bar_y = height - 20
        bar_width = int(width * progress)
        draw.rectangle([(0, bar_y - 4), (bar_width, bar_y)], fill=(100, 200, 255))

        filename = out / f"frame_{i + 1:04d}.{fmt}"
        img.save(str(filename))

        if (i + 1) % 60 == 0 or i == 0:
            print(f"  Generated {i + 1}/{frame_count} frames")

    print(f"✓ Generated {frame_count} placeholder frames to {output_dir}/")
    return frame_count


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract frames from Veo 3.1 video for scroll-driven websites",
    )
    parser.add_argument("video", nargs="?", help="Path to input video file")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output directory (positional alt for --output-dir)",
    )
    parser.add_argument(
        "--output-dir",
        default="frames",
        help="Output directory for frames (default: frames/)",
    )
    parser.add_argument(
        "--format",
        choices=["png", "webp", "jpg"],
        default="png",
        help="Output image format (default: png)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second to extract (default: 30)",
    )
    parser.add_argument(
        "--generate-placeholder",
        action="store_true",
        help="Generate gradient placeholder frames (no video needed)",
    )
    parser.add_argument(
        "--frame-count",
        type=int,
        default=240,
        help="Number of placeholder frames to generate (default: 240)",
    )

    args = parser.parse_args()

    # Resolve output directory: positional > --output-dir > default
    output_dir = args.output if args.output else args.output_dir

    if args.generate_placeholder:
        generate_placeholder_frames(output_dir, args.frame_count, fmt=args.format)
    elif args.video:
        extract_frames(args.video, output_dir, args.format, args.fps)
    else:
        parser.error("Provide a video file or use --generate-placeholder")


if __name__ == "__main__":
    main()
