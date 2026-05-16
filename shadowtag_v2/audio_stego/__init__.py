# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
ShadowTag v2 - Audio Steganography Module

This module provides audio steganography capabilities for embedding and extracting
hidden data within audio files using various encoding techniques.
"""

from .encoder import AudioEncoder
from .decoder import AudioDecoder
from .spectral import SpectralProcessor
from .phase import PhaseEncoder

__all__ = [
  "AudioEncoder",
  "AudioDecoder",
  "SpectralProcessor",
  "PhaseEncoder",
]

__version__ = "2.0.0"
