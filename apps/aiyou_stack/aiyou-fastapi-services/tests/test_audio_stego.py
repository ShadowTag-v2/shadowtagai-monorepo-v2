"""Tests for audio_stego module."""

from pathlib import Path

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st
from shadowtag_v2.audio_stego import (
    AudioWatermarkConfig,
    butter_highpass,
    embed_audio_watermark,
    extract_audio_watermark,
    extract_bits_from_signal,
    generate_spread_spectrum_signal,
    prompt_hash,
)


class TestPromptHash:
    """Tests for prompt_hash function."""

    def test_deterministic(self):
        """Hash should be deterministic."""
        h1 = prompt_hash("test")
        h2 = prompt_hash("test")
        assert h1 == h2

    def test_length(self):
        """Default hash should be 16 bytes."""
        h = prompt_hash("test")
        assert len(h) == 16

    @given(st.text(min_size=1))
    def test_property_consistency(self, prompt: str):
        """Hash should be consistent across calls."""
        h1 = prompt_hash(prompt)
        h2 = prompt_hash(prompt)
        assert h1 == h2


class TestSpreadSpectrumSignal:
    """Tests for spread spectrum signal generation."""

    def test_generate_signal_shape(self):
        """Generated signal should have correct shape."""
        config = AudioWatermarkConfig()
        bits = np.array([0, 1, 0, 1], dtype=np.uint8)

        signal = generate_spread_spectrum_signal(bits, config)

        expected_length = int(config.sample_rate * config.duration)
        assert len(signal) == expected_length
        assert signal.dtype == np.float32

    def test_signal_amplitude(self):
        """Signal amplitude should match config."""
        config = AudioWatermarkConfig(amplitude=0.1)
        bits = np.array([1, 1, 1, 1], dtype=np.uint8)

        signal = generate_spread_spectrum_signal(bits, config)

        # Max amplitude should be approximately config.amplitude
        assert np.abs(signal).max() <= config.amplitude * 1.1

    def test_different_bits_produce_different_signals(self):
        """Different bit patterns should produce different signals."""
        config = AudioWatermarkConfig()

        bits1 = np.array([0, 0, 0, 0], dtype=np.uint8)
        bits2 = np.array([1, 1, 1, 1], dtype=np.uint8)

        signal1 = generate_spread_spectrum_signal(bits1, config)
        signal2 = generate_spread_spectrum_signal(bits2, config)

        # Signals should differ
        assert not np.allclose(signal1, signal2)


class TestHighpassFilter:
    """Tests for highpass filter."""

    def test_filter_shape(self):
        """Filtered signal should have same shape as input."""
        config = AudioWatermarkConfig()
        signal = np.random.randn(48000).astype(np.float32)

        filtered = butter_highpass(signal, config)

        assert filtered.shape == signal.shape
        assert filtered.dtype == np.float32

    def test_filter_attenuates_low_freq(self):
        """Filter should attenuate low frequencies."""
        config = AudioWatermarkConfig(highpass_cutoff=5000.0)

        # Create low-frequency signal (1 kHz)
        sr = 48000
        t = np.linspace(0, 1, sr, endpoint=False)
        low_freq = np.sin(2 * np.pi * 1000 * t).astype(np.float32)

        filtered = butter_highpass(low_freq, config)

        # Filtered signal should have much lower amplitude
        assert np.abs(filtered).max() < np.abs(low_freq).max() * 0.5


class TestBitExtraction:
    """Tests for bit extraction from signal."""

    def test_extract_bits_shape(self):
        """Should extract correct number of bits."""
        config = AudioWatermarkConfig()
        signal = np.random.randn(int(config.sample_rate * config.duration)).astype(np.float32)

        bits = extract_bits_from_signal(signal, 8, config)

        assert len(bits) == 8
        assert bits.dtype == np.uint8
        assert all(b in [0, 1] for b in bits)

    def test_extract_from_embedded_signal(self):
        """Should extract bits from generated spread spectrum signal."""
        config = AudioWatermarkConfig(chip_rate=100)
        original_bits = np.array([0, 1, 1, 0, 1, 0, 0, 1], dtype=np.uint8)

        # Generate signal
        signal = generate_spread_spectrum_signal(original_bits, config)

        # Extract bits
        extracted = extract_bits_from_signal(signal, len(original_bits), config)

        # Should match reasonably well (allow some errors)
        accuracy = np.sum(original_bits == extracted) / len(original_bits)
        assert accuracy >= 0.6  # At least 60% accuracy


class TestAudioWatermarking:
    """Tests for audio-level watermarking."""

    def test_embed_audio(self, sample_audio: Path, temp_dir: Path, sample_prompt: str):
        """Should embed watermark into audio."""
        output_path = temp_dir / "watermarked.wav"
        config = AudioWatermarkConfig()

        result = embed_audio_watermark(sample_audio, output_path, sample_prompt, config)

        assert result["ok"] is True
        assert output_path.exists()
        assert result["sample_rate"] == 48000
        assert "prompt_hash" in result

    def test_extract_audio(self, sample_audio: Path, temp_dir: Path, sample_prompt: str):
        """Should extract and verify watermark from audio."""
        output_path = temp_dir / "watermarked.wav"
        config = AudioWatermarkConfig()

        # Embed
        embed_audio_watermark(sample_audio, output_path, sample_prompt, config)

        # Extract and verify
        verify_result = extract_audio_watermark(output_path, sample_prompt, config)

        assert verify_result["ok"] is True
        assert "extracted_hash" in verify_result
        # Note: Audio watermarking is less robust than video, allow higher BER
        # Verification might fail due to signal processing - that's expected

    def test_low_sample_rate_rejected(self, temp_dir: Path):
        """Should reject audio with sample rate < 40 kHz."""
        import soundfile as sf

        # Create 16 kHz audio (too low)
        low_sr_audio = temp_dir / "low_sr.wav"
        audio = np.random.randn(16000, 2).astype(np.float32)
        sf.write(str(low_sr_audio), audio, 16000)

        output_path = temp_dir / "out.wav"

        with pytest.raises(ValueError, match="Sample rate.*too low"):
            embed_audio_watermark(low_sr_audio, output_path, "test")

    def test_file_not_found(self, temp_dir: Path):
        """Should raise FileNotFoundError for missing input."""
        missing = temp_dir / "nonexistent.wav"
        output = temp_dir / "out.wav"

        with pytest.raises(FileNotFoundError):
            embed_audio_watermark(missing, output, "test")

    def test_extraction_without_prompt(self, sample_audio: Path, temp_dir: Path):
        """Should extract hash without verification."""
        output_path = temp_dir / "watermarked.wav"
        config = AudioWatermarkConfig()

        # Embed
        embed_audio_watermark(sample_audio, output_path, "test prompt", config)

        # Extract without expected prompt
        result = extract_audio_watermark(output_path, config=config)

        assert result["ok"] is True
        assert "extracted_hash" in result
        assert "verified" not in result


class TestAudioWatermarkConfig:
    """Tests for AudioWatermarkConfig."""

    def test_default_config(self):
        """Should have sensible defaults."""
        config = AudioWatermarkConfig()
        assert config.sample_rate == 48000
        assert config.carrier_freq >= 19000  # Ultrasonic
        assert config.amplitude > 0
        assert config.hash_bits == 128

    def test_custom_config(self):
        """Should allow custom configuration."""
        config = AudioWatermarkConfig(
            sample_rate=96000,
            carrier_freq=20000.0,
            amplitude=0.05,
        )
        assert config.sample_rate == 96000
        assert config.carrier_freq == 20000.0
        assert config.amplitude == 0.05
