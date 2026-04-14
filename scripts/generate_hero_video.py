"""  # noqa: INP001
scripts/generate_hero_video.py

Veo 3.1 Hero Video Generator for ShadowTag AI

Generates high-fidelity background video assets using Google's Veo 3.1 API
(veo-3.1-generate-preview) for the ShadowTag AI hero section.

Workflow:
  1. Generate a reference image via Gemini 3.1 Flash Image (Nano Banana 2)
  2. Feed reference into Veo 3.1 for cinematic video generation
  3. Download the artifact and place it in the public assets directory

Requirements:
  - GEMINI_API_KEY environment variable set
  - google-genai Python SDK installed: pip install google-genai

Usage:
  python scripts/generate_hero_video.py [--prompt "custom prompt"] [--output path/to/output.mp4]
"""

from __future__ import annotations

import argparse
import os
import sys
import time

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai SDK not installed. Run: pip install google-genai")
    sys.exit(1)


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────
SHADOWTAG_COLORS = {
    "bg": "#080c18",
    "primary": "#00ff88",
    "secondary": "#7c3aed",
    "tertiary": "#00d4ff",
    "surface": "#0f131f",
}

DEFAULT_VIDEO_PROMPT = (
    "Cinematic 4K looping background: a dark obsidian void with slowly undulating "
    "liquid mesh gradients. Colors: electric emerald green (#00ff88), deep violet (#7c3aed), "
    "and cyan (#00d4ff) flow organically across the frame like bioluminescent aurora currents. "
    "Subtle particle networks drift upward through the scene. Camera: static wide shot, "
    "no shake, perfectly smooth. The mood is premium B2B technology, sovereign, powerful, "
    "hypnotic. Think: dark luxury fintech dashboard background. 8 seconds, seamless loop. "
    "No text, no faces, no objects — pure abstract kinetic motion."
)

DEFAULT_IMAGE_PROMPT = (
    "Dark obsidian tech background with flowing electric emerald (#00ff88), violet (#7c3aed), "
    "and cyan (#00d4ff) mesh gradients. Premium B2B AI aesthetic. Abstract, no text. "
    "Bioluminescent aurora currents on deep black (#080c18). Ultra high resolution, 16:9."
)

DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "apps", "shadowtagai", "public", "hero-bg-video.mp4"
)

# Image gen model (Nano Banana 2)
IMAGE_MODEL = "gemini-3.1-flash-image-preview"

# Video gen model (Veo 3.1)
VIDEO_MODEL = "veo-3.1-generate-preview"


