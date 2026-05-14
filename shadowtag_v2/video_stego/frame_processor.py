# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Video Frame Processor

Handles low-level frame manipulation for steganographic operations.
"""

from typing import List, Tuple
import numpy as np
from enum import Enum


class ColorChannel(Enum):
    """Color channels for RGB frames"""

    RED = 0
    GREEN = 1
    BLUE = 2
    ALL = 3


class FrameProcessor:
    """
    Low-level frame processing for steganographic embedding and extraction.

    Provides utilities for:
    - LSB manipulation in video frames
    - Frame-level bit operations
    - Spatial domain processing
    """

    @staticmethod
    def embed_bits_lsb(frame: np.ndarray, bits: list[int], bits_per_channel: int = 2, channels: ColorChannel = ColorChannel.ALL) -> np.ndarray:
        """
        Embed bits into frame using LSB substitution.

        Args:
            frame: Input frame as numpy array (H, W, C)
            bits: List of bits to embed (0 or 1)
            bits_per_channel: Number of LSBs to use per channel
            channels: Which color channels to use

        Returns:
            Modified frame with embedded bits

        Raises:
            ValueError: If bits don't fit in frame capacity
        """
        if not 1 <= bits_per_channel <= 4:
            raise ValueError("bits_per_channel must be between 1 and 4")

        modified_frame = frame.copy()
        bit_mask = (1 << bits_per_channel) - 1  # Mask for LSBs
        clear_mask = ~bit_mask & 0xFF  # Mask to clear LSBs

        # Calculate capacity
        capacity = FrameProcessor.calculate_frame_capacity(frame.shape, bits_per_channel, channels)

        if len(bits) > capacity:
            raise ValueError(f"Cannot embed {len(bits)} bits in frame with capacity {capacity}")

        # Determine which channels to use
        channel_indices = FrameProcessor._get_channel_indices(channels)

        # Embed bits
        bit_index = 0
        for y in range(frame.shape[0]):
            for x in range(frame.shape[1]):
                for c in channel_indices:
                    if bit_index >= len(bits):
                        return modified_frame

                    # Extract bits_per_channel bits from bit stream
                    value = 0
                    for i in range(bits_per_channel):
                        if bit_index < len(bits):
                            value |= bits[bit_index] << i
                            bit_index += 1

                    # Clear LSBs and embed new value
                    pixel_value = modified_frame[y, x, c]
                    pixel_value = (pixel_value & clear_mask) | value
                    modified_frame[y, x, c] = pixel_value

        return modified_frame

    @staticmethod
    def extract_bits_lsb(frame: np.ndarray, num_bits: int, bits_per_channel: int = 2, channels: ColorChannel = ColorChannel.ALL) -> list[int]:
        """
        Extract bits from frame using LSB extraction.

        Args:
            frame: Input frame as numpy array (H, W, C)
            num_bits: Number of bits to extract
            bits_per_channel: Number of LSBs used per channel
            channels: Which color channels were used

        Returns:
            List of extracted bits (0 or 1)
        """
        if not 1 <= bits_per_channel <= 4:
            raise ValueError("bits_per_channel must be between 1 and 4")

        bit_mask = (1 << bits_per_channel) - 1
        channel_indices = FrameProcessor._get_channel_indices(channels)

        bits = []
        bit_index = 0

        for y in range(frame.shape[0]):
            for x in range(frame.shape[1]):
                for c in channel_indices:
                    if bit_index >= num_bits:
                        return bits

                    # Extract LSBs
                    pixel_value = frame[y, x, c]
                    embedded_value = pixel_value & bit_mask

                    # Convert to individual bits
                    for i in range(bits_per_channel):
                        if bit_index < num_bits:
                            bit = (embedded_value >> i) & 1
                            bits.append(bit)
                            bit_index += 1

        return bits

    @staticmethod
    def calculate_frame_capacity(frame_shape: tuple[int, int, int], bits_per_channel: int = 2, channels: ColorChannel = ColorChannel.ALL) -> int:
        """
        Calculate the bit capacity of a single frame.

        Args:
            frame_shape: Shape tuple (height, width, channels)
            bits_per_channel: Number of LSBs to use
            channels: Which color channels to use

        Returns:
            Capacity in bits
        """
        height, width, num_channels = frame_shape
        channel_count = len(FrameProcessor._get_channel_indices(channels))

        return height * width * channel_count * bits_per_channel

    @staticmethod
    def _get_channel_indices(channels: ColorChannel) -> list[int]:
        """
        Get list of channel indices to process.

        Args:
            channels: Channel selection

        Returns:
            List of channel indices (0-2 for RGB)
        """
        if channels == ColorChannel.ALL:
            return [0, 1, 2]
        elif channels == ColorChannel.RED:
            return [0]
        elif channels == ColorChannel.GREEN:
            return [1]
        elif channels == ColorChannel.BLUE:
            return [2]
        else:
            raise ValueError(f"Unknown channel type: {channels}")

    @staticmethod
    def bytes_to_bits(data: bytes) -> list[int]:
        """
        Convert bytes to list of bits.

        Args:
            data: Input bytes

        Returns:
            List of bits (0 or 1)
        """
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits

    @staticmethod
    def bits_to_bytes(bits: list[int]) -> bytes:
        """
        Convert list of bits to bytes.

        Args:
            bits: List of bits (0 or 1)

        Returns:
            Bytes object
        """
        # Pad bits to multiple of 8
        padded_bits = bits + [0] * (8 - len(bits) % 8 if len(bits) % 8 != 0 else 0)

        byte_array = []
        for i in range(0, len(padded_bits), 8):
            byte_value = 0
            for j in range(8):
                byte_value |= padded_bits[i + j] << j
            byte_array.append(byte_value)

        return bytes(byte_array)

    @staticmethod
    def calculate_psnr(original: np.ndarray, modified: np.ndarray) -> float:
        """
        Calculate Peak Signal-to-Noise Ratio between original and modified frames.

        Args:
            original: Original frame
            modified: Modified frame

        Returns:
            PSNR value in dB
        """
        mse = np.mean((original.astype(float) - modified.astype(float)) ** 2)

        if mse == 0:
            return float("inf")

        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))

        return psnr
