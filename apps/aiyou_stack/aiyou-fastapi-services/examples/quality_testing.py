#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Quality Testing Example

Demonstrates comprehensive quality evaluation of watermarked content.
"""

from shadowtag_v2 import ShadowTagV2
from shadowtag_v2.config.presets import get_preset
from shadowtag_v2.testing.quality_metrics import (
    evaluate_audio_quality,
    evaluate_video_quality,
    evaluate_watermark_robustness,
)


def main():
    print("=" * 60)
    print("ShadowTag v2: Quality Testing Example")
    print("=" * 60)

    # Initialize watermarking system
    config = get_preset("balanced")
    shadowtag = ShadowTagV2(config)

    # Watermark content
    print("\nWatermarking content...")
    shadowtag.watermark_content(
        video_path="input_video.mp4",
        audio_path="input_audio.wav",
        prompt="Quality test content",
        model_id="test-model",
        params={"seed": 999},
        output_video_path="watermarked_test.mp4",
        output_audio_path="watermarked_test.wav",
    )

    print("✓ Watermarking complete")

    # Evaluate video quality
    print("\n" + "=" * 60)
    print("VIDEO QUALITY METRICS")
    print("=" * 60)

    video_quality = evaluate_video_quality(
        original_path="input_video.mp4",
        watermarked_path="watermarked_test.mp4",
        num_frames=30,
    )

    print("\nPSNR (Peak Signal-to-Noise Ratio):")
    print(f"  Mean: {video_quality['psnr_mean']:.2f} dB")
    print(f"  Std:  {video_quality['psnr_std']:.2f} dB")
    print(f"  Status: {'✓ Excellent' if video_quality['psnr_mean'] >= 40 else '⚠ Good'}")

    print("\nSSIM (Structural Similarity Index):")
    print(f"  Mean: {video_quality['ssim_mean']:.4f}")
    print(f"  Std:  {video_quality['ssim_std']:.4f}")
    print(f"  Status: {'✓ Excellent' if video_quality['ssim_mean'] >= 0.95 else '⚠ Good'}")

    print(f"\nOverall Grade: {video_quality['quality_grade'].upper()}")

    # Evaluate audio quality
    print("\n" + "=" * 60)
    print("AUDIO QUALITY METRICS")
    print("=" * 60)

    audio_quality = evaluate_audio_quality(
        original_path="input_audio.wav",
        watermarked_path="watermarked_test.wav",
    )

    print("\nSNR (Signal-to-Noise Ratio):")
    print(f"  Value: {audio_quality['snr']:.2f} dB")
    print(f"  Status: {'✓ Excellent' if audio_quality['snr'] >= 35 else '⚠ Good'}")

    print(f"\nOverall Grade: {audio_quality['quality_grade'].upper()}")
    print(f"Duration: {audio_quality['duration']:.2f}s")

    # Evaluate watermark robustness
    print("\n" + "=" * 60)
    print("WATERMARK ROBUSTNESS")
    print("=" * 60)

    # Extract watermark
    verification = shadowtag.verify_content(
        watermarked_video_path="watermarked_test.mp4",
        watermarked_audio_path="watermarked_test.wav",
        original_video_path="input_video.mp4",
        original_audio_path="input_audio.wav",
    )

    # Generate original watermark bits for comparison
    from shadowtag_v2.security.crypto_payload import generate_watermark_payload

    original_bits, _ = generate_watermark_payload(
        prompt="Quality test content",
        model_id="test-model",
        params={"seed": 999},
    )

    extracted_bits = verification["video_bits"]

    robustness = evaluate_watermark_robustness(
        original_bits=original_bits,
        extracted_bits=extracted_bits,
    )

    print("\nBit Error Rate (BER):")
    print(f"  Value: {robustness['ber']:.2%}")
    print(f"  Accuracy: {robustness['accuracy']:.2%}")
    print(f"  Errors: {robustness['num_errors']} / {robustness['total_bits']} bits")
    print(f"  Status: {'✓ Excellent' if robustness['ber'] <= 0.02 else '⚠ Good'}")

    print(f"\nOverall Grade: {robustness['robustness_grade'].upper()}")

    # Final summary
    print("\n" + "=" * 60)
    print("QUALITY SUMMARY")
    print("=" * 60)

    print(f"\nVideo Quality:     {video_quality['quality_grade'].upper()}")
    print(f"Audio Quality:     {audio_quality['quality_grade'].upper()}")
    print(f"Watermark Robust:  {robustness['robustness_grade'].upper()}")

    # Overall pass/fail
    all_excellent = (
        video_quality["quality_grade"] in ["excellent", "good"]
        and audio_quality["quality_grade"] in ["excellent", "good"]
        and robustness["robustness_grade"] in ["excellent", "good"]
    )

    if all_excellent:
        print("\n✓ PASSED: All quality metrics meet requirements")
    else:
        print("\n⚠ WARNING: Some quality metrics below target")


if __name__ == "__main__":
    main()
