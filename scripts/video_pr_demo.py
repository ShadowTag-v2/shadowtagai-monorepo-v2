#!/usr/bin/env python3
"""Video PR Demo Generator — Concatenates Veo clips into a PR demo reel.

Combines multiple Veo-generated video clips into a single demo reel
suitable for GitHub PR descriptions and product demos.

Usage:
    python scripts/video_pr_demo.py --output demo_reel.mp4
    python scripts/video_pr_demo.py --clips hero_drift counselconduit_hero --output custom.mp4

Task #16
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import tempfile

VEO_DIR = pathlib.Path("labs/uphillsnowball/external_payloads/veo_output")
OUTPUT_DIR = pathlib.Path("public/demos")

DEFAULT_CLIPS = [
  "hero_drift_0",
  "counselconduit_hero_0",
  "onboarding_flow_0",
  "billing_explainer_0",
  "stripe_webhook_0",
  "shadowtagai_marketing_0",
]


def find_ffmpeg() -> str:
  """Locate ffmpeg binary."""
  for path in ["/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg", "ffmpeg"]:
    try:
      subprocess.run([path, "-version"], capture_output=True, check=True)
      return path
    except FileNotFoundError, subprocess.CalledProcessError:
      continue
  sys.exit(1)


def create_concat_file(clips: list[str], tmp_dir: pathlib.Path) -> pathlib.Path:
  """Create an ffmpeg concat demuxer file."""
  concat_path = tmp_dir / "concat.txt"
  with concat_path.open("w") as f:
    for clip_name in clips:
      clip_path = VEO_DIR / f"{clip_name}.mp4"
      if not clip_path.exists():
        continue
      f.write(f"file '{clip_path.resolve()}'\n")
  return concat_path


def concatenate_videos(
  ffmpeg: str,
  concat_file: pathlib.Path,
  output: pathlib.Path,
) -> None:
  """Concatenate videos using ffmpeg concat demuxer."""
  output.parent.mkdir(parents=True, exist_ok=True)
  cmd = [
    ffmpeg,
    "-y",
    "-f",
    "concat",
    "-safe",
    "0",
    "-i",
    str(concat_file),
    "-c",
    "copy",
    str(output),
  ]
  result = subprocess.run(cmd, capture_output=True, text=True)
  if result.returncode != 0:
    sys.exit(1)
  output.stat().st_size / (1024 * 1024)


def main() -> None:
  parser = argparse.ArgumentParser(description="Create Video PR demo reel")
  parser.add_argument("--clips", nargs="+", default=DEFAULT_CLIPS, help="Clip names")
  parser.add_argument("--output", default="demo_reel.mp4", help="Output filename")
  args = parser.parse_args()

  ffmpeg = find_ffmpeg()
  output_path = OUTPUT_DIR / args.output

  with tempfile.TemporaryDirectory() as tmp_dir:
    concat_file = create_concat_file(args.clips, pathlib.Path(tmp_dir))
    concatenate_videos(ffmpeg, concat_file, output_path)


if __name__ == "__main__":
  main()
