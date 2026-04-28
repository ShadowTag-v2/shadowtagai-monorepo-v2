#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Visualize latency test results"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def load_results(json_path: Path):
    """Load results from JSON report"""
    with open(json_path) as f:
        return json.load(f)


def plot_latency_distribution(report: dict, output_path: Path):
    """Plot latency distribution histogram"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    latency = report["latency"]["successful_requests"]

    # Histogram
    ax1.hist(
        [latency["p50"], latency["p90"], latency["p99"]],
        bins=20,
        edgecolor="black",
        alpha=0.7,
    )
    ax1.axvline(report["config"]["p99_target_ms"], color="r", linestyle="--", label="P99 Target")
    ax1.set_xlabel("Latency (ms)")
    ax1.set_ylabel("Frequency")
    ax1.set_title("Latency Distribution")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Box plot
    data = [
        latency["min"],
        latency["p50"],
        latency["p90"],
        latency["p95"],
        latency["p99"],
        latency["max"],
    ]
    ax2.boxplot([data], labels=["Latency"])
    ax2.axhline(report["config"]["p99_target_ms"], color="r", linestyle="--", label="P99 Target")
    ax2.set_ylabel("Latency (ms)")
    ax2.set_title("Latency Box Plot")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved to {output_path}")


def plot_percentiles(report: dict, output_path: Path):
    """Plot latency percentiles"""
    fig, ax = plt.subplots(figsize=(10, 6))

    latency = report["latency"]["successful_requests"]
    percentiles = [0, 50, 90, 95, 99, 100]
    values = [
        latency["min"],
        latency["p50"],
        latency["p90"],
        latency["p95"],
        latency["p99"],
        latency["max"],
    ]

    ax.plot(percentiles, values, marker="o", linewidth=2, markersize=8)
    ax.axhline(
        report["config"]["p99_target_ms"],
        color="r",
        linestyle="--",
        label="P99 Target",
        linewidth=2,
    )

    # Highlight P99
    ax.scatter([99], [latency["p99"]], color="red", s=200, zorder=5)

    ax.set_xlabel("Percentile")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Latency Percentiles")
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize latency test results")
    parser.add_argument("report", type=Path, help="Path to JSON report file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results"),
        help="Output directory for plots",
    )

    args = parser.parse_args()

    # Load report
    report = load_results(args.report)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate plots
    plot_latency_distribution(report, args.output_dir / "latency_distribution.png")
    plot_percentiles(report, args.output_dir / "latency_percentiles.png")


if __name__ == "__main__":
    main()
