# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Plugin Manager — Background plugin/marketplace installation manager.

Ported from Claude Code v2.1.91 services/plugins/PluginInstallationManager.ts.

Architecture
~~~~~~~~~~~~
Handles automatic installation of plugins and marketplaces from trusted
sources (repository and user settings) without blocking startup:

1. **Diff detection**: Compare declared marketplaces against materialized
   (installed) state to find missing/changed entries.
2. **Background reconciliation**: Install/update marketplaces with progress
   callbacks for UI status updates.
3. **Auto-refresh**: After new installs, clear caches and reload plugins.
4. **Status tracking**: Per-marketplace status (pending/installing/installed/
   failed) for monitoring.

In AGNT context, this maps to the skill fleet lifecycle: detecting new skills,
installing from external repos, and refreshing the active skill registry.
"""

from packages.plugin_manager.manager import (
    MarketplaceStatus,
    PluginInstallationManager,
    ReconciliationResult,
)

__all__ = [
    "MarketplaceStatus",
    "PluginInstallationManager",
    "ReconciliationResult",
]
