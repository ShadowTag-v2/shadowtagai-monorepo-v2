# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag v2 - Video Steganography Module

This module provides video steganography capabilities for embedding and extracting
hidden data within video frames using various encoding techniques.
"""

from .encoder import VideoEncoder
from .decoder import VideoDecoder
from .frame_processor import FrameProcessor
from .codec import StegoCodec

__all__ = [
  "VideoEncoder",
  "VideoDecoder",
  "FrameProcessor",
  "StegoCodec",
]

__version__ = "2.0.0"
