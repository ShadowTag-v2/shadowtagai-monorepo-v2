# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag v2 - Advanced Steganography Toolkit

A comprehensive steganography framework for embedding and extracting hidden data
in video and audio files, with blockchain-inspired receipt chains for verification.

Modules:
    - video_stego: Video steganography operations
    - audio_stego: Audio steganography operations
    - receipt_chain: Blockchain-style verification and audit trails
    - cli: Command-line interface

Usage:
    from shadowtag_v2 import video_stego, audio_stego, receipt_chain

    # Video encoding
    from shadowtag_v2.video_stego import VideoEncoder, EncoderConfig
    encoder = VideoEncoder(EncoderConfig(bits_per_channel=2))
    stats = encoder.encode(video_path, payload, output_path)

    # Audio encoding
    from shadowtag_v2.audio_stego import AudioEncoder, AudioEncoderConfig
    encoder = AudioEncoder(AudioEncoderConfig(method="phase"))
    stats = encoder.encode(audio_path, payload, output_path)

    # Receipt chain management
    from shadowtag_v2.receipt_chain import ReceiptChain, Receipt
    chain = ReceiptChain()
    chain.add_receipt(receipt)
"""

from . import video_stego
from . import audio_stego
from . import receipt_chain
from . import cli

__version__ = "2.0.0"
__author__ = "ShadowTag Development Team"
__all__ = [
  "video_stego",
  "audio_stego",
  "receipt_chain",
  "cli",
]
