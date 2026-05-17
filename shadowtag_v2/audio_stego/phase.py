# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Phase Encoding for Audio Steganography

Implements phase-based encoding techniques in the frequency domain.
"""

import numpy as np
from .spectral import SpectralProcessor


class PhaseEncoder:
  """
  Phase-based audio steganography encoder.

  Embeds data by modifying the phase components of audio in the
  frequency domain while preserving magnitude information.
  """

  def __init__(
    self, frame_size: int = 2048, hop_size: int = 512, phase_range: float = np.pi / 4
  ):
    """
    Initialize phase encoder.

    Args:
        frame_size: FFT frame size
        hop_size: Hop size for STFT
        phase_range: Maximum phase deviation for encoding (radians)
    """
    self.spectral = SpectralProcessor(frame_size, hop_size)
    self.phase_range = phase_range

  def encode(self, audio: np.ndarray, bits: list[int]) -> np.ndarray:
    """
    Encode bits into audio using phase manipulation.

    Args:
        audio: Input audio samples
        bits: List of bits to encode (0 or 1)

    Returns:
        Encoded audio samples
    """
    # Compute STFT
    stft_matrix = self.spectral.stft(audio)
    magnitude, phase = self.spectral.get_magnitude_phase(stft_matrix)

    # Modify phase to encode bits
    modified_phase = self._embed_bits_in_phase(phase, bits)

    # Reconstruct STFT
    modified_stft = self.spectral.reconstruct_from_magnitude_phase(
      magnitude, modified_phase
    )

    # Convert back to time domain
    encoded_audio = self.spectral.istft(modified_stft)

    return encoded_audio[: len(audio)]  # Trim to original length

  def decode(self, audio: np.ndarray, num_bits: int) -> list[int]:
    """
    Decode bits from phase-encoded audio.

    Args:
        audio: Encoded audio samples
        num_bits: Number of bits to extract

    Returns:
        List of extracted bits
    """
    # Compute STFT
    stft_matrix = self.spectral.stft(audio)
    _, phase = self.spectral.get_magnitude_phase(stft_matrix)

    # Extract bits from phase
    bits = self._extract_bits_from_phase(phase, num_bits)

    return bits

  def _embed_bits_in_phase(self, phase: np.ndarray, bits: list[int]) -> np.ndarray:
    """
    Embed bits into phase matrix.

    Uses phase deviation to represent binary values:
    - 0: phase -= phase_range
    - 1: phase += phase_range

    Args:
        phase: Original phase matrix (frames, bins)
        bits: Bits to embed

    Returns:
        Modified phase matrix
    """
    modified_phase = phase.copy()
    num_frames, num_bins = phase.shape

    # Use middle frequency bins (more perceptually masked)
    bin_start = num_bins // 4
    bin_end = 3 * num_bins // 4
    bin_end - bin_start

    bit_idx = 0
    for frame_idx in range(num_frames):
      if bit_idx >= len(bits):
        break

      for bin_idx in range(bin_start, bin_end):
        if bit_idx >= len(bits):
          break

        # Encode bit as phase deviation
        if bits[bit_idx] == 0:
          modified_phase[frame_idx, bin_idx] -= self.phase_range
        else:
          modified_phase[frame_idx, bin_idx] += self.phase_range

        bit_idx += 1

    # Wrap phase to [-π, π]
    modified_phase = np.arctan2(np.sin(modified_phase), np.cos(modified_phase))

    return modified_phase

  def _extract_bits_from_phase(self, phase: np.ndarray, num_bits: int) -> list[int]:
    """
    Extract bits from phase matrix.

    Args:
        phase: Phase matrix (frames, bins)
        num_bits: Number of bits to extract

    Returns:
        List of extracted bits
    """
    num_frames, num_bins = phase.shape
    bin_start = num_bins // 4
    bin_end = 3 * num_bins // 4

    bits = []
    bit_idx = 0

    for frame_idx in range(num_frames):
      if bit_idx >= num_bits:
        break

      for bin_idx in range(bin_start, bin_end):
        if bit_idx >= num_bits:
          break

        # Decode bit from phase value
        # Positive deviation = 1, negative = 0
        phase_val = phase[frame_idx, bin_idx]
        bit = 1 if phase_val > 0 else 0
        bits.append(bit)

        bit_idx += 1

    return bits

  def calculate_capacity(self, audio_length: int, sample_rate: int) -> int:
    """
    Calculate embedding capacity for given audio length.

    Args:
        audio_length: Number of audio samples
        sample_rate: Sample rate in Hz

    Returns:
        Capacity in bits
    """
    # Calculate number of STFT frames
    num_frames = 1 + (audio_length - self.spectral.frame_size) // self.spectral.hop_size

    # Usable bins (middle 50% of spectrum)
    num_bins = self.spectral.frame_size // 2 + 1
    usable_bins = num_bins // 2

    # Total capacity
    capacity_bits = num_frames * usable_bins

    return capacity_bits
