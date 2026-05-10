"""agnt_voice — Safe Harbor Voice Module.

Local-only voice capture and STT. Text-only bottleneck — raw audio
bytes NEVER enter the LLM context window.
"""

from ._types import (
  FinalizeSource,
  RecordingAvailability,
  VoiceDependencyCheck,
  VoiceStreamCallbacks,
)
from .gate import is_voice_enabled

__all__ = [
  "FinalizeSource",
  "RecordingAvailability",
  "VoiceDependencyCheck",
  "VoiceStreamCallbacks",
  "is_voice_enabled",
]