# ──────────────────────────────────────────────
# Veo 3.1 Video Generation
# ──────────────────────────────────────────────
class Veo31Pipeline:
    """Orchestrates the Nano Banana 2 → Veo 3.1 video generation pipeline."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Export it or pass via --api-key."
            )
        self.client = genai.Client(api_key=self.api_key)

    def generate_reference_image(self, prompt: str, output_path: str = "reference_frame.png") -> str:
        """
        Step 1: Generate a high-quality reference frame using Gemini 3.1 Flash Image
        (Nano Banana 2) via generate_content with IMAGE response modality.
        """
        print(f"🎨 [Step 1/3] Generating reference frame via {IMAGE_MODEL}...")

        response = self.client.models.generate_content(
            model=IMAGE_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                ),
            ),
        )

        # Extract image from response parts
        for part in response.parts:
            if part.inline_data is not None:
                img_bytes = part.inline_data.data
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"   ✅ Reference frame saved: {output_path} ({len(img_bytes)} bytes)")
                return output_path

        raise RuntimeError("Image generation returned no image parts.")

    def generate_video(
        self,
        prompt: str,
        reference_image_path: str | None = None,
        output_path: str = DEFAULT_OUTPUT,
        aspect_ratio: str = "16:9",
    ) -> str:
        """
        Step 2: Generate video via Veo 3.1 API.

        Supports:
          - Text-to-video (prompt only)
          - Image-to-video (first frame anchored to reference image)
        """
        print(f"🎬 [Step 2/3] Submitting video generation to {VIDEO_MODEL}...")

        # Build the request — Veo 3.1 has strict personGeneration rules:
        #   Image-to-video: "allow_adult" ONLY
        #   Text-to-video:  "allow_all" ONLY
        # See: https://ai.google.dev/gemini-api/docs/video#veo-api-parameters
        if reference_image_path and os.path.exists(reference_image_path):
            print(f"   📎 Using reference image: {reference_image_path}")
            with open(reference_image_path, "rb") as f:
                image_bytes = f.read()

            image = types.Image(
                image_bytes=image_bytes,
                mime_type="image/png",
            )
            generate_config = types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=8,
                person_generation="allow_adult",
                resolution="1080p",
            )
            operation = self.client.models.generate_videos(
                model=VIDEO_MODEL,
                prompt=prompt,
                image=image,
                config=generate_config,
            )
        else:
            print("   📝 Text-to-video mode (no reference image)")
            generate_config = types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=8,
                person_generation="allow_all",
                resolution="1080p",
            )
            operation = self.client.models.generate_videos(
                model=VIDEO_MODEL,
                prompt=prompt,
                config=generate_config,
            )

        # Poll for completion
        print("   ⏳ Waiting for video generation (this can take 2-5 minutes)...")
        poll_count = 0
        while not operation.done:
            time.sleep(10)
            poll_count += 1
            operation = self.client.operations.get(operation)
            elapsed = poll_count * 10
            print(f"      ... polling ({elapsed}s elapsed)")

        # Extract result
        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError(
                f"Video generation failed. Operation result: {operation}"
            )

        video = operation.response.generated_videos[0]

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download and save using the SDK's file download + save pattern
        try:
            self.client.files.download(file=video.video)
            video.video.save(output_path)
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"   ✅ Video saved: {output_path} ({size_mb:.1f} MB)")
        except AttributeError:
            # Fallback: direct byte access for older SDK versions
            video_bytes = video.video.video_bytes
            if video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_bytes)
                size_mb = len(video_bytes) / (1024 * 1024)
                print(f"   ✅ Video saved (direct bytes): {output_path} ({size_mb:.1f} MB)")
            else:
                raise RuntimeError("Could not download video bytes from response.")

        return output_path

    def generate_looping_video(
        self,
        prompt: str,
        first_frame_path: str | None = None,
        last_frame_path: str | None = None,
        output_path: str = DEFAULT_OUTPUT,
    ) -> str:
        """
        Generate a seamless looping video by providing both first and last frames.
        Uses Veo 3.1's image interpolation when both frames are provided.
        """
        print("🔄 [Looping Mode] Generating seamless loop with frame anchors...")

        config = types.GenerateVideosConfig(
            aspect_ratio="16:9",
            number_of_videos=1,
            duration_seconds=8,
            person_generation="dont_allow",
        )

        # Load first frame image
        image = None
        last_frame = None
        if first_frame_path and os.path.exists(first_frame_path):
            with open(first_frame_path, "rb") as f:
                image = types.Image(image_bytes=f.read(), mime_type="image/png")
        if last_frame_path and os.path.exists(last_frame_path):
            with open(last_frame_path, "rb") as f:
                last_frame = types.Image(image_bytes=f.read(), mime_type="image/png")

        # Veo 3.1 supports image + lastFrame for interpolation
        kwargs = {
            "model": VIDEO_MODEL,
            "prompt": prompt,
            "config": config,
        }
        if image:
            kwargs["image"] = image
        if last_frame:
            kwargs["last_frame"] = last_frame

        operation = self.client.models.generate_videos(**kwargs)

        print("   ⏳ Awaiting loop generation...")
        while not operation.done:
            time.sleep(10)
            operation = self.client.operations.get(operation)
            print("      ... still processing")

        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError("Loop video generation failed.")

        video = operation.response.generated_videos[0]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            self.client.files.download(file=video.video)
            video.video.save(output_path)
        except AttributeError:
            video_bytes = video.video.video_bytes
            if video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_bytes)

        print(f"   ✅ Looping video saved: {output_path}")
        return output_path

    def run_full_pipeline(
        self,
        video_prompt: str = DEFAULT_VIDEO_PROMPT,
        image_prompt: str = DEFAULT_IMAGE_PROMPT,
        output_path: str = DEFAULT_OUTPUT,
        skip_reference: bool = False,
    ) -> dict:
        """
        Execute the complete Nano Banana 2 → Veo 3.1 pipeline.

        Returns a dict with paths to generated assets.
        """
        print("=" * 60)
        print("  ShadowTag AI — Veo 3.1 Hero Video Pipeline")
        print("=" * 60)

        results = {"reference_image": None, "video": None}

        # Step 1: Generate reference image
        ref_path = None
        if not skip_reference:
            ref_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "apps", "shadowtagai", "public"
            )
            ref_path = os.path.join(ref_dir, "hero-ref-frame.png")
            try:
                self.generate_reference_image(image_prompt, ref_path)
                results["reference_image"] = ref_path
            except Exception as e:
                print(f"   ⚠️  Reference image generation failed: {e}")
                print("   Continuing without reference frame (text-to-video mode)...")
                ref_path = None

        # Step 2: Generate video
        video_path = self.generate_video(
            prompt=video_prompt,
            reference_image_path=ref_path,
            output_path=output_path,
        )
        results["video"] = video_path

        # Step 3: Summary
        print("\n" + "=" * 60)
        print("  ✅ Pipeline Complete")
        print("=" * 60)
        print(f"  Reference Image: {results['reference_image'] or 'skipped'}")
        print(f"  Video Output:    {results['video']}")
        print("\n  Next: Update index.html hero section to use this video.")
        print("  CSS: <video> with object-fit: cover, autoplay, loop, muted, playsinline")
        print("=" * 60)

        return results


# ──────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Generate Veo 3.1 hero background video for ShadowTag AI"
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_VIDEO_PROMPT,
        help="Video generation prompt",
    )
    parser.add_argument(
        "--image-prompt",
        default=DEFAULT_IMAGE_PROMPT,
        help="Reference image generation prompt (Nano Banana 2)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output video file path",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Gemini API key (overrides GEMINI_API_KEY env var)",
    )
    parser.add_argument(
        "--skip-reference",
        action="store_true",
        help="Skip reference image generation (text-to-video only)",
    )
    parser.add_argument(
        "--video-only",
        action="store_true",
        help="Skip image generation and use existing reference if available",
    )

    args = parser.parse_args()

    pipeline = Veo31Pipeline(api_key=args.api_key)

    pipeline.run_full_pipeline(
        video_prompt=args.prompt,
        image_prompt=args.image_prompt,
        output_path=args.output,
        skip_reference=args.skip_reference or args.video_only,
    )


if __name__ == "__main__":
    main()
