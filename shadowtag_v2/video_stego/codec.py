# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Steganography Codec

Provides encoding/decoding protocols and format specifications.
"""

from typing import Any
from dataclasses import dataclass
from enum import Enum
import json
import struct


class CodecVersion(Enum):
    """Supported codec versions"""

    V2_0 = "2.0"
    V2_1 = "2.1"


class EncodingMethod(Enum):
    """Supported encoding methods"""

    LSB = "lsb"
    DCT = "dct"
    SPATIAL = "spatial"
    HYBRID = "hybrid"


@dataclass
class CodecHeader:
    """
    Header structure for steganographically encoded data.

    Contains metadata needed for proper decoding.
    """

    version: str  # Codec version
    method: str  # Encoding method used
    bits_per_channel: int  # LSBs used per channel
    compression: bool  # Whether data is compressed
    encryption: bool  # Whether data is encrypted
    error_correction: bool  # Whether error correction is applied
    payload_size: int  # Original payload size in bytes
    checksum: int  # CRC32 checksum
    metadata: dict[str, Any] | None = None  # Optional user metadata

    MAGIC_BYTES = b"SHDW"  # Magic number for identification
    HEADER_VERSION = 1
    HEADER_SIZE = 64  # Fixed header size in bytes

    def to_bytes(self) -> bytes:
        """
        Serialize header to bytes.

        Returns:
            Serialized header (fixed 64 bytes)
        """
        # Pack fixed fields
        header = struct.pack(
            "!4sH H H B B B B I I",
            self.MAGIC_BYTES,  # 4 bytes: Magic number
            self.HEADER_VERSION,  # 2 bytes: Header version
            int(self.version.replace(".", "")),  # 2 bytes: Codec version
            EncodingMethod[self.method.upper()].value.encode()[0],  # 2 bytes: Method
            self.bits_per_channel,  # 1 byte
            int(self.compression),  # 1 byte
            int(self.encryption),  # 1 byte
            int(self.error_correction),  # 1 byte
            self.payload_size,  # 4 bytes
            self.checksum,  # 4 bytes
        )

        # Serialize metadata as JSON (remaining bytes)
        metadata_json = json.dumps(self.metadata or {}).encode()
        metadata_size = min(len(metadata_json), self.HEADER_SIZE - len(header) - 2)

        # Pack metadata size and data
        header += struct.pack("!H", metadata_size)
        header += metadata_json[:metadata_size]

        # Pad to fixed size
        header += b"\x00" * (self.HEADER_SIZE - len(header))

        return header

    @classmethod
    def from_bytes(cls, data: bytes) -> "CodecHeader":
        """
        Deserialize header from bytes.

        Args:
            data: Header bytes (at least 64 bytes)

        Returns:
            Parsed CodecHeader object

        Raises:
            ValueError: If header is invalid
        """
        if len(data) < cls.HEADER_SIZE:
            raise ValueError("Invalid header: too short")

        # Unpack fixed fields
        (
            magic,
            header_version,
            codec_version,
            method_byte,
            bits_per_channel,
            compression,
            encryption,
            error_correction,
            payload_size,
            checksum,
        ) = struct.unpack("!4sH H H B B B B I I", data[:24])

        # Validate magic bytes
        if magic != cls.MAGIC_BYTES:
            raise ValueError(f"Invalid magic bytes: expected {cls.MAGIC_BYTES}, got {magic}")

        # Parse metadata
        metadata_size = struct.unpack("!H", data[24:26])[0]
        metadata_json = data[26 : 26 + metadata_size]

        metadata = None
        if metadata_size > 0:
            try:
                metadata = json.loads(metadata_json.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                metadata = None

        # Convert codec version
        version_str = f"{codec_version // 10}.{codec_version % 10}"

        # Convert method
        method = "lsb"  # Default, TODO: proper mapping

        return cls(
            version=version_str,
            method=method,
            bits_per_channel=bits_per_channel,
            compression=bool(compression),
            encryption=bool(encryption),
            error_correction=bool(error_correction),
            payload_size=payload_size,
            checksum=checksum,
            metadata=metadata,
        )


class StegoCodec:
    """
    High-level codec for steganographic data encoding/decoding.

    Handles header management, data formatting, and protocol compliance.
    """

    def __init__(self, version: CodecVersion = CodecVersion.V2_0):
        """
        Initialize codec.

        Args:
            version: Codec version to use
        """
        self.version = version

    def create_header(self, method: EncodingMethod, payload_size: int, config: dict[str, Any], metadata: dict[str, Any] | None = None) -> CodecHeader:
        """
        Create a codec header for encoded data.

        Args:
            method: Encoding method used
            payload_size: Size of payload in bytes
            config: Encoding configuration
            metadata: Optional user metadata

        Returns:
            CodecHeader object
        """
        header = CodecHeader(
            version=self.version.value,
            method=method.value,
            bits_per_channel=config.get("bits_per_channel", 2),
            compression=config.get("compression", False),
            encryption=config.get("encryption", False),
            error_correction=config.get("error_correction", False),
            payload_size=payload_size,
            checksum=0,  # TODO: Calculate CRC32
            metadata=metadata,
        )

        return header

    def parse_header(self, data: bytes) -> CodecHeader:
        """
        Parse codec header from encoded data.

        Args:
            data: Encoded data with header

        Returns:
            Parsed CodecHeader

        Raises:
            ValueError: If header is invalid
        """
        return CodecHeader.from_bytes(data)

    def validate_compatibility(self, header: CodecHeader) -> bool:
        """
        Validate that a header is compatible with this codec version.

        Args:
            header: Header to validate

        Returns:
            True if compatible, False otherwise
        """
        # Check version compatibility
        if header.version != self.version.value:
            return False

        # Check supported methods
        try:
            EncodingMethod(header.method)
        except ValueError:
            return False

        return True
