# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tests for audio_stego module
"""

import pytest
import numpy as np

from shadowtag_v2.audio_stego import (
  AudioEncoder,
  AudioDecoder,
  SpectralProcessor,
  PhaseEncoder,
  AudioEncoderConfig,
)


class TestSpectralProcessor:
  """Tests for SpectralProcessor"""

  def test_initialization(self):
    """Test spectral processor initializes correctly"""
    processor = SpectralProcessor(frame_size=2048, hop_size=512)
    assert processor.frame_size == 2048
    assert processor.hop_size == 512

  def test_invalid_frame_size(self):
    """Test non-power-of-2 frame size raises error"""
    with pytest.raises(ValueError, match="power of 2"):
      SpectralProcessor(frame_size=1000)

  def test_invalid_hop_size(self):
    """Test hop size > frame size raises error"""
    with pytest.raises(ValueError, match="hop_size"):
      SpectralProcessor(frame_size=2048, hop_size=4096)

  def test_stft_istft_roundtrip(self):
    """Test STFT/ISTFT reconstruction"""
    processor = SpectralProcessor()

    # Generate test signal (1 second at 44.1kHz)
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave

    # Transform and inverse
    stft_matrix = processor.stft(audio)
    reconstructed = processor.istft(stft_matrix)

    # Check reconstruction quality (should be very close)
    # Account for edge effects by comparing middle portion
    mid_start = 1000
    mid_end = -1000
    correlation = np.corrcoef(
      audio[mid_start:mid_end], reconstructed[mid_start:mid_end]
    )[0, 1]

    assert correlation > 0.99  # Very high correlation

  def test_magnitude_phase_decomposition(self):
    """Test magnitude/phase decomposition and reconstruction"""
    processor = SpectralProcessor()

    # Create simple STFT matrix
    stft_matrix = np.random.randn(100, 1025) + 1j * np.random.randn(100, 1025)

    # Decompose
    magnitude, phase = processor.get_magnitude_phase(stft_matrix)

    # Reconstruct
    reconstructed = processor.reconstruct_from_magnitude_phase(magnitude, phase)

    # Verify reconstruction
    np.testing.assert_allclose(stft_matrix, reconstructed, rtol=1e-10)

  def test_spectral_flatness(self):
    """Test spectral flatness calculation"""
    processor = SpectralProcessor()

    # White noise (high flatness)
    white_noise = np.random.randn(1025)
    white_noise = np.abs(white_noise)
    flatness_noise = processor.calculate_spectral_flatness(white_noise)
    assert flatness_noise > 0.5  # Should be relatively high

    # Pure tone (low flatness)
    pure_tone = np.zeros(1025)
    pure_tone[100] = 1.0  # Single spike
    flatness_tone = processor.calculate_spectral_flatness(pure_tone)
    assert flatness_tone < 0.5  # Should be relatively low


class TestPhaseEncoder:
  """Tests for PhaseEncoder"""

  def test_initialization(self):
    """Test phase encoder initializes correctly"""
    encoder = PhaseEncoder()
    assert encoder.spectral.frame_size == 2048
    assert encoder.phase_range == np.pi / 4

  def test_capacity_calculation(self):
    """Test capacity calculation"""
    encoder = PhaseEncoder()

    # 1 second at 44.1kHz
    sample_rate = 44100
    audio_length = 44100

    capacity = encoder.calculate_capacity(audio_length, sample_rate)
    assert capacity > 0
    assert isinstance(capacity, int)

  def test_encode_decode_roundtrip(self):
    """Test encoding and decoding bits"""
    encoder = PhaseEncoder()

    # Generate test audio (1 second)
    sample_rate = 44100
    t = np.linspace(0, 1.0, sample_rate)
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz

    # Test bits
    test_bits = [0, 1, 1, 0, 1, 0, 0, 1] * 10  # 80 bits

    # Encode
    encoded_audio = encoder.encode(audio, test_bits)

    # Decode
    decoded_bits = encoder.decode(encoded_audio, len(test_bits))

    # Verify (allow some errors due to phase quantization)
    matches = sum(a == b for a, b in zip(test_bits, decoded_bits))
    accuracy = matches / len(test_bits)
    assert accuracy > 0.7  # At least 70% accuracy


class TestAudioEncoder:
  """Tests for AudioEncoder"""

  def test_initialization(self):
    """Test encoder initializes with default config"""
    encoder = AudioEncoder()
    assert encoder.config.method == "lsb"
    assert encoder.config.use_encryption is True

  def test_invalid_method_raises_error(self):
    """Test invalid method raises ValueError"""
    with pytest.raises(ValueError, match="Invalid method"):
      AudioEncoder(AudioEncoderConfig(method="invalid"))

  def test_invalid_bits_per_sample_raises_error(self):
    """Test invalid bits_per_sample raises ValueError"""
    with pytest.raises(ValueError, match="bits_per_sample"):
      AudioEncoder(AudioEncoderConfig(bits_per_sample=10))

  def test_snr_calculation(self):
    """Test SNR calculation"""
    encoder = AudioEncoder()

    # Create similar signals
    original = np.random.randn(10000)
    encoded = original + np.random.randn(10000) * 0.01  # Add small noise

    snr = encoder._calculate_snr(original, encoded)
    assert snr > 20  # Should have decent SNR


class TestAudioDecoder:
  """Tests for AudioDecoder"""

  def test_initialization(self):
    """Test decoder initializes correctly"""
    decoder = AudioDecoder()
    assert decoder.config.verify_integrity is True

  def test_method_detection(self):
    """Test method detection returns valid method"""
    decoder = AudioDecoder()
    audio = np.random.randn(44100)

    method = decoder._detect_method(audio)
    assert method in ["lsb", "phase", "echo", "spread_spectrum"]
