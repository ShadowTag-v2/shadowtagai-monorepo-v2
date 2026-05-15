# /antigravity/core/guard.py
"""THE GIDEON GUARD
Doctrine: 2026 CSRMC (Continuous Authority to Operate)
Function: The absolute veto power over all enterprise actions.
"""

import functools
from datetime import datetime


class GideonGuard:
    def __init__(self, strict_mode: bool = True):
        self.strict = strict_mode
        # The "Fleece" Parameters (Hard-Coded Survival Rules)
        self.gates = {
            "MIN_MARGIN": 0.30,  # We never work for <30% profit.
            "MIN_LTV_CAC": 4.0,  # We never buy users who don't pay 4x back.
            "MAX_RISK": 0.05,  # 5% Risk of Ruin (Kelly Criterion).
            "TECH_MATURITY": 6,  # 6 Months "Lindy" age for new tech.
        }

    def audit(self, domain: str):
        """The Decorator: Grants 'Authority to Operate' (cATO) per function call."""

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 1. TELEMETRY INGEST (The Snapshot)
                # We assume the last argument is always a 'telemetry' dict
                telemetry = kwargs.get("telemetry", {})
                timestamp = datetime.now().isoformat()

                # 2. THE AUDIT (Policy-as-Code)
                violations = []

                if domain == "FINANCE":
                    margin = telemetry.get("margin", 0.0)
                    if margin < self.gates["MIN_MARGIN"]:
                        violations.append(f"CRITICAL: Margin {margin:.1%} < 30%")

                elif domain == "R_AND_D":
                    age = telemetry.get("tech_age", 0)
                    if age < self.gates["TECH_MATURITY"]:
                        violations.append(f"CRITICAL: Tech too new ({age}mo). Hype Risk.")

                # 3. THE VERDICT
                if violations and self.strict:
                    print(f"\\n[{timestamp}] ⛔ GIDEON HALT: {func.__name__} denied.")
                    for v in violations:
                        print(f"   ↳ {v}")
                    return None  # Action Blocked.

                # 4. EXECUTION
                return func(*args, **kwargs)

            return wrapper

        return decorator


# Singleton Instance
judge = GideonGuard()
