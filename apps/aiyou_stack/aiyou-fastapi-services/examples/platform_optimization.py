#!/usr/bin/env python3
"""
Platform Optimization Example

Demonstrates platform-specific watermarking for different social media platforms.
"""

from shadowtag_v2 import ShadowTagV2
from shadowtag_v2.config.presets import get_preset, get_preset_info, list_presets


def watermark_for_platform(platform, video_path, audio_path):
    """Watermark content optimized for specific platform."""

    print(f"\n{'=' * 60}")
    print(f"WATERMARKING FOR: {platform.upper()}")
    print(f"{'=' * 60}")

    # Get platform preset
    config = get_preset(platform)
    info = get_preset_info(platform)

    print("\nPreset Information:")
    print(f"  Description: {info['description']}")
    print(f"  Expected survival: {info['expected_survival']:.0%}")
    print(f"  Video delta: {info['video']['delta']}")
    print(f"  Video alpha: {info['video']['alpha']}")
    print(f"  Video redundancy: {info['video']['redundancy']}")
    print(f"  Audio alpha: {info['audio']['alpha']}")
    print(f"  Audio bands: {info['audio']['bands']}")
    print(f"  Error correction: {info['use_error_correction']}")

    # Initialize watermarking system
    shadowtag = ShadowTagV2(config)

    # Watermark content
    result = shadowtag.watermark_content(
        video_path=video_path,
        audio_path=audio_path,
        prompt=f"AI-generated content for {platform}",
        model_id="stable-diffusion-xl-1.0",
        params={"seed": 12345, "platform": platform},
        output_video_path=f"{platform}_watermarked.mp4",
        output_audio_path=f"{platform}_watermarked.wav",
    )

    print(f"\n✓ {platform.upper()} watermarking complete!")
    print(f"  Output: {result['watermarked_video']}")
    print(f"  Processing time: {result['processing_time']:.2f}s")

    return result


def main():
    print("=" * 60)
    print("ShadowTag v2: Platform Optimization Example")
    print("=" * 60)

    # List all available presets
    print("\nAvailable Platform Presets:")
    presets = list_presets()
    for name, description in presets.items():
        print(f"  • {name}: {description}")

    # Input files (replace with actual paths)
    video_path = "input_video.mp4"
    audio_path = "input_audio.wav"

    # Watermark for different platforms
    platforms = ["youtube", "tiktok", "instagram", "twitter"]

    results = {}
    for platform in platforms:
        try:
            result = watermark_for_platform(platform, video_path, audio_path)
            results[platform] = result
        except Exception as e:
            print(f"\n✗ Error watermarking for {platform}: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"\nWatermarked {len(results)} platforms:")
    for platform, result in results.items():
        print(f"  • {platform}: {result['watermarked_video']} ({result['processing_time']:.1f}s)")

    print("\n✓ Platform optimization complete!")


if __name__ == "__main__":
    main()
