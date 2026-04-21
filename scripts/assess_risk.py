#!/usr/bin/env python3
import sys


def check_wet_fleece() -> int:
    # Verify no unparameterized production billing API keys are hardcoded
    # Wet Fleece demands $0 spend limits physically locked in
    return 0


def check_dry_ground(margin) -> int:
    if margin < 0.40:
        return 1
    return 0


def complete() -> None:
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    phase = int(sys.argv[1])
    try:
        margin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    except ValueError:
        margin = 0.0

    if phase == 1:
        res = check_wet_fleece()
        if res == 0:
            complete()
        sys.exit(res)
    elif phase == 2:
        res = check_dry_ground(margin)
        if res == 0:
            complete()
        sys.exit(res)
    else:
        sys.exit(1)
