# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
cor_google — Google-Native Slip-Scale Operating Layer.

Replaces legacy XML-based inter-process communication with:
- AG-UI Event Protocol (typed event bus for Triad + Judge 6)
- GCP Substrate (Firestore/BigQuery telemetry plane)
- A2A Mesh (Google Interactions API agent routing)

Architecture: arXiv:2512.14982 Bidirectional Attention Mimicry
"""

from packages.cor_google.ag_ui import AGUIEvent, AGUIEventBus
from packages.cor_google.gcp_substrate import GCPSubstrate
from packages.cor_google.a2a_mesh import A2AMesh

__all__ = [
  "AGUIEvent",
  "AGUIEventBus",
  "GCPSubstrate",
  "A2AMesh",
]
