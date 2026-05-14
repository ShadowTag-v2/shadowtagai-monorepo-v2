# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Spectral Processing for Audio Steganography

Provides frequency domain analysis and manipulation for audio steganography.
"""

from typing import Tuple
import numpy as np


class SpectralProcessor:
    """
    Handles spectral domain operations for audio steganography.

    Provides tools for:
    - FFT/IFFT transformations
    - Spectral masking
    - Frequency bin manipulation
    """

    def __init__(self, frame_size: int = 2048, hop_size: int = 512):
        """
        Initialize spectral processor.

        Args:
            frame_size: FFT frame size (should be power of 2)
            hop_size: Hop size for overlapping frames
        """
        self.frame_size = frame_size
        self.hop_size = hop_size

        # Validate parameters
        if frame_size & (frame_size - 1) != 0:
            raise ValueError("frame_size must be a power of 2")

        if hop_size > frame_size:
            raise ValueError("hop_size must be <= frame_size")

    def stft(self, audio: np.ndarray) -> np.ndarray:
        """
        Compute Short-Time Fourier Transform.

        Args:
            audio: Time domain audio samples

        Returns:
            Complex STFT matrix (frames, bins)
        """
        # Apply Hann window
        window = np.hanning(self.frame_size)

        # Calculate number of frames
        num_frames = 1 + (len(audio) - self.frame_size) // self.hop_size

        # Allocate STFT matrix
        stft_matrix = np.zeros((num_frames, self.frame_size // 2 + 1), dtype=np.complex128)

        # Compute STFT for each frame
        for i in range(num_frames):
            start = i * self.hop_size
            frame = audio[start : start + self.frame_size] * window
            stft_matrix[i] = np.fft.rfft(frame)

        return stft_matrix

    def istft(self, stft_matrix: np.ndarray) -> np.ndarray:
        """
        Compute Inverse Short-Time Fourier Transform.

        Args:
            stft_matrix: Complex STFT matrix (frames, bins)

        Returns:
            Time domain audio samples
        """
        num_frames = stft_matrix.shape[0]
        audio_length = (num_frames - 1) * self.hop_size + self.frame_size

        # Allocate output and window sum arrays
        audio = np.zeros(audio_length)
        window_sum = np.zeros(audio_length)
        window = np.hanning(self.frame_size)

        # Reconstruct audio using overlap-add
        for i in range(num_frames):
            start = i * self.hop_size
            frame = np.fft.irfft(stft_matrix[i])
            audio[start : start + self.frame_size] += frame * window
            window_sum[start : start + self.frame_size] += window**2

        # Normalize by window sum
        non_zero = window_sum > 1e-10
        audio[non_zero] /= window_sum[non_zero]

        return audio

    def get_magnitude_phase(self, stft_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Extract magnitude and phase from STFT matrix.

        Args:
            stft_matrix: Complex STFT matrix

        Returns:
            Tuple of (magnitude, phase)
        """
        magnitude = np.abs(stft_matrix)
        phase = np.angle(stft_matrix)
        return magnitude, phase

    def reconstruct_from_magnitude_phase(self, magnitude: np.ndarray, phase: np.ndarray) -> np.ndarray:
        """
        Reconstruct STFT matrix from magnitude and phase.

        Args:
            magnitude: Magnitude matrix
            phase: Phase matrix

        Returns:
            Complex STFT matrix
        """
        return magnitude * np.exp(1j * phase)

    def apply_spectral_mask(self, stft_matrix: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Apply spectral mask to STFT matrix.

        Args:
            stft_matrix: Complex STFT matrix
            mask: Binary or continuous mask

        Returns:
            Masked STFT matrix
        """
        return stft_matrix * mask

    def find_perceptual_bins(self, magnitude: np.ndarray, threshold: float = 0.1) -> np.ndarray:
        """
        Find frequency bins suitable for embedding (perceptually masked).

        Args:
            magnitude: Magnitude spectrum
            threshold: Relative threshold for bin selection

        Returns:
            Boolean array indicating suitable bins
        """
        # Normalize magnitude
        max_mag = np.max(magnitude)
        if max_mag == 0:
            return np.zeros_like(magnitude, dtype=bool)

        normalized = magnitude / max_mag

        # Select bins above threshold (high energy bins can hide data better)
        suitable = normalized > threshold

        return suitable

    def calculate_spectral_flatness(self, magnitude: np.ndarray) -> float:
        """
        Calculate spectral flatness (tonality measure).

        Args:
            magnitude: Magnitude spectrum

        Returns:
            Spectral flatness value (0 = tonal, 1 = noise-like)
        """
        # Avoid log(0)
        magnitude = magnitude + 1e-10

        geometric_mean = np.exp(np.mean(np.log(magnitude)))
        arithmetic_mean = np.mean(magnitude)

        if arithmetic_mean == 0:
            return 0.0

        flatness = geometric_mean / arithmetic_mean
        return flatness
