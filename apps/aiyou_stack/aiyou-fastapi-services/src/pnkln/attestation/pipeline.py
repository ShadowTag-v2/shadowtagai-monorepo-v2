"""
PNKLN Attestation Pipeline

Handles the end-to-end flow of media attestation:
1. Ingestion
2. Semantic Hashing (NeuralHash)
3. Judge #6 Enforcement (Gateway)
4. Cryptographic Signing (ShadowTag) - optional integration
5. Verification
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pnkln.core.judge_six_pipeline import get_judge

from src.pnkln.neural_hash import get_neural_hash

logger = logging.getLogger(__name__)


@dataclass
class AttestationResult:
    """Standardized result for the attestation process."""

    asset_name: str
    asset_type: str
    neural_hash: str
    decision: str  # APPROVE/REJECT
    decision_reason: str
    metadata: dict[str, Any]


class AttestationPipeline:
    """
    Pipeline for processing media assets through Neural Hash attestation
    and Judge #6 Governance.
    """

    def __init__(self):
        self.neural_hash = get_neural_hash()
        self.judge = get_judge()

    async def run_pipeline(
        self, input_path: Path, metadata: dict[str, Any] | None = None
    ) -> AttestationResult:
        """
        Run the full Iron Core attestation loop.

        Args:
            input_path: Path to the media file
            metadata: Additional metadata (provenance info, user ID, etc.)
        """
        metadata = metadata or {}
        if not input_path.exists():
            raise FileNotFoundError(f"Asset not found: {input_path}")

        logger.info(f"Starting Iron Core attestation for {input_path.name}")

        # 1. Generate Neural Hash (The Fingerprint)
        try:
            suffix = input_path.suffix.lower()
            if suffix in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
                hash_res = self.neural_hash.compute_video_hash(input_path)
                asset_type = "video"
            else:
                hash_res = self.neural_hash.compute_image_hash(input_path)
                asset_type = "image"
        except Exception as e:
            logger.error(f"Hashing failed for {input_path}: {e}")
            # If hashing fails, we likely can't proceed with HIGH confidence
            # But the Judge might reject it anyway.
            # We'll re-raise or handle. For critical pipeline, fail closed.
            raise

        # 2. Judge #6 Gate Check (The Governance)
        # We simulate provenance data for MVP or use provided metadata
        provenance_data = metadata.get("provenance", {"receipt_id": "pending_generation"})

        judgment = self.judge.evaluate_asset(
            asset_id=input_path.name,
            provenance_data=provenance_data,
            neural_hash_confidence=hash_res.confidence,
        )

        if judgment.decision == "REJECT":
            logger.warning(f"Asset blocked by Judge #6: {judgment.reason}")
            # In validation mode, we return the rejection result
        else:
            logger.info(f"Asset APPROVED by Judge #6: {judgment.reason}")

        # 3. Construct Final Record
        result = AttestationResult(
            asset_name=input_path.name,
            asset_type=asset_type,
            neural_hash=hash_res.hex_hash,
            decision=judgment.decision,
            decision_reason=judgment.reason,
            metadata={
                **metadata,
                "model_version": hash_res.model_version,
                "latency_ms": hash_res.latency_ms,
                "confidence": hash_res.confidence,
                "judge_timestamp": judgment.timestamp,
            },
        )

        return result

    # Legacy wrapper for backward compatibility if needed
    def process_asset(
        self, file_path: str | Path, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Synchronous wrapper for run_pipeline (or legacy implementation).
        Modified to use the new flow synchronously if possible, or just legacy logic.
        For now, we'll map to the new logic but since run_pipeline is async,
        we might need to run it in loop or just keep sync logic here dupe.

        For simplest MPV integration, we'll keep the synchronous logic here
        but inject the judge check.
        """
        import asyncio

        path = Path(file_path)

        # Simple sync execution of the async logic
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(self.run_pipeline(path, metadata))

        # Convert dataclass to dict for legacy consumers
        return {
            "asset_name": result.asset_name,
            "asset_type": result.asset_type,
            "neural_hash": result.neural_hash,
            "decision": result.decision,
            "decision_reason": result.decision_reason,
            "metadata": result.metadata,
        }

    def verify_asset(
        self, file_path: str | Path, original_hash: str, threshold: float = 0.90
    ) -> dict[str, Any]:
        """
        Verify if an asset matches a claimed original hash semantically.
        """
        # Re-compute hash of the current file
        # We can reuse NeuralHash directly here to avoid async complexity of pipeline
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            hash_res = self.neural_hash.compute_video_hash(path)
        else:
            hash_res = self.neural_hash.compute_image_hash(path)

        current_hash = hash_res.hex_hash

        # Compare
        similarity = self.neural_hash.compare(current_hash, original_hash)
        is_match = similarity >= threshold

        return {
            "is_match": is_match,
            "similarity_score": similarity,
            "threshold_used": threshold,
            "current_hash": current_hash,
            "original_hash": original_hash,
        }


# Singleton or factory if needed
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = AttestationPipeline()
    return _pipeline
