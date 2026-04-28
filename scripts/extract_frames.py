#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""extract_frames.py — Extract frames from video or generate placeholders.

Usage:
    # From a real Veo 3.1 video:
    python extract_frames.py hero.mp4 frames/ --fps 30

    # Generate placeholder gradient frames:
    python extract_frames.py --generate-placeholder frames/ --count 240

    # Generate WebP frames for smaller payload:
    python extract_frames.py hero.mp4 frames/ --format webp --quality 85
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def extract_frames(
    video_path: str,
    output_dir: str,
    fps: int = 30,
    frame_format: str = "png",
    quality: int = 85,
) -> int:
    """Extract frames from a video using ffmpeg.

    Args:
        video_path: Path to the input video file.
        output_dir: Directory to save extracted frames.
        fps: Frames per second to extract.
        frame_format: Output format ('png' or 'webp').
        quality: Quality for WebP (1-100, higher = better).

    Returns:
        Number of frames extracted.

    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_pattern = os.path.join(output_dir, f"frame_%04d.{frame_format}")

    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"fps={fps}",
    ]

    if frame_format == "webp":
        cmd.extend(["-quality", str(quality)])

    cmd.extend(["-y", output_pattern])

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        sys.exit(1)

    return len([f for f in os.listdir(output_dir) if f.startswith("frame_") and f.endswith(f".{frame_format}")])


def generate_placeholder_frames(
    output_dir: str,
    count: int = 240,
    width: int = 1920,
    height: int = 1080,
    frame_format: str = "png",
) -> int:
    """Generate gradient placeholder frames for development.

    Args:
        output_dir: Directory to save generated frames.
        count: Number of frames to generate.
        width: Frame width in pixels.
        height: Frame height in pixels.
        frame_format: Output format ('png' or 'webp').

    Returns:
        Number of frames generated.

    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit(1)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for i in range(count):
        progress = i / max(count - 1, 1)

        img = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(img)

        # Gradient: deep blue → magenta → cyan
        for y in range(height):
            row_progress = y / height
            r = int(10 + 80 * progress + 60 * row_progress)
            g = int(10 + 30 * (1 - progress) + 40 * row_progress)
            b = int(40 + 100 * (1 - progress * 0.5) + 80 * row_progress)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Frame counter
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
            small_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
        except OSError:
            font = ImageFont.load_default()
            small_font = font

        frame_text = f"FRAME {i + 1:04d}/{count}"
        draw.text((width // 2 - 120, height // 2 - 20), frame_text, fill=(255, 255, 255, 180), font=font)

        # Progress bar
        bar_width = int(width * 0.6)
        bar_x = (width - bar_width) // 2
        bar_y = height // 2 + 40
        draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, bar_y + 8)], fill=(40, 40, 60))
        draw.rectangle([(bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + 8)], fill=(100, 200, 255))

        # Metadata
        meta = f"Placeholder • {width}×{height} • {frame_format.upper()}"
        draw.text((bar_x, bar_y + 20), meta, fill=(120, 120, 140), font=small_font)

        # Save
        filename = os.path.join(output_dir, f"frame_{i + 1:04d}.{frame_format}")
        save_kwargs = {}
        if frame_format == "webp":
            save_kwargs["quality"] = 85
        img.save(filename, **save_kwargs)

        if (i + 1) % 50 == 0 or i == 0:
            pass

    return count


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Extract video frames or generate placeholders for cinematic scroll.")
    parser.add_argument("video", nargs="?", help="Input video file path")
    parser.add_argument("output_dir", nargs="?", default="frames", help="Output directory")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")
    parser.add_argument("--format", choices=["png", "webp"], default="png", help="Frame format")
    parser.add_argument("--quality", type=int, default=85, help="WebP quality (1-100)")
    parser.add_argument("--generate-placeholder", action="store_true", help="Generate placeholder frames")
    parser.add_argument("--count", type=int, default=240, help="Number of placeholder frames")
    parser.add_argument("--width", type=int, default=1920, help="Frame width")
    parser.add_argument("--height", type=int, default=1080, help="Frame height")

    args = parser.parse_args()

    if args.generate_placeholder:
        output_dir = args.video or args.output_dir
        generate_placeholder_frames(
            output_dir=output_dir,
            count=args.count,
            width=args.width,
            height=args.height,
            frame_format=args.format,
        )
    elif args.video:
        extract_frames(
            video_path=args.video,
            output_dir=args.output_dir,
            fps=args.fps,
            frame_format=args.format,
            quality=args.quality,
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
