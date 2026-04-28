# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ActiveShield Modular Compliance Framework (MCF v1.0)

"Users select which laws apply to them. ActiveShield assembles
the exact compliance modules needed — nothing more, nothing less."

Compliance-as-Documentation™ - evidence that defends you.
"""

from app.compliance.registry import RegulationRegistry, get_registry

__all__ = ["RegulationRegistry", "get_registry"]
