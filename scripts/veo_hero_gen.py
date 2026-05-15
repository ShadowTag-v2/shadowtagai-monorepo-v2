#!/usr/bin/env python3
"""veo_hero_gen.py — Veo 3.1 Hero Video Generation Configuration
══════════════════════════════════════════════════════════════
Configures a Cloud Run Job to generate hero background videos
using the Veo 3.1 API for both ShadowTagAI and KovelAI sites.

Usage:
  # Deploy as Cloud Run Job
  gcloud run jobs create veo-hero-gen \
    --source=. \
    --project=shadowtag-omega-v4 \
    --region=us-central1 \
    --set-env-vars="GEMINI_API_KEY=<key>" \
    --memory=512Mi \
    --task-timeout=600s

  # Execute manually
  gcloud run jobs execute veo-hero-gen --project=shadowtag-omega-v4

  # Schedule via Cloud Scheduler (monthly regeneration)
  gcloud scheduler jobs create http veo-hero-monthly \
    --schedule="0 4 1 * *" \
    --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/..." \
    --oauth-service-account-email="shadowtag-omega-v4@appspot.gserviceaccount.com" \
    --project=shadowtag-omega-v4 --location=us-central1
"""

from dataclasses import dataclass


@dataclass
class VeoHeroConfig:
  """Configuration for Veo 3.1 hero video generation."""

  # Model
  model: str = "veo-3.1"

  # Video parameters
  duration_seconds: int = 8
  resolution: str = "4k"  # 3840x2160
  fps: int = 30
  aspect_ratio: str = "16:9"

  # Output
  output_format: str = "mp4"
  codec: str = "h264"

  # GCS output paths
  gcs_bucket: str = "shadowtag-omega-v4-hero-videos"

  def get_sites(self) -> list[dict]:
    """Return site-specific generation configs."""
    return [
      {
        "site": "shadowtagai",
        "prompt": (
          "Cinematic aerial establishing shot of a futuristic research campus "
          "at twilight, bioluminescent pathways connecting glass-walled labs, "
          "holographic data visualizations floating in the air, deep navy and "
          "electric blue color palette, volumetric fog, camera slowly dollying "
          "forward through the scene, photorealistic, 8K quality"
        ),
        "output_path": f"gs://{self.gcs_bucket}/shadowtagai/hero-bg.mp4",
        "negative_prompt": "text, watermark, logo, people close-up, cartoon, anime",
      },
      {
        "site": "kovelai",
        "prompt": (
          "Elegant abstract visualization of flowing golden data streams through "
          "a dark obsidian void, particles coalescing into legal document "
          "silhouettes then dissolving, warm amber and champagne gold tones, "
          "cinematic depth of field, slow orbital camera movement, premium "
          "luxury aesthetic, photorealistic 8K"
        ),
        "output_path": f"gs://{self.gcs_bucket}/kovelai/hero-bg.mp4",
        "negative_prompt": "text, watermark, logo, cartoon, low quality, blurry",
      },
    ]

  def to_api_request(self, site_config: dict) -> dict:
    """Build the Veo 3.1 API request payload."""
    return {
      "model": f"models/{self.model}",
      "generate_video_config": {
        "prompt": site_config["prompt"],
        "negative_prompt": site_config.get("negative_prompt", ""),
        "duration_seconds": self.duration_seconds,
        "resolution": self.resolution,
        "fps": self.fps,
        "aspect_ratio": self.aspect_ratio,
        "output_format": self.output_format,
      },
      "output_config": {
        "gcs_uri": site_config["output_path"],
      },
    }


def main() -> None:
  """Print generation configs for verification."""
  config = VeoHeroConfig()
  sites = config.get_sites()

  for site in sites:
    config.to_api_request(site)


if __name__ == "__main__":
  main()
