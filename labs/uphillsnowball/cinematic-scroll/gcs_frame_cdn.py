#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""gcs_frame_cdn.py — GCS-backed Frame CDN with Signed URLs.

Generates signed URLs for frame sequences stored in GCS,
enabling CDN-grade delivery with immutable caching.

Usage:
    python gcs_frame_cdn.py --bucket shadowtag-omega-v4-media \
        --prefix cinematic-scroll/frames \
        --count 240 \
        --output manifest.json
"""

import argparse
import datetime
import json
import logging
import os

from google.cloud import storage as gcs_storage


def generate_frame_manifest(
    bucket_name: str,
    prefix: str,
    frame_count: int = 240,
    frame_format: str = "png",
    expiration_hours: int = 168,  # 7 days
    output_path: str | None = None,
) -> dict:
    """Generate a manifest of signed URLs for a frame sequence.

    Args:
        bucket_name: GCS bucket name.
        prefix: GCS path prefix for frames.
        frame_count: Number of frames.
        frame_format: Frame file format.
        expiration_hours: Signed URL expiration in hours.
        output_path: Optional path to write manifest JSON.

    Returns:
        Dict with manifest data.
    """
    client = gcs_storage.Client()
    bucket = client.bucket(bucket_name)

    frames = []
    expiration = datetime.timedelta(hours=expiration_hours)

    for i in range(frame_count):
        blob_name = f"{prefix}/frame_{i + 1:04d}.{frame_format}"
        blob = bucket.blob(blob_name)

        if blob.exists():
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method="GET",
            )
            frames.append(
                {
                    "index": i + 1,
                    "blob": blob_name,
                    "url": signed_url,
                    "size_bytes": blob.size,
                }
            )
        else:
            frames.append(
                {
                    "index": i + 1,
                    "blob": blob_name,
                    "url": None,
                    "exists": False,
                }
            )

    manifest = {
        "bucket": bucket_name,
        "prefix": prefix,
        "frame_count": frame_count,
        "frame_format": frame_format,
        "available_frames": sum(1 for f in frames if f.get("url")),
        "expiration_hours": expiration_hours,
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "frames": frames,
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)
        logging.info(f"Manifest written to: {output_path}")

    return manifest


def upload_frames_to_gcs(
    local_dir: str,
    bucket_name: str,
    prefix: str,
    frame_format: str = "png",
    content_type: str | None = None,
) -> int:
    """Upload local frame directory to GCS.

    Args:
        local_dir: Local directory containing frames.
        bucket_name: Target GCS bucket.
        prefix: GCS path prefix.
        frame_format: Frame file format to filter.
        content_type: Override content type.

    Returns:
        Number of frames uploaded.
    """
    client = gcs_storage.Client()
    bucket = client.bucket(bucket_name)
    uploaded = 0

    mime = content_type or f"image/{frame_format}"
    if frame_format == "webp":
        mime = "image/webp"

    for filename in sorted(os.listdir(local_dir)):
        if not filename.startswith("frame_") or not filename.endswith(f".{frame_format}"):
            continue

        local_path = os.path.join(local_dir, filename)
        blob_name = f"{prefix}/{filename}"
        blob = bucket.blob(blob_name)

        blob.upload_from_filename(local_path, content_type=mime)
        blob.cache_control = "public, max-age=2592000, immutable"
        blob.patch()

        uploaded += 1
        if uploaded % 50 == 0:
            logging.info(f"Uploaded {uploaded} frames...")

    logging.info(f"Uploaded {uploaded} frames to gs://{bucket_name}/{prefix}/")
    return uploaded


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="GCS Frame CDN Manager")
    sub = parser.add_subparsers(dest="command")

    # Generate manifest
    manifest_cmd = sub.add_parser("manifest", help="Generate signed URL manifest")
    manifest_cmd.add_argument("--bucket", default="shadowtag-omega-v4-media")
    manifest_cmd.add_argument("--prefix", default="cinematic-scroll/frames")
    manifest_cmd.add_argument("--count", type=int, default=240)
    manifest_cmd.add_argument("--format", default="png")
    manifest_cmd.add_argument("--output", default="frame_manifest.json")

    # Upload frames
    upload_cmd = sub.add_parser("upload", help="Upload frames to GCS")
    upload_cmd.add_argument("local_dir", help="Local frames directory")
    upload_cmd.add_argument("--bucket", default="shadowtag-omega-v4-media")
    upload_cmd.add_argument("--prefix", default="cinematic-scroll/frames")
    upload_cmd.add_argument("--format", default="png")

    args = parser.parse_args()

    if args.command == "manifest":
        manifest = generate_frame_manifest(
            bucket_name=args.bucket,
            prefix=args.prefix,
            frame_count=args.count,
            frame_format=args.format,
            output_path=args.output,
        )
        print(f"Manifest: {manifest['available_frames']}/{manifest['frame_count']} frames available")
    elif args.command == "upload":
        count = upload_frames_to_gcs(
            local_dir=args.local_dir,
            bucket_name=args.bucket,
            prefix=args.prefix,
            frame_format=args.format,
        )
        print(f"Uploaded {count} frames")
    else:
        parser.print_help()
