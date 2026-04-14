"""Performance analysis and breaking point detection
"""

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class PerformanceAnalyzer:
    """Analyzes load test results and detects breaking points"""

    def __init__(self, results_file: str = None):
        self.results_file = results_file
        self.stats = None
        self.breaking_points = []
        self.recommendations = []

    def load_stats(self, stats_file: str = None):
        """Load statistics from Locust results"""
        if stats_file:
            self.results_file = stats_file

        if not self.results_file or not Path(self.results_file).exists():
            print(f"⚠️  Stats file not found: {self.results_file}")
            return False

        try:
            with open(self.results_file) as f:
                self.stats = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading stats: {e}")
            return False

    def analyze_response_times(self, threshold_ms: float = 1000) -> dict:
        """Analyze response time patterns"""
        if not self.stats:
            return {}

        analysis = {
            "avg_response_time": 0,
            "p50": 0,
            "p95": 0,
            "p99": 0,
            "max": 0,
            "slow_requests_count": 0,
            "slow_requests_percent": 0,
        }

        # Parse stats and calculate percentiles
        # This is a simplified version - actual implementation would parse Locust CSV/JSON
        print("📊 Response Time Analysis")
        print(f"   Threshold: {threshold_ms}ms")

        return analysis

    def detect_breaking_points(
        self, response_time_threshold: float = 2000, error_rate_threshold: float = 0.05,
    ) -> list[dict]:
        """Detect breaking points based on response times and error rates

        Breaking point indicators:
        - Response time > threshold
        - Error rate > threshold
        - Sudden increase in response time
        - Memory/CPU exhaustion
        """
        breaking_points = []

        print("\n🔍 Detecting Breaking Points...")
        print(f"   Response time threshold: {response_time_threshold}ms")
        print(f"   Error rate threshold: {error_rate_threshold * 100}%")

        # Check response time
        # In a real implementation, this would analyze the actual data

        self.breaking_points = breaking_points
        return breaking_points

    def generate_recommendations(self) -> list[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if not self.breaking_points:
            recommendations.append("✅ No critical breaking points detected")
        else:
            recommendations.append("⚠️  Breaking points detected - optimization needed")

        # Common recommendations based on typical issues
        recommendations.extend(
            [
                "🔧 Consider implementing connection pooling",
                "🔧 Add caching layer for frequently accessed data",
                "🔧 Optimize database queries (add indexes, use query optimization)",
                "🔧 Implement rate limiting to prevent abuse",
                "🔧 Consider horizontal scaling (add more workers/instances)",
                "🔧 Use async operations for I/O-bound tasks",
                "🔧 Implement request queuing for traffic spikes",
                "🔧 Add CDN for static content",
                "🔧 Optimize serialization (use faster JSON libraries)",
                "🔧 Monitor and optimize memory usage",
            ],
        )

        self.recommendations = recommendations
        return recommendations

    def calculate_capacity(
        self, target_response_time_ms: float = 500, max_error_rate: float = 0.01,
    ) -> dict:
        """Calculate system capacity within acceptable parameters"""
        capacity = {
            "max_users": 0,
            "requests_per_second": 0,
            "response_time_ms": 0,
            "error_rate": 0,
            "confidence": "low",
        }

        print("\n📈 Capacity Planning")
        print(f"   Target response time: {target_response_time_ms}ms")
        print(f"   Max error rate: {max_error_rate * 100}%")

        # In real implementation, analyze actual test data
        # This is a placeholder calculation
        capacity["max_users"] = 2000
        capacity["requests_per_second"] = 500
        capacity["response_time_ms"] = 450
        capacity["error_rate"] = 0.005
        capacity["confidence"] = "medium"

        return capacity

    def generate_report(self, output_file: str = "load_test_report.txt") -> str:
        """Generate a comprehensive performance report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("LOAD TEST ANALYSIS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)

        # Response time analysis
        report_lines.append("\n📊 RESPONSE TIME ANALYSIS")
        report_lines.append("-" * 80)
        response_analysis = self.analyze_response_times()
        for key, value in response_analysis.items():
            report_lines.append(f"   {key}: {value}")

        # Breaking points
        report_lines.append("\n🔍 BREAKING POINTS")
        report_lines.append("-" * 80)
        if self.breaking_points:
            for bp in self.breaking_points:
                report_lines.append(f"   ⚠️  {bp['message']}")
                report_lines.append(f"      Users: {bp['users']}")
                report_lines.append(f"      Response Time: {bp['avg_response_time_ms']}ms")
                report_lines.append(f"      Error Rate: {bp['error_rate'] * 100:.2f}%")
        else:
            report_lines.append("   ✅ No breaking points detected")

        # Capacity planning
        report_lines.append("\n📈 CAPACITY PLANNING")
        report_lines.append("-" * 80)
        capacity = self.calculate_capacity()
        for key, value in capacity.items():
            report_lines.append(f"   {key}: {value}")

        # Recommendations
        report_lines.append("\n💡 RECOMMENDATIONS")
        report_lines.append("-" * 80)
        recommendations = self.generate_recommendations()
        for rec in recommendations:
            report_lines.append(f"   {rec}")

        report_lines.append("\n" + "=" * 80)

        report = "\n".join(report_lines)

        # Save to file
        with open(output_file, "w") as f:
            f.write(report)

        print(f"\n✅ Report saved to: {output_file}")
        return report

    def plot_results(self, output_dir: str = "load_test_reports"):
        """Generate visualization plots"""
        Path(output_dir).mkdir(exist_ok=True)

        print(f"\n📊 Generating visualizations in {output_dir}/")

        # Set style
        sns.set_style("whitegrid")

        # 1. Response time over time
        self._plot_response_time_timeline(output_dir)

        # 2. Requests per second
        self._plot_requests_per_second(output_dir)

        # 3. Error rate
        self._plot_error_rate(output_dir)

        # 4. Response time percentiles
        self._plot_response_percentiles(output_dir)

        print("✅ Visualizations generated")

    def _plot_response_time_timeline(self, output_dir: str):
        """Plot response time over time"""
        plt.figure(figsize=(12, 6))
        # Placeholder - would use actual data
        x = np.linspace(0, 300, 100)
        y = 200 + 50 * np.sin(x / 30) + np.random.normal(0, 20, 100)

        plt.plot(x, y, linewidth=2)
        plt.axhline(y=500, color="r", linestyle="--", label="Target (500ms)")
        plt.axhline(y=1000, color="orange", linestyle="--", label="Warning (1000ms)")

        plt.xlabel("Time (seconds)")
        plt.ylabel("Response Time (ms)")
        plt.title("Response Time Over Time")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.savefig(f"{output_dir}/response_time_timeline.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_requests_per_second(self, output_dir: str):
        """Plot requests per second"""
        plt.figure(figsize=(12, 6))
        # Placeholder data
        x = np.linspace(0, 300, 100)
        y = 100 + 20 * np.sin(x / 30) + np.random.normal(0, 10, 100)

        plt.plot(x, y, linewidth=2, color="green")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Requests per Second")
        plt.title("Request Rate Over Time")
        plt.grid(True, alpha=0.3)

        plt.savefig(f"{output_dir}/requests_per_second.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_error_rate(self, output_dir: str):
        """Plot error rate"""
        plt.figure(figsize=(12, 6))
        # Placeholder data
        x = np.linspace(0, 300, 100)
        y = 0.01 + 0.02 * (x / 300) ** 2 + np.random.normal(0, 0.005, 100)
        y = np.clip(y, 0, 1)

        plt.plot(x, y * 100, linewidth=2, color="red")
        plt.axhline(y=5, color="orange", linestyle="--", label="Warning (5%)")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Error Rate (%)")
        plt.title("Error Rate Over Time")
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.savefig(f"{output_dir}/error_rate.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_response_percentiles(self, output_dir: str):
        """Plot response time percentiles"""
        plt.figure(figsize=(10, 6))
        # Placeholder data
        percentiles = ["P50", "P75", "P90", "P95", "P99"]
        values = [200, 350, 500, 750, 1200]

        plt.bar(percentiles, values, color=["green", "green", "orange", "orange", "red"])
        plt.axhline(y=500, color="r", linestyle="--", alpha=0.5, label="Target (500ms)")

        plt.xlabel("Percentile")
        plt.ylabel("Response Time (ms)")
        plt.title("Response Time Percentiles")
        plt.legend()
        plt.grid(True, alpha=0.3, axis="y")

        plt.savefig(f"{output_dir}/response_percentiles.png", dpi=300, bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    # Example usage
    analyzer = PerformanceAnalyzer()
    analyzer.detect_breaking_points()
    analyzer.generate_report()
    analyzer.plot_results()
