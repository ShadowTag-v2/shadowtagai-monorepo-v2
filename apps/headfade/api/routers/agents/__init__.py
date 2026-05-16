"""HeadFade ADK Forensic Agent Fleet.

Four specialized agents that decompose video forensic analysis
into orthogonal domains. Each agent receives the same video context
but analyzes from a different perspective. Results are fused by
the Arbiter Engine into a unified confidence score.

Agent Fleet:
  TemporalCoherenceAgent  — Frame-to-frame motion consistency
  PhysicsSimulationAgent  — Lighting/shadow geometry validation
  AudioVisualSyncAgent    — Lip-sync and audio/video alignment
  MetadataForensicsAgent  — Container/codec/EXIF anomaly detection
"""

from routers.agents.audio_visual_sync import AudioVisualSyncAgent
from routers.agents.metadata_forensics import MetadataForensicsAgent
from routers.agents.physics_simulation import PhysicsSimulationAgent
from routers.agents.temporal_coherence import TemporalCoherenceAgent

__all__ = [
  "AudioVisualSyncAgent",
  "MetadataForensicsAgent",
  "PhysicsSimulationAgent",
  "TemporalCoherenceAgent",
]
