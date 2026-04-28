#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Basic Watermarking Example

Demonstrates basic watermarking and verification workflow.
"""

from shadowtag_v2 import ShadowTagV2
from shadowtag_v2.config.presets import get_preset


def main():
    print("=" * 60)
    print("ShadowTag v2: Basic Watermarking Example")
    print("=" * 60)

    # Load YouTube preset (optimized for high quality)
    config = get_preset("youtube")
    print("\nUsing preset: youtube")
    print(f"Expected survival rate: {config['expected_survival']:.0%}")

    # Initialize watermarking system
    shadowtag = ShadowTagV2(config)
    print("\n✓ ShadowTag v2 initialized")

    # Define AI generation metadata
    prompt = "A serene sunset over snow-capped mountains with golden light"
    model_id = "stable-diffusion-xl-1.0"
    params = {"seed": 42, "steps": 50, "cfg_scale": 7.5, "sampler": "DPM++ 2M Karras"}

    print("\nAI Generation Metadata:")
    print(f"  Prompt: {prompt[:50]}...")
    print(f"  Model: {model_id}")
    print(f"  Params: {params}")

    # Watermark content
    print("\n" + "=" * 60)
    print("WATERMARKING CONTENT")
    print("=" * 60)

    result = shadowtag.watermark_content(
        video_path="input_video.mp4",
        audio_path="input_audio.wav",
        prompt=prompt,
        model_id=model_id,
        params=params,
        output_video_path="watermarked_video.mp4",
        output_audio_path="watermarked_audio.wav",
    )

    print("\n✓ Watermarking complete!")
    print(f"  Video: {result['watermarked_video']}")
    print(f"  Audio: {result['watermarked_audio']}")
    print(f"  Watermark hash: {result['watermark_hash'][:32]}...")
    print(f"  Processing time: {result['processing_time']:.2f}s")

    # Verify watermarked content
    print("\n" + "=" * 60)
    print("VERIFYING WATERMARKED CONTENT")
    print("=" * 60)

    verification = shadowtag.verify_content(
        watermarked_video_path="watermarked_video.mp4",
        watermarked_audio_path="watermarked_audio.wav",
        original_video_path="input_video.mp4",
        original_audio_path="input_audio.wav",
        expected_metadata=result["metadata"],
    )

    print("\n✓ Verification complete!")
    print(f"  Verified: {verification['verified']}")
    print(f"  Layer agreement: {verification['layer_agreement']:.2%}")
    print(f"  Confidence: {verification['confidence']:.2%}")
    print(f"  Blockchain verified: {verification['blockchain_verified']}")

    # Display extracted payload information
    payload_info = verification["payload_info"]
    print("\nExtracted Payload:")
    print(f"  Content hash: {payload_info['content_hash'][:16]}...")
    print(f"  Timestamp: {payload_info['timestamp']}")
    print(f"  Version: {payload_info['version']}")

    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)


if __name__ == "__main__":
    main()
