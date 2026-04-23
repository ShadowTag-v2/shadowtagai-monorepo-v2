# labs/uphillsnowball/tests/test_shadowtag_processor.py
"""Unit tests for ShadowTagProcessor.embed_watermark (Item 11)."""

from __future__ import annotations

import numpy as np
import pytest

from src.watermark.shadowtag_dct import (
    ShadowTagProcessor,
    embed_qim,
    extract_qim,
    perform_dct,
    inverse_dct,
)


class TestQIMPrimitives:
    """Test Quantization Index Modulation building blocks."""

    def test_embed_extract_bit_zero(self):
        """QIM round-trip for bit 0."""
        coeff = 42.7
        modified = embed_qim(coeff, 0, delta=10)
        assert extract_qim(modified, delta=10) == 0

    def test_embed_extract_bit_one(self):
        """QIM round-trip for bit 1."""
        coeff = 42.7
        modified = embed_qim(coeff, 1, delta=10)
        assert extract_qim(modified, delta=10) == 1

    def test_embed_idempotent(self):
        """Embedding the same bit twice yields the same coefficient."""
        coeff = 55.3
        first = embed_qim(coeff, 1, delta=10)
        second = embed_qim(first, 1, delta=10)
        assert first == pytest.approx(second)

    @pytest.mark.parametrize("bit", [0, 1])
    @pytest.mark.parametrize("coeff", [-30.5, 0.0, 15.2, 100.9])
    def test_qim_round_trip_parametric(self, coeff: float, bit: int):
        """QIM round-trip across diverse coefficient values."""
        modified = embed_qim(coeff, bit, delta=10)
        assert extract_qim(modified, delta=10) == bit


class TestDCTTransforms:
    """Test DCT / inverse DCT correctness."""

    def test_dct_idct_round_trip(self):
        """Forward + inverse DCT recovers original block within tolerance."""
        block = np.random.randint(0, 256, (8, 8), dtype=np.uint8)
        dct_block = perform_dct(block)
        recovered = inverse_dct(dct_block)
        np.testing.assert_array_almost_equal(block.astype(float), recovered.astype(float), decimal=0)

    def test_dct_shape_preserved(self):
        """DCT output is 8x8."""
        block = np.zeros((8, 8), dtype=np.uint8)
        dct_block = perform_dct(block)
        assert dct_block.shape == (8, 8)


class TestShadowTagProcessor:
    """Tests for embed_watermark and extract_watermark."""

    @pytest.fixture
    def processor(self) -> ShadowTagProcessor:
        return ShadowTagProcessor(delta=10)

    @pytest.fixture
    def frame_64x64(self) -> np.ndarray:
        """64x64 grayscale frame with varied content."""
        np.random.seed(42)
        return np.random.randint(0, 256, (64, 64), dtype=np.uint8)

    def test_embed_returns_same_shape(self, processor, frame_64x64):
        """Watermarked frame has same shape as input."""
        payload = [1, 0, 1, 0]
        result = processor.embed_watermark(frame_64x64, payload)
        assert result.shape == frame_64x64.shape

    def test_embed_returns_uint8(self, processor, frame_64x64):
        """Watermarked frame dtype is uint8."""
        payload = [1, 0]
        result = processor.embed_watermark(frame_64x64, payload)
        assert result.dtype == np.uint8

    def test_embed_extract_round_trip(self, processor, frame_64x64):
        """Watermark can be extracted after embedding."""
        payload = [1, 0, 1, 1, 0, 0, 1, 0]
        watermarked = processor.embed_watermark(frame_64x64, payload)
        extracted = processor.extract_watermark(watermarked, len(payload))
        assert extracted == payload

    def test_embed_visual_quality_psnr(self, processor, frame_64x64):
        """Watermarked frame has PSNR > 30 dB (imperceptible)."""
        payload = [1, 0, 1, 1]
        watermarked = processor.embed_watermark(frame_64x64, payload)
        mse = np.mean((frame_64x64.astype(float) - watermarked.astype(float)) ** 2)
        if mse > 0:
            psnr = 10 * np.log10(255.0**2 / mse)
            assert psnr > 30, f"PSNR {psnr:.1f} dB is too low"

    def test_embed_rejects_3d_frame(self, processor):
        """3D (color) frames raise ValueError."""
        frame_3d = np.zeros((64, 64, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="2D"):
            processor.embed_watermark(frame_3d, [1, 0])

    def test_embed_empty_payload(self, processor, frame_64x64):
        """Empty payload leaves frame unchanged."""
        result = processor.embed_watermark(frame_64x64, [])
        np.testing.assert_array_equal(result, frame_64x64)

    def test_embed_payload_longer_than_blocks(self, processor):
        """Payload longer than available blocks embeds what it can."""
        tiny_frame = np.random.randint(0, 256, (16, 16), dtype=np.uint8)
        huge_payload = [1] * 1000
        result = processor.embed_watermark(tiny_frame, huge_payload)
        assert result.shape == tiny_frame.shape

    def test_different_deltas_produce_different_results(self, frame_64x64):
        """Different delta values produce different watermarked frames."""
        p1 = ShadowTagProcessor(delta=5)
        p2 = ShadowTagProcessor(delta=20)
        payload = [1, 0, 1, 0]
        r1 = p1.embed_watermark(frame_64x64, payload)
        r2 = p2.embed_watermark(frame_64x64, payload)
        assert not np.array_equal(r1, r2)
