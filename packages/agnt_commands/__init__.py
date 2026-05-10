# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""AGNT Commands — Slash command registry.

10 ported commands: clear, compact, config, commit, context,
cost, diff, doctor, dream, effort.
"""

from packages.agnt_commands.commands import (
  COMMAND_REGISTRY,
  CommandContext,
  CommandResult,
  dispatch_command,
)

__all__ = [
  "COMMAND_REGISTRY",
  "CommandContext",
  "CommandResult",
  "dispatch_command",
]
