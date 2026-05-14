# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tests for video_stego module
"""

import pytest
import numpy as np
from pathlib import Path

from shadowtag_v2.video_stego import (
    VideoEncoder,
    VideoDecoder,
    FrameProcessor,
    EncoderConfig,
    ColorChannel,
)


class TestFrameProcessor:
    """Tests for FrameProcessor"""

    def test_bytes_to_bits_conversion(self):
        """Test converting bytes to bits"""
        data = b"AB"
        bits = FrameProcessor.bytes_to_bits(data)

        # 'A' = 65 = 01000001, 'B' = 66 = 01000010
        assert len(bits) == 16
        assert all(bit in [0, 1] for bit in bits)

    def test_bits_to_bytes_conversion(self):
        """Test converting bits to bytes"""
        bits = [1, 0, 0, 0, 0, 1, 1, 0]  # 'a' = 97
        result = FrameProcessor.bits_to_bytes(bits)
        assert result == b"a"

    def test_roundtrip_conversion(self):
        """Test roundtrip byte/bit conversion"""
        original = b"Hello, World!"
        bits = FrameProcessor.bytes_to_bits(original)
        recovered = FrameProcessor.bits_to_bytes(bits)
        assert recovered == original

    def test_calculate_frame_capacity(self):
        """Test frame capacity calculation"""
        frame_shape = (1080, 1920, 3)  # Full HD RGB
        capacity = FrameProcessor.calculate_frame_capacity(frame_shape, bits_per_channel=2, channels=ColorChannel.ALL)

        # 1080 * 1920 * 3 * 2 = 12,441,600 bits
        assert capacity == 1080 * 1920 * 3 * 2

    def test_embed_and_extract_bits_lsb(self):
        """Test LSB embedding and extraction"""
        # Create test frame
        frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        # Create test data
        test_data = b"Test"
        bits = FrameProcessor.bytes_to_bits(test_data)

        # Embed
        modified_frame = FrameProcessor.embed_bits_lsb(frame, bits, bits_per_channel=2)

        # Extract
        extracted_bits = FrameProcessor.extract_bits_lsb(modified_frame, len(bits), bits_per_channel=2)

        # Verify
        assert extracted_bits == bits

        # Verify frame not drastically changed
        psnr = FrameProcessor.calculate_psnr(frame, modified_frame)
        assert psnr > 30  # Should have high PSNR (minimal visible change)

    def test_capacity_overflow(self):
        """Test that embedding too many bits raises error"""
        frame = np.zeros((10, 10, 3), dtype=np.uint8)
        bits = [0] * 10000  # Too many bits

        with pytest.raises(ValueError, match="Cannot embed"):
            FrameProcessor.embed_bits_lsb(frame, bits)


class TestVideoEncoder:
    """Tests for VideoEncoder"""

    def test_encoder_initialization(self):
        """Test encoder initializes with default config"""
        encoder = VideoEncoder()
        assert encoder.config.bits_per_channel == 2
        assert encoder.config.use_encryption is True

    def test_invalid_config_raises_error(self):
        """Test invalid config raises ValueError"""
        with pytest.raises(ValueError):
            VideoEncoder(EncoderConfig(bits_per_channel=10))

        with pytest.raises(ValueError):
            VideoEncoder(EncoderConfig(frame_skip=0))

    def test_capacity_estimation(self):
        """Test capacity estimation"""
        encoder = VideoEncoder()
        # This will use placeholder implementation
        capacity = encoder.estimate_capacity(Path("/fake/path.mp4"))
        assert "total_bytes" in capacity
        assert "usable_bytes" in capacity


class TestVideoDecoder:
    """Tests for VideoDecoder"""

    def test_decoder_initialization(self):
        """Test decoder initializes with default config"""
        decoder = VideoDecoder()
        assert decoder.config.verify_integrity is True

    def test_detect_embedded_data(self):
        """Test detection returns proper structure"""
        decoder = VideoDecoder()
        result = decoder.detect_embedded_data(Path("/fake/path.mp4"))

        assert "has_embedded_data" in result
        assert "confidence" in result
        assert "suspected_method" in result


class TestCodec:
    """Tests for StegoCodec"""

    def test_codec_header_serialization(self):
        """Test codec header can be serialized and deserialized"""
        from shadowtag_v2.video_stego.codec import (
            CodecHeader,
            StegoCodec,
            EncodingMethod,
            CodecVersion,
        )

        codec = StegoCodec(CodecVersion.V2_0)
        header = codec.create_header(
            method=EncodingMethod.LSB,
            payload_size=1024,
            config={
                "bits_per_channel": 2,
                "compression": False,
                "encryption": True,
                "error_correction": True,
            },
        )

        # Serialize
        header_bytes = header.to_bytes()
        assert len(header_bytes) == CodecHeader.HEADER_SIZE

        # Deserialize
        recovered = CodecHeader.from_bytes(header_bytes)
        assert recovered.payload_size == 1024
        assert recovered.bits_per_channel == 2
        assert recovered.encryption is True
