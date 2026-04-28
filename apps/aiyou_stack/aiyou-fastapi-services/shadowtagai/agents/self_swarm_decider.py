#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""self_swarm_decider.py

Utility wrapper that uses the internal n-autoresearch/Kosmos/BioAgents swarm implementation to
make *all* of Antigravity's future decisions.  Before performing any action –
whether writing code, running a command, or updating a file – this module
evaluates a decision description with the swarm and returns the consensus
outcome.

Typical usage::

    from shadowtagai.agents.self_swarm_decider import SwarmDecisionMaker

    decider = SwarmDecisionMaker()
    # Example: decide whether to commit a new file
    decision = "SWARM VOTE: Commit new file shadowtagai/agents/self_swarm_decider.py | RISK: L | BRAKES: 0"
    result = decider.evaluate(decision)
    print(result)  # prints the formatted swarm decision report

The decision text must follow the pattern used by the internal swarm:

    SWARM VOTE: <intent> | RISK: <L|M|H|EH> | BRAKES: <int>

If risk or brakes are omitted they default to ``M`` and ``0`` respectively.

All decisions are evaluated *internally* – no external API calls – and thus
incur **$0 cost**.
"""

from __future__ import annotations

# Import the internal swarm implementation we added earlier
# The path is relative to the repository root
from shadowtagai.agents.internal_swarm import InternalSwarm


class SwarmDecisionMaker:
    """Facade around :class:`InternalSwarm` for Antigravity's own use.

    The class stores a single ``InternalSwarm`` instance and provides a
    convenient ``evaluate`` method that returns the raw report string.
    """

    def __init__(self) -> None:
        self.swarm = InternalSwarm()
        # Cache the last decision for debugging / audit purposes
        self.last_report: str | None = None
        self.last_decision: str | None = None

    def evaluate(self, decision_str: str) -> str:
        """Run the internal swarm on ``decision_str``.

        Parameters
        ----------
        decision_str: str
            The raw decision string, e.g.
            ``"SWARM VOTE: Commit new file X | RISK: L | BRAKES: 0"``.

        Returns
        -------
        str
            Formatted swarm decision report (exactly as required by the
            protocol).

        """
        self.last_decision = decision_str
        report = self.swarm.evaluate(decision_str)
        self.last_report = report
        return report

    def get_last_report(self) -> str | None:
        """Return the most recent swarm report, if any."""
        return self.last_report

    def get_last_decision(self) -> str | None:
        """Return the most recent raw decision string, if any."""
        return self.last_decision


# ---------------------------------------------------------------------------
# Simple CLI for quick manual checks (optional)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            'Usage: python self_swarm_decider.py "SWARM VOTE: <intent> | RISK: <L|M|H|EH> | BRAKES: <int>"',
        )
        sys.exit(1)
    decision_input = " ".join(sys.argv[1:])
    decider = SwarmDecisionMaker()
    print(decider.evaluate(decision_input))
