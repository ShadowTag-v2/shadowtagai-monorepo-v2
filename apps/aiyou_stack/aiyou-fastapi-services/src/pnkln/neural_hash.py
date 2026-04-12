"""
PNKLN Neural Hash - Semantic/Latent Hash Generation (CLIP-based)

Generates semantic hashes for media assets using CLIP (Contrastive Language-Image Pre-training).
Captures perceptual similarity to survive re-encoding, compression, and minor edits.
Crucial for Phase 1 "Iron Core" security premium.

Implementation:
- Model: openai/clip-vit-base-patch32 (Standard, robust, ~350MB)
- Output: 512-bit hex signature (64 bytes)
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np  # type: ignore

# Lazy imports to optimize cold boot time for Cloud Run
try:
    import torch  # type: ignore
    from PIL import Image  # type: ignore
    from transformers import CLIPModel, CLIPProcessor  # type: ignore

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class HashResult:
    """Result of a neural hash operation."""

    hex_hash: str  # The 64-byte hex string (512 bits)
    model_version: str  # e.g. "openai/clip-vit-base-patch32"
    latency_ms: float  # Processing time
    confidence: float = 1.0


class NeuralHash:
    """
    CLIP-based Semantic Hashing.
    Converts media content into a 512-bit semantic fingerprint.
    """

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self._model = None
        self._processor = None
        self._device = None

    def _ensure_model_loaded(self):
        """Lazy load the model to save resources until first use."""
        if not ML_AVAILABLE:
            raise ImportError(
                "NeuralHash requires torch, transformers, and pillow. "
                "Please run: pip install torch transformers pillow numpy"
            )

        if self._model is None:
            logger.info(f"Loading NeuralHash model: {self.model_name}")
            t0 = time.time()

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = CLIPModel.from_pretrained(self.model_name).to(self._device)
            self._processor = CLIPProcessor.from_pretrained(self.model_name)

            logger.info(f"Model loaded on {self._device} in {time.time() - t0:.2f}s")

    def _binarize_embedding(self, embedding: np.ndarray) -> str:
        """
        Convert float embedding to 512-bit hex string (Locality Sensitive Hash).
        Logic: Threshold at 0 (hypersphere center) -> bits -> hex.
        """
        bits = (embedding > 0).astype(np.uint8)
        packed = np.packbits(bits)
        return str(packed.tobytes().hex())

    def _hex_to_bits(self, hex_str: str) -> np.ndarray:
        """Unpack hex string back to bit array for comparison."""
        bytes_obj = bytes.fromhex(hex_str)
        packed = np.frombuffer(bytes_obj, dtype=np.uint8)
        return np.unpackbits(packed)

    def compute_image_hash(self, image_path: str | Path) -> HashResult:
        """Generate neural hash for a single image."""
        self._ensure_model_loaded()
        t0 = time.time()

        processor = self._processor
        model = self._model
        device = self._device

        if not processor or not model or not device:
            # This case should ideally not be reached if _ensure_model_loaded() is successful
            logger.error("NeuralHash model or processor not loaded correctly.")
            return HashResult(
                hex_hash="00" * 64,  # Fallback zero hash
                model_version=self.model_name,
                latency_ms=(time.time() - t0) * 1000,
                confidence=0.0,
            )

        try:
            image = Image.open(image_path)
            # Preprocess and move to device
            inputs = processor(images=image, return_tensors="pt").to(device)

            # Inference
            with torch.no_grad():
                outputs = model.get_image_features(**inputs)

            # Normalize embedding
            embedding = outputs.cpu().numpy().flatten()
            embedding = embedding / np.linalg.norm(embedding)

            return HashResult(
                hex_hash=self._binarize_embedding(embedding),
                model_version=self.model_name,
                latency_ms=(time.time() - t0) * 1000,
            )

        except Exception as e:
            logger.error(f"Neural hash failed for {image_path}: {e}")
            raise

    def compute_video_hash(self, video_path: str | Path) -> HashResult:
        """
        Generate neural hash for a video file (STUB for Phase 1).
        Likely extracts keyframes and averages them or hashes the middle frame.
        """
        logger.warning(f"Video Hashing is in BETA for {video_path}. Using placeholder.")
        # TODO: Implement actual video frame extraction and averaging
        return HashResult(
            hex_hash="00" * 64,  # Null hash
            model_version=self.model_name,
            latency_ms=0.0,
            confidence=0.5,
        )

    def compare(self, hash1: str, hash2: str) -> float:
        """
        Compare two neural hashes using Hamming Distance.
        Returns similarity: 0.0 to 1.0 (1.0 = identical content).
        """
        bits1 = self._hex_to_bits(hash1)
        bits2 = self._hex_to_bits(hash2)

        if len(bits1) != len(bits2):
            raise ValueError("Hash length mismatch")

        # Hamming distance: count differing bits
        mismatch_count = np.sum(bits1 != bits2)
        total_bits = len(bits1)

        # Raw accuracy: (total - mismatch) / total
        raw_sim = 1.0 - (mismatch_count / total_bits)

        # Rescale: Random chance is 0.5 similarity in high-dim space.
        # We map 0.5->0.0 and 1.0->1.0 to make it intuitive.
        adj_sim = max(0.0, (raw_sim - 0.5) * 2)

        return float(adj_sim)


# Singleton instance
_instance = None


def get_neural_hash() -> NeuralHash:
    global _instance
    if _instance is None:
        _instance = NeuralHash()
    return _instance
