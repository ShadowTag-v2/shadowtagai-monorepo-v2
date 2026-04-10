"""Tests for video_stego module."""

from pathlib import Path

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from shadowtag_v2.video_stego import (
    VideoWatermarkConfig,
    bits_to_bytes,
    bytes_to_bits,
    embed_frame,
    embed_video_watermark,
    extract_frame,
    extract_video_watermark,
    prompt_hash,
)


class TestPromptHash:
    """Tests for prompt_hash function."""

    def test_deterministic(self):
        """Hash should be deterministic."""
        prompt = "test prompt"
        hash1 = prompt_hash(prompt)
        hash2 = prompt_hash(prompt)
        assert hash1 == hash2

    def test_different_prompts(self):
        """Different prompts should produce different hashes."""
        hash1 = prompt_hash("prompt A")
        hash2 = prompt_hash("prompt B")
        assert hash1 != hash2

    def test_hash_length(self):
        """Hash should be 128 bits (16 bytes) by default."""
        h = prompt_hash("test")
        assert len(h) == 16

    def test_custom_bits(self):
        """Should support custom bit lengths."""
        h64 = prompt_hash("test", bits=64)
        h256 = prompt_hash("test", bits=256)
        assert len(h64) == 8
        assert len(h256) == 32

    def test_invalid_bits(self):
        """Should reject non-multiple-of-8 bit lengths."""
        with pytest.raises(ValueError, match="must be multiple of 8"):
            prompt_hash("test", bits=100)

    @given(st.text(min_size=1, max_size=100))
    def test_property_hash_length(self, prompt: str):
        """Property test: all hashes should be 16 bytes."""
        h = prompt_hash(prompt)
        assert len(h) == 16


class TestBitsConversion:
    """Tests for bits/bytes conversion."""

    def test_bytes_to_bits(self):
        """Should convert bytes to bit array."""
        b = b"\xff\x00"
        bits = bytes_to_bits(b)
        expected = np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        np.testing.assert_array_equal(bits, expected)

    def test_bits_to_bytes(self):
        """Should convert bit array to bytes."""
        bits = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.uint8)
        b = bits_to_bytes(bits)
        assert b == b"\xaa"

    def test_roundtrip(self):
        """Bytes -> bits -> bytes should be identity."""
        original = b"Hello, World!"
        bits = bytes_to_bits(original)
        recovered = bits_to_bytes(bits)
        assert recovered == original

    def test_padding(self):
        """Should pad bits to multiple of 8."""
        bits = np.array([1, 0, 1], dtype=np.uint8)
        b = bits_to_bytes(bits)
        # Should pad with 5 zeros: [1,0,1,0,0,0,0,0] = 0xa0
        assert b == b"\xa0"


class TestFrameWatermarking:
    """Tests for frame-level watermarking."""

    def test_embed_extract_frame(self):
        """Should embed and extract bits from frame."""
        # Create test frame
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        config = VideoWatermarkConfig()

        # Create test bits
        test_bytes = b"Test"
        bits = bytes_to_bits(test_bytes)

        # Embed
        watermarked = embed_frame(frame, bits, config)
        assert watermarked.shape == frame.shape

        # Extract
        extracted = extract_frame(watermarked, len(bits), config)
        assert len(extracted) == len(bits)

        # Should have low bit error rate
        ber = np.sum(bits != extracted) / len(bits)
        assert ber < 0.1  # Allow 10% error

    def test_frame_similarity(self):
        """Watermarked frame should be visually similar to original."""
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        config = VideoWatermarkConfig()

        bits = bytes_to_bits(b"X" * 16)
        watermarked = embed_frame(frame, bits, config)

        # MSE should be small
        mse = np.mean((frame.astype(float) - watermarked.astype(float)) ** 2)
        assert mse < 5.0  # Very small changes


class TestVideoWatermarking:
    """Tests for video-level watermarking."""

    def test_embed_video(self, sample_video: Path, temp_dir: Path, sample_prompt: str):
        """Should embed watermark into video."""
        output_path = temp_dir / "watermarked.mp4"
        config = VideoWatermarkConfig()

        result = embed_video_watermark(sample_video, output_path, sample_prompt, config)

        assert result["ok"] is True
        assert output_path.exists()
        assert result["frames"] > 0
        assert "prompt_hash" in result

    def test_extract_video(self, sample_video: Path, temp_dir: Path, sample_prompt: str):
        """Should extract and verify watermark from video."""
        output_path = temp_dir / "watermarked.mp4"
        config = VideoWatermarkConfig()

        # Embed
        embed_video_watermark(sample_video, output_path, sample_prompt, config)
        assert output_path.exists()

        # Extract and verify
        verify_result = extract_video_watermark(output_path, sample_prompt, config)

        assert verify_result["ok"] is True
        assert "extracted_hash" in verify_result
        assert verify_result.get("verified", False) is True
        assert verify_result.get("bit_error_rate", 1.0) < 0.15  # Allow 15% BER

    def test_wrong_prompt_fails(self, sample_video: Path, temp_dir: Path):
        """Should fail verification with wrong prompt."""
        output_path = temp_dir / "watermarked.mp4"
        config = VideoWatermarkConfig()

        # Embed with one prompt
        embed_video_watermark(sample_video, output_path, "correct prompt", config)

        # Verify with different prompt
        verify_result = extract_video_watermark(output_path, "wrong prompt", config)

        assert verify_result.get("verified", True) is False

    def test_file_not_found(self, temp_dir: Path):
        """Should raise FileNotFoundError for missing input."""
        missing = temp_dir / "nonexistent.mp4"
        output = temp_dir / "out.mp4"

        with pytest.raises(FileNotFoundError):
            embed_video_watermark(missing, output, "test")

    def test_extraction_without_prompt(self, sample_video: Path, temp_dir: Path):
        """Should extract hash without verification."""
        output_path = temp_dir / "watermarked.mp4"
        config = VideoWatermarkConfig()

        # Embed
        embed_video_watermark(sample_video, output_path, "test prompt", config)

        # Extract without expected prompt
        result = extract_video_watermark(output_path, config=config)

        assert result["ok"] is True
        assert "extracted_hash" in result
        assert "verified" not in result  # No verification without expected prompt


class TestVideoWatermarkConfig:
    """Tests for VideoWatermarkConfig."""

    def test_default_config(self):
        """Should have sensible defaults."""
        config = VideoWatermarkConfig()
        assert config.block_size == 8
        assert config.hash_bits == 128
        assert config.redundancy >= 1

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = VideoWatermarkConfig(
            block_size=16,
            hash_bits=64,
            redundancy=5,
        )
        assert config.block_size == 16
        assert config.hash_bits == 64
        assert config.redundancy == 5
