#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Vertex AI Veo Configuration — High-Resolution (1080p) Backend.

Configures Vertex AI backend for Veo operations requiring higher
resolution (1080p) or enterprise SLA features not available in the
Gemini Developer API.

Task #6

Usage:
    python scripts/vertex_veo_config.py --list-models
    python scripts/vertex_veo_config.py --generate --preset hero_drift --resolution 1080p
"""

from __future__ import annotations

import argparse
import sys

# Vertex AI model mappings (Veo via Vertex uses different model names)
VERTEX_VEO_MODELS = {
    "veo-3.1": {
        "vertex_model": "google/veo-3.1",
        "endpoint": "us-central1-aiplatform.googleapis.com",
        "max_resolution": "1080p",
        "max_duration": "8s",
        "pricing": "$0.35/sec",
    },
    "veo-3.1-fast": {
        "vertex_model": "google/veo-3.1-fast",
        "endpoint": "us-central1-aiplatform.googleapis.com",
        "max_resolution": "720p",
        "max_duration": "8s",
        "pricing": "$0.10/sec",
    },
    "veo-3.0": {
        "vertex_model": "google/veo-3.0",
        "endpoint": "us-central1-aiplatform.googleapis.com",
        "max_resolution": "1080p",
        "max_duration": "8s",
        "pricing": "$0.30/sec",
    },
    "veo-2.0": {
        "vertex_model": "google/veo-2.0-generate-001",
        "endpoint": "us-central1-aiplatform.googleapis.com",
        "max_resolution": "1080p",
        "max_duration": "8s",
        "pricing": "$0.35/sec",
    },
}

GCS_OUTPUT_URI = "gs://shadowtag-omega-v4-media/veo-output/vertex/"


def list_models() -> None:
    """Print available Vertex AI Veo models."""
    for _name, _config in VERTEX_VEO_MODELS.items():
        pass


def generate_vertex_request(preset: str, resolution: str) -> dict:
    """Generate a Vertex AI Veo generation request payload."""
    model = "veo-3.1" if resolution == "1080p" else "veo-3.1-fast"
    vertex_config = VERTEX_VEO_MODELS[model]

    # Import preset from main pipeline
    sys.path.insert(0, ".")
    from scripts.veo_pipeline import PRESETS

    if preset not in PRESETS:
        sys.exit(1)

    preset_config = PRESETS[preset]

    return {
        "model": vertex_config["vertex_model"],
        "endpoint": vertex_config["endpoint"],
        "project": "shadowtag-omega-v4",
        "location": "us-central1",
        "parameters": {
            "prompt": preset_config.get("prompt", ""),
            "aspect_ratio": preset_config.get("aspect_ratio", "16:9"),
            "number_of_videos": 1,
            "output_gcs_uri": f"{GCS_OUTPUT_URI}{preset}/",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Vertex AI Veo Configuration")
    parser.add_argument("--list-models", action="store_true", help="List Vertex AI Veo models")
    parser.add_argument("--generate", action="store_true", help="Generate Vertex API request")
    parser.add_argument("--preset", default="hero_drift", help="Preset name")
    parser.add_argument("--resolution", default="1080p", choices=["720p", "1080p"], help="Output resolution")
    args = parser.parse_args()

    if args.list_models:
        list_models()
    elif args.generate:
        generate_vertex_request(args.preset, args.resolution)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
