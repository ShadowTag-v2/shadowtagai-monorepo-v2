"""Kernel 3: Audit Trail Compression using zstd."""

import zstandard as zstd
import hashlib
import json
from app.kernels.base import Kernel, KernelChainError
from app.models.kernel import KernelInput, KernelOutput, KernelMetrics
from app.models.decision import JudgeSixClassification, AuditTrail


class AuditCompressKernel(Kernel):
    """
    Kernel 3: Compress decision metadata into audit trail.

    Specifications:
    - Input: Decision metadata + full context
    - Output: zstd compressed trail (target: 487 bytes)
    - Model: Rules-based (deterministic, no ML)
    - Compression ratio: ~10:1 (library claim)
    """

    TARGET_SIZE_BYTES = 487
    COMPRESSION_LEVEL = 22  # Maximum zstd compression

    def __init__(self):
        super().__init__(
            name="AuditCompressKernel",
            max_latency_ms=None,  # No strict latency requirement (deterministic)
        )

        # Initialize zstd compressor
        self.compressor = zstd.ZstdCompressor(level=self.COMPRESSION_LEVEL)

    async def execute(self, kernel_input: KernelInput) -> KernelOutput:
        """
        Compress decision metadata into audit trail.

        Args:
            kernel_input: Contains JudgeSixClassification and metadata

        Returns:
            KernelOutput with AuditTrail
        """
        try:
            # Extract classification
            if isinstance(kernel_input.data, JudgeSixClassification):
                classification = kernel_input.data
            else:
                raise KernelChainError(f"Invalid input type: expected JudgeSixClassification, got {type(kernel_input.data)}")

            # Build audit metadata (structured for compression)
            audit_metadata = {
                "decision": classification.decision,
                "confidence": round(classification.confidence, 4),
                "risk_tier": classification.risk_tier,
                "reasoning": classification.reasoning,
                "trace_id": kernel_input.trace_id,
                "metadata": kernel_input.metadata,
            }

            # Serialize to JSON
            metadata_json = json.dumps(audit_metadata, sort_keys=True, separators=(",", ":"))
            original_data = metadata_json.encode("utf-8")
            original_size = len(original_data)

            # Compress using zstd
            compressed_data = self.compressor.compress(original_data)
            compressed_size = len(compressed_data)

            # Calculate compression ratio
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 0

            # Generate checksum
            checksum = hashlib.sha256(compressed_data).hexdigest()

            # Create audit trail
            audit_trail = AuditTrail(
                compressed_data=compressed_data,
                compression_ratio=compression_ratio,
                original_size_bytes=original_size,
                compressed_size_bytes=compressed_size,
                checksum=checksum,
            )

            # Check if we met target size
            if compressed_size > self.TARGET_SIZE_BYTES:
                # Log warning but don't fail (this is informational)
                kernel_input.metadata["size_warning"] = f"Compressed size {compressed_size}B exceeds target {self.TARGET_SIZE_BYTES}B"

            return KernelOutput(
                data=audit_trail,
                kernel_name=self.name,
                success=True,
                metadata={
                    "compression_ratio": compression_ratio,
                    "size_reduction_pct": (1 - compressed_size / original_size) * 100,
                },
                metrics=KernelMetrics(
                    latency_ms=0,  # Will be set by base class
                    token_count_input=0,  # No tokens (rules-based)
                    token_count_output=0,
                    cost_usd=0.0,  # Deterministic compression is free
                ),
            )

        except Exception as e:
            raise KernelChainError(f"Audit compression failed: {str(e)}") from e

    @staticmethod
    def decompress(audit_trail: AuditTrail) -> dict:
        """
        Decompress audit trail back to original metadata.

        Utility function for audit retrieval.
        """
        decompressor = zstd.ZstdDecompressor()
        decompressed_data = decompressor.decompress(audit_trail.compressed_data)
        return json.loads(decompressed_data.decode("utf-8"))
