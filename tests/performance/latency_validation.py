"""
Latency Validation Script for Judge #6 HITL System
Validates p99 ≤90ms performance target

Usage:
    python tests/performance/latency_validation.py

Output:
    - Latency distribution (p50, p90, p95, p99, p100)
    - Pass/fail for p99 ≤90ms target
    - Performance breakdown by judge vertical
    - CSV export for analysis
"""

import time
import statistics
import json
from typing import List, Dict, Any
from datetime import datetime
from src.judges import JudgeFactory, JudgeRequest, JudgeType


class LatencyValidator:
    """Validate Judge #6 latency performance"""

    def __init__(self, num_samples: int = 1000):
        """
        Initialize validator

        Args:
            num_samples: Number of decisions to test (default: 1000)
        """
        self.num_samples = num_samples
        self.results: dict[JudgeType, list[float]] = {
            judge_type: [] for judge_type in JudgeType
        }

    def generate_sample_request(self, judge_type: JudgeType, idx: int) -> JudgeRequest:
        """Generate sample request for testing"""
        contexts = {
            JudgeType.FIN: {
                "amount_usd": 50000 + (idx % 50000),
                "vendor_status": ["new", "approved", "unverified"][idx % 3],
                "purchase_order": f"PO-{idx}" if idx % 2 == 0 else None,
                "destination_country": ["US", "UK", "Unknown"][idx % 3]
            },
            JudgeType.CASE: {
                "case_value_usd": 100000 + (idx % 900000),
                "case_type": ["contract_dispute", "litigation", "settlement"][idx % 3],
                "conflict_check_passed": idx % 4 != 0,
                "probability_of_success": 0.3 + (idx % 7) * 0.1
            },
            JudgeType.LAW: {
                "compliance_area": ["eu_ai_act", "gdpr", "ca_sb53", "export_control"][idx % 4],
                "ai_system_type": ["biometric_identification", "credit_scoring"][idx % 2] if idx % 2 == 0 else None,
                "legal_review_completed": idx % 3 != 0,
                "dpia_completed": idx % 2 == 0
            },
            JudgeType.FRAUD: {
                "fraud_score": 0.1 + (idx % 8) * 0.1,
                "identity_verified": idx % 2 == 0,
                "geo_location_mismatch": idx % 3 == 0,
                "velocity_check_failed": idx % 5 == 0,
                "amount_usd": 1000 + (idx % 9000)
            }
        }

        return JudgeRequest(
            request_id=f"perf_test_{judge_type.value}_{idx}",
            judge_type=judge_type,
            action_type="test_action",
            context=contexts[judge_type],
            requested_by="performance_test@example.com"
        )

    def run_validation(self, verbose: bool = True) -> dict[str, Any]:
        """
        Run latency validation

        Args:
            verbose: Print progress messages

        Returns:
            Validation results dictionary
        """
        if verbose:
            print("Judge #6 Latency Validation")
            print(f"{'=' * 60}")
            print("Target: p99 ≤90ms")
            print(f"Samples per vertical: {self.num_samples // len(JudgeType)}")
            print()

        # Run tests for each judge vertical
        for judge_type in JudgeType:
            if verbose:
                print(f"Testing {judge_type.value}... ", end="", flush=True)

            judge = JudgeFactory.get_judge(judge_type)
            samples_per_judge = self.num_samples // len(JudgeType)

            for i in range(samples_per_judge):
                request = self.generate_sample_request(judge_type, i)

                # Measure latency
                start = time.perf_counter()
                response = judge.judge(request)
                end = time.perf_counter()

                latency_ms = (end - start) * 1000
                self.results[judge_type].append(latency_ms)

            if verbose:
                print(f"✓ ({len(self.results[judge_type])} samples)")

        # Calculate statistics
        results = self._calculate_statistics(verbose)

        return results

    def _calculate_statistics(self, verbose: bool) -> dict[str, Any]:
        """Calculate latency statistics"""
        all_latencies = []
        for latencies in self.results.values():
            all_latencies.extend(latencies)

        all_latencies_sorted = sorted(all_latencies)

        # Overall statistics
        overall_stats = {
            "total_samples": len(all_latencies),
            "mean_ms": statistics.mean(all_latencies),
            "median_ms": statistics.median(all_latencies),
            "stddev_ms": statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0,
            "min_ms": min(all_latencies),
            "max_ms": max(all_latencies),
            "p50_ms": all_latencies_sorted[int(len(all_latencies_sorted) * 0.50)],
            "p90_ms": all_latencies_sorted[int(len(all_latencies_sorted) * 0.90)],
            "p95_ms": all_latencies_sorted[int(len(all_latencies_sorted) * 0.95)],
            "p99_ms": all_latencies_sorted[int(len(all_latencies_sorted) * 0.99)],
            "p100_ms": all_latencies_sorted[-1],
        }

        # Per-vertical statistics
        vertical_stats = {}
        for judge_type, latencies in self.results.items():
            if not latencies:
                continue

            sorted_latencies = sorted(latencies)
            vertical_stats[judge_type.value] = {
                "samples": len(latencies),
                "mean_ms": statistics.mean(latencies),
                "p50_ms": sorted_latencies[int(len(sorted_latencies) * 0.50)],
                "p99_ms": sorted_latencies[int(len(sorted_latencies) * 0.99)],
                "max_ms": max(latencies),
            }

        # Pass/fail determination
        p99_target = 90.0
        passed = overall_stats["p99_ms"] <= p99_target

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "target_p99_ms": p99_target,
            "passed": passed,
            "overall": overall_stats,
            "by_vertical": vertical_stats,
        }

        if verbose:
            self._print_results(results)

        return results

    def _print_results(self, results: dict[str, Any]):
        """Print validation results"""
        print()
        print(f"{'=' * 60}")
        print("OVERALL RESULTS")
        print(f"{'=' * 60}")

        overall = results["overall"]
        print(f"Total samples:  {overall['total_samples']}")
        print(f"Mean latency:   {overall['mean_ms']:.2f}ms")
        print(f"Std deviation:  {overall['stddev_ms']:.2f}ms")
        print()

        print("LATENCY DISTRIBUTION:")
        print(f"  p50 (median): {overall['p50_ms']:.2f}ms")
        print(f"  p90:          {overall['p90_ms']:.2f}ms")
        print(f"  p95:          {overall['p95_ms']:.2f}ms")
        print(f"  p99:          {overall['p99_ms']:.2f}ms  {'✓ PASS' if results['passed'] else '✗ FAIL'}")
        print(f"  p100 (max):   {overall['p100_ms']:.2f}ms")
        print()

        print(f"{'=' * 60}")
        print("BY VERTICAL")
        print(f"{'=' * 60}")

        for judge_type, stats in results["by_vertical"].items():
            status = "✓" if stats["p99_ms"] <= results["target_p99_ms"] else "✗"
            print(f"{judge_type:12} {status}  p50: {stats['p50_ms']:5.2f}ms  p99: {stats['p99_ms']:5.2f}ms  max: {stats['max_ms']:5.2f}ms")

        print()
        print(f"{'=' * 60}")
        if results["passed"]:
            print(f"✓ VALIDATION PASSED: p99 = {overall['p99_ms']:.2f}ms ≤ {results['target_p99_ms']}ms")
        else:
            print(f"✗ VALIDATION FAILED: p99 = {overall['p99_ms']:.2f}ms > {results['target_p99_ms']}ms")
        print(f"{'=' * 60}")

    def export_results(self, results: dict[str, Any], filename: str = "latency_validation_results.json"):
        """Export results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults exported to: {filename}")

    def export_csv(self, filename: str = "latency_raw_data.csv"):
        """Export raw latency data to CSV"""
        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["judge_type", "sample_idx", "latency_ms"])

            for judge_type, latencies in self.results.items():
                for idx, latency in enumerate(latencies):
                    writer.writerow([judge_type.value, idx, f"{latency:.4f}"])

        print(f"Raw data exported to: {filename}")


def main():
    """Run latency validation"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate Judge #6 latency performance")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples to test (default: 1000)")
    parser.add_argument("--export-json", action="store_true", help="Export results to JSON")
    parser.add_argument("--export-csv", action="store_true", help="Export raw data to CSV")
    parser.add_argument("--quiet", action="store_true", help="Suppress output (just return exit code)")

    args = parser.parse_args()

    validator = LatencyValidator(num_samples=args.samples)
    results = validator.run_validation(verbose=not args.quiet)

    if args.export_json:
        validator.export_results(results)

    if args.export_csv:
        validator.export_csv()

    # Exit with status code
    exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
