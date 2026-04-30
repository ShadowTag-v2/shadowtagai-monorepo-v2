# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass
from typing import List


@dataclass
class UserIntent:
    is_explicit: bool
    scope_exceeded: bool
    agent_inferred: bool


def evaluate_composite_action(commands: list[str], intent: UserIntent) -> bool:
    """Evaluates composite actions with user intent override."""
    # Rule 2: Scope escalation = autonomous
    if intent.scope_exceeded:
        return False
    # Rule 4: Agent-inferred parameters != user-intended
    if intent.agent_inferred and not intent.is_explicit:
        return False

    for cmd in commands:
        if "rm -rf" in cmd or "DROP TABLE" in cmd.upper():
            if not intent.is_explicit:
                return False
    return True
