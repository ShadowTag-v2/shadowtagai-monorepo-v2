import functools


class GideonGuard:
    """
    The 'Judge 6' Protocol Enforcement Layer.
    Refuses to execute functions if financial/risk gates are not met.
    """

    def __init__(self, strict_mode=True):
        self.strict = strict_mode
        self.gates = {"MIN_MARGIN": 0.30, "MIN_LTV_CAC": 4.0, "MAX_PAYBACK_MONTHS": 3}

    def audit(self, func):
        """Decorator: The 'Fleece Test' before execution."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Extract Metrics from args (assumes dict passed as 'metrics')
            metrics = kwargs.get("metrics", args[0] if args and isinstance(args[0], dict) else {})

            # 2. Run The Validation
            violations = []
            if "margin" in metrics and metrics["margin"] < self.gates["MIN_MARGIN"]:
                violations.append(
                    f"Margin {metrics['margin']:.2%} < {self.gates['MIN_MARGIN']:.0%}"
                )

            if "ltv_cac" in metrics and metrics["ltv_cac"] < self.gates["MIN_LTV_CAC"]:
                violations.append(f"LTV:CAC {metrics['ltv_cac']:.1f} < {self.gates['MIN_LTV_CAC']}")

            if (
                "payback_months" in metrics
                and metrics["payback_months"] > self.gates["MAX_PAYBACK_MONTHS"]
            ):
                violations.append(
                    f"Payback {metrics['payback_months']} months > {self.gates['MAX_PAYBACK_MONTHS']}"
                )

            # 3. Judgment
            if violations and self.strict:
                error_msg = f"⛔ GIDEON BLOCK: {func.__name__} halted. Violations: {violations}"
                print(error_msg)
                return {"status": "BLOCKED", "reason": violations}

            # 4. Execute (Wet Fleece Confirmed)
            print(f"✅ GIDEON PASS: Executing {func.__name__}...")
            return func(*args, **kwargs)

        return wrapper


# Instance for import
judge = GideonGuard(strict_mode=True)
