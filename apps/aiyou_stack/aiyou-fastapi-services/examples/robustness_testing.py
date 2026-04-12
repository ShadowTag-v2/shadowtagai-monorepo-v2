#!/usr/bin/env python3
"""
Robustness Testing Example

Demonstrates comprehensive robustness testing against various attacks.
"""

from shadowtag_v2 import ShadowTagV2
from shadowtag_v2.config.presets import get_preset
from shadowtag_v2.testing.robustness_tests import RobustnessTests


def test_watermark_survival(
    shadowtag, original_video, original_audio, attacked_video, attacked_audio, test_name
):
    """Test if watermark survives after attack."""

    print(f"\nTesting: {test_name}")
    print("-" * 40)

    try:
        # Extract watermark from attacked content
        verification = shadowtag.verify_content(
            watermarked_video_path=attacked_video,
            watermarked_audio_path=attacked_audio,
            original_video_path=original_video,
            original_audio_path=original_audio,
        )

        if verification["verified"]:
            print("  ✓ SURVIVED")
            print(f"  Layer agreement: {verification['layer_agreement']:.2%}")
            print(f"  Confidence: {verification['confidence']:.2%}")
            return True
        else:
            print("  ✗ FAILED")
            print(f"  Reason: {verification.get('reason', 'Unknown')}")
            return False

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("ShadowTag v2: Robustness Testing Example")
    print("=" * 60)

    # Initialize watermarking system with robust preset
    config = get_preset("robust")
    shadowtag = ShadowTagV2(config)

    print("\nUsing preset: ROBUST")
    print(f"Expected survival: {config['expected_survival']:.0%}")

    # Watermark original content
    print("\n" + "=" * 60)
    print("WATERMARKING ORIGINAL CONTENT")
    print("=" * 60)

    result = shadowtag.watermark_content(
        video_path="input_video.mp4",
        audio_path="input_audio.wav",
        prompt="Robustness test content",
        model_id="test-model",
        params={"seed": 777},
        output_video_path="robust_watermarked.mp4",
        output_audio_path="robust_watermarked.wav",
    )

    print("✓ Watermarking complete")
    watermarked_video = result["watermarked_video"]
    watermarked_audio = result["watermarked_audio"]

    # Initialize robustness tester
    tester = RobustnessTests()

    # Run video attacks
    print("\n" + "=" * 60)
    print("VIDEO ROBUSTNESS TESTS")
    print("=" * 60)

    video_results = {}

    # H.264 compression tests
    print("\nH.264 Compression Tests:")
    for crf in [18, 23, 28, 32]:
        attacked = tester.test_h264_crf(watermarked_video, crf)
        survived = test_watermark_survival(
            shadowtag,
            "input_video.mp4",
            "input_audio.wav",
            attacked,
            watermarked_audio,
            f"H.264 CRF {crf}",
        )
        video_results[f"h264_crf{crf}"] = survived

    # Platform simulation tests
    print("\nPlatform Simulation Tests:")

    # YouTube
    youtube_attacked = tester.test_youtube_simulation(watermarked_video)
    youtube_survived = test_watermark_survival(
        shadowtag,
        "input_video.mp4",
        "input_audio.wav",
        youtube_attacked,
        watermarked_audio,
        "YouTube Simulation",
    )
    video_results["youtube"] = youtube_survived

    # TikTok
    tiktok_attacked = tester.test_tiktok_simulation(watermarked_video)
    tiktok_survived = test_watermark_survival(
        shadowtag,
        "input_video.mp4",
        "input_audio.wav",
        tiktok_attacked,
        watermarked_audio,
        "TikTok Simulation",
    )
    video_results["tiktok"] = tiktok_survived

    # Instagram
    instagram_attacked = tester.test_instagram_simulation(watermarked_video)
    instagram_survived = test_watermark_survival(
        shadowtag,
        "input_video.mp4",
        "input_audio.wav",
        instagram_attacked,
        watermarked_audio,
        "Instagram Simulation",
    )
    video_results["instagram"] = instagram_survived

    # Run audio attacks
    print("\n" + "=" * 60)
    print("AUDIO ROBUSTNESS TESTS")
    print("=" * 60)

    audio_results = {}

    # MP3 tests
    print("\nMP3 Encoding Tests:")
    for bitrate in [128, 192, 320]:
        attacked = tester.test_mp3_encoding(watermarked_audio, bitrate)
        survived = test_watermark_survival(
            shadowtag,
            "input_video.mp4",
            "input_audio.wav",
            watermarked_video,
            attacked,
            f"MP3 {bitrate}k",
        )
        audio_results[f"mp3_{bitrate}k"] = survived

    # AAC tests
    print("\nAAC Encoding Tests:")
    for bitrate in [128, 256]:
        attacked = tester.test_aac_encoding(watermarked_audio, bitrate)
        survived = test_watermark_survival(
            shadowtag,
            "input_video.mp4",
            "input_audio.wav",
            watermarked_video,
            attacked,
            f"AAC {bitrate}k",
        )
        audio_results[f"aac_{bitrate}k"] = survived

    # Results summary
    print("\n" + "=" * 60)
    print("ROBUSTNESS SUMMARY")
    print("=" * 60)

    print("\nVideo Tests:")
    video_survival = sum(video_results.values()) / len(video_results) * 100
    for test, survived in video_results.items():
        status = "✓" if survived else "✗"
        print(f"  {status} {test}")
    print(f"\nVideo survival rate: {video_survival:.1f}%")

    print("\nAudio Tests:")
    audio_survival = sum(audio_results.values()) / len(audio_results) * 100
    for test, survived in audio_results.items():
        status = "✓" if survived else "✗"
        print(f"  {status} {test}")
    print(f"\nAudio survival rate: {audio_survival:.1f}%")

    # Overall survival
    all_results = list(video_results.values()) + list(audio_results.values())
    overall_survival = sum(all_results) / len(all_results) * 100

    print("\n" + "=" * 60)
    print(f"OVERALL SURVIVAL RATE: {overall_survival:.1f}%")
    print("=" * 60)

    if overall_survival >= 90:
        print("\n✓ EXCELLENT: Meets production requirements")
    elif overall_survival >= 80:
        print("\n✓ GOOD: Acceptable for most use cases")
    elif overall_survival >= 70:
        print("\n⚠ ACCEPTABLE: May need parameter tuning")
    else:
        print("\n✗ POOR: Requires significant improvements")


if __name__ == "__main__":
    main()
