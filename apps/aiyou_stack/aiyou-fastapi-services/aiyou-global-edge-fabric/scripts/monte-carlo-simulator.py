#!/usr/bin/env python3
"""ShadowTag-v4 Monte Carlo Valuation Simulator

Runs 10,000 simulations to model exit valuation uncertainty.
Accounts for revenue volatility, margin variance, and multiple ranges.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Configuration
SIMULATIONS = 10000
REVENUE_VOLATILITY = 0.25  # 25% std dev
MARGIN_VOLATILITY = 0.10  # 10% std dev
MULTIPLE_MIN = 8
MULTIPLE_MAX = 15
TARGET_YEAR = 2030
SCENARIO = "base"  # conservative, base, aggressive


def load_projections():
    """Load revenue projections from JSON"""
    path = Path(__file__).parent.parent / "models" / "revenue-projections.json"
    with open(path) as f:
        return json.load(f)


def simulate_exit_value(base_revenue, base_margin, n_sims=SIMULATIONS):
    """Run Monte Carlo simulation for exit valuation

    Returns:
        dict with percentiles (p10, p50, p90) and full distribution

    """
    np.random.seed(42)  # Reproducible

    # Generate revenue samples (lognormal distribution)
    revenue_samples = np.random.lognormal(
        mean=np.log(base_revenue),
        sigma=REVENUE_VOLATILITY,
        size=n_sims,
    )

    # Generate margin samples (normal, clipped to [0, 1])
    margin_samples = np.random.normal(loc=base_margin, scale=MARGIN_VOLATILITY, size=n_sims)
    margin_samples = np.clip(margin_samples, 0.15, 0.50)  # Realistic bounds

    # Generate multiple samples (uniform)
    multiple_samples = np.random.uniform(low=MULTIPLE_MIN, high=MULTIPLE_MAX, size=n_sims)

    # Calculate EBITDA and valuations
    ebitda_samples = revenue_samples * margin_samples
    valuation_samples = ebitda_samples * multiple_samples

    # Compute percentiles
    results = {
        "p10": np.percentile(valuation_samples, 10),
        "p25": np.percentile(valuation_samples, 25),
        "p50": np.percentile(valuation_samples, 50),
        "p75": np.percentile(valuation_samples, 75),
        "p90": np.percentile(valuation_samples, 90),
        "mean": np.mean(valuation_samples),
        "std": np.std(valuation_samples),
        "distribution": valuation_samples,
    }

    return results


def generate_report(results, projections):
    """Generate markdown report"""
    print("\n" + "=" * 60)
    print(f"ShadowTag-v4 Monte Carlo Simulation Results ({SIMULATIONS:,} runs)")
    print("=" * 60 + "\n")

    base_rev = projections["total_revenue"][str(TARGET_YEAR)][SCENARIO]
    base_margin = projections["margins"]["ebitda_margin"][str(TARGET_YEAR)]

    print(f"Base Case ({SCENARIO.capitalize()}):")
    print(f"  Revenue: ${base_rev / 1e9:.2f}B")
    print(f"  EBITDA Margin: {base_margin * 100:.1f}%")
    print(f"  EBITDA: ${(base_rev * base_margin) / 1e9:.2f}B")
    print(f"\nValuation Multiples: {MULTIPLE_MIN}× – {MULTIPLE_MAX}× EBITDA\n")

    print("Exit Valuation Distribution:")
    print(f"  10th percentile (bear):  ${results['p10'] / 1e9:.2f}B")
    print(f"  25th percentile:         ${results['p25'] / 1e9:.2f}B")
    print(f"  50th percentile (base):  ${results['p50'] / 1e9:.2f}B")
    print(f"  75th percentile:         ${results['p75'] / 1e9:.2f}B")
    print(f"  90th percentile (bull):  ${results['p90'] / 1e9:.2f}B")
    print(f"\n  Mean:                    ${results['mean'] / 1e9:.2f}B")
    print(f"  Std Dev:                 ${results['std'] / 1e9:.2f}B")

    # Founder wealth (60% equity retained)
    founder_equity = 0.60
    print(f"\nFounder Wealth @ {int(founder_equity * 100)}% Equity Retained:")
    print(f"  10th percentile:         ${results['p10'] * founder_equity / 1e9:.2f}B")
    print(f"  50th percentile:         ${results['p50'] * founder_equity / 1e9:.2f}B")
    print(f"  90th percentile:         ${results['p90'] * founder_equity / 1e9:.2f}B")

    # Probability of outcomes
    prob_10b = (results["distribution"] >= 10e9).sum() / SIMULATIONS * 100
    prob_20b = (results["distribution"] >= 20e9).sum() / SIMULATIONS * 100
    prob_30b = (results["distribution"] >= 30e9).sum() / SIMULATIONS * 100

    print("\nProbability of Exit >= $XB:")
    print(f"  >= $10B: {prob_10b:.1f}%")
    print(f"  >= $20B: {prob_20b:.1f}%")
    print(f"  >= $30B: {prob_30b:.1f}%")

    print("\n" + "=" * 60 + "\n")


def plot_distribution(results):
    """Generate histogram of valuation distribution"""
    plt.figure(figsize=(12, 6))

    # Histogram
    plt.hist(
        results["distribution"] / 1e9,
        bins=50,
        alpha=0.7,
        color="steelblue",
        edgecolor="black",
    )

    # Add percentile lines
    plt.axvline(results["p10"] / 1e9, color="red", linestyle="--", linewidth=2, label="p10 (bear)")
    plt.axvline(
        results["p50"] / 1e9,
        color="green",
        linestyle="--",
        linewidth=2,
        label="p50 (base)",
    )
    plt.axvline(
        results["p90"] / 1e9,
        color="orange",
        linestyle="--",
        linewidth=2,
        label="p90 (bull)",
    )

    plt.xlabel("Exit Valuation ($B)", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.title(
        f"ShadowTag-v4 Exit Valuation Distribution ({SIMULATIONS:,} Monte Carlo Simulations)",
        fontsize=14,
        fontweight="bold",
    )
    plt.legend(fontsize=10)
    plt.grid(axis="y", alpha=0.3)

    # Save
    output_path = Path(__file__).parent.parent / "models" / "valuation-distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Chart saved to: {output_path}")

    # Show
    plt.show()


def main():
    # Load data
    projections = load_projections()

    # Extract base case
    base_revenue = projections["total_revenue"][str(TARGET_YEAR)][SCENARIO]
    base_margin = projections["margins"]["ebitda_margin"][str(TARGET_YEAR)]

    # Run simulation
    results = simulate_exit_value(base_revenue, base_margin)

    # Report
    generate_report(results, projections)

    # Plot
    plot_distribution(results)

    # Save results
    output = {
        "scenario": SCENARIO,
        "target_year": TARGET_YEAR,
        "simulations": SIMULATIONS,
        "base_revenue": base_revenue,
        "base_margin": base_margin,
        "results": {
            "p10": results["p10"],
            "p25": results["p25"],
            "p50": results["p50"],
            "p75": results["p75"],
            "p90": results["p90"],
            "mean": results["mean"],
            "std": results["std"],
        },
    }

    output_path = Path(__file__).parent.parent / "models" / "monte-carlo-results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
