#!/usr/bin/env python3
import json
import sys

"""
# pnkln_10fingers_audit.py

Implements the pnkln 10 Fingers Audit for business viability scoring.

USAGE:
    python3 pnkln_10fingers_audit.py --score '{"MarketDemand": 8, "OfferMix": 7, ...}'
    OR interactively if no args.
"""

pnkln_10FINGERS = [
    ("MarketDemand", "verified size/fragmentation/category"),
    ("OfferMix", "anchor+upsells+hedges validated"),
    ("TechLeverage", "automation ROI<18m"),
    ("DistributionDensity", "cluster/batch/route"),
    ("PricingPower", "GBB tiers/ARPC up"),
    ("LaborTraining", "labor<=0.30, training multiplier"),
    ("Marketing", "cheap compounding channels then paid"),
    ("RiskCompliance", "risk matrix+moat"),
    ("ScalingModel", "unit econ proven>30% margin"),
    ("ExitAsset", "systems/contracts/reviews or durable CF"),
]

# WEIGHTS (for composite scoring)
WEIGHTS = {
    "MarketDemand": 1.3,  # Heaviest - no market = death
    "OfferMix": 1.1,  # Revenue architecture
    "TechLeverage": 1.1,  # Automation multiplier
    "DistributionDensity": 1.1,  # Route economics
    "PricingPower": 1.0,  # ARPC expansion
    "LaborTraining": 1.1,  # Cost control
    "Marketing": 1.0,  # Customer acquisition
    "RiskCompliance": 1.0,  # Moat/defensibility
    "ScalingModel": 1.1,  # Unit economics proof
    "ExitAsset": 1.0,  # Liquidity event readiness
}


def pnkln_score_10fingers(scores):
    """
    scores: dict{name:0-10}
    returns: composite viability score 0-100
    """
    total_weighted_score = sum(min(10, max(0, scores.get(k, 0))) * WEIGHTS[k] for k, _ in pnkln_10FINGERS)
    max_possible_score = sum(10 * WEIGHTS[k] for k, _ in pnkln_10FINGERS)

    return round(100 * total_weighted_score / max_possible_score, 1)


def get_verdict(viability):
    if viability >= 75.0:
        return "GO (Proceed with Execution)"
    elif viability >= 60.0:
        return "CONDITIONAL (Address Red Flags, Retest)"
    else:
        return "HOLD (Fundamental Flaws - Pivot or Kill)"


def main():
    scores = {}

    # Handle arguments
    arg_idx = 1
    if len(sys.argv) > 1:
        if sys.argv[1] == "--score":
            arg_idx = 2

        if len(sys.argv) > arg_idx:
            try:
                # Handle single quoted JSON string from CLI
                json_str = sys.argv[arg_idx]
                scores = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON input: {e}")
                sys.exit(1)

    if not scores:
        # Interactive Mode
        print("\n🖐  pnkln 10 FINGERS AUDIT  🖐")
        print("Rate each dimension from 0-10.\n")

        for category, description in pnkln_10FINGERS:
            while True:
                try:
                    val = input(f"[{category}] {description} (0-10): ")
                    val_float = float(val)
                    if 0 <= val_float <= 10:
                        scores[category] = val_float
                        break
                    print("Please enter a number between 0 and 10.")
                except ValueError:
                    print("Invalid input.")

    viability = pnkln_score_10fingers(scores)
    verdict = get_verdict(viability)

    print("\n" + "=" * 40)
    print(f" VIABILITY SCORE: {viability}")
    print(f" VERDICT:         {verdict}")
    print("=" * 40 + "\n")

    # Dump Report
    report = {"scores": scores, "viability": viability, "verdict": verdict, "details": pnkln_10FINGERS}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
