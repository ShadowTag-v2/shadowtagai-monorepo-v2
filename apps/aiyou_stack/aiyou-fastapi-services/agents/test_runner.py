"""
TestRunner - Automated test execution agent.
Runs pytest with coverage and benchmarks.
"""

import json
import subprocess
from pathlib import Path


class TestRunner:
    """Automated test execution and reporting."""

    def __init__(self, repo_path: str = "./"):
        self.repo_path = Path(repo_path)
        self.results = {}

    def run_pytest(self, test_path: str = "tests/", verbose: bool = True) -> dict:
        """Run pytest with JSON output."""
        print(f"///▞ TEST RUNNER :: Running pytest on {test_path}")

        args = ["python3", "-m", "pytest", test_path, "--tb=short", "-q"]

        if verbose:
            args.append("-v")

        try:
            result = subprocess.run(
                args, capture_output=True, text=True, cwd=self.repo_path, timeout=300
            )

            # Parse output
            passed = result.stdout.count(" PASSED")
            failed = result.stdout.count(" FAILED")
            errors = result.stdout.count(" ERROR")

            self.results["pytest"] = {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "exit_code": result.returncode,
                "output": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            }

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "passed": passed,
                "failed": failed,
                "errors": errors,
            }

        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Tests exceeded 5 minute timeout"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_coverage(self, test_path: str = "tests/", source: str = "src/") -> dict:
        """Run pytest with coverage report."""
        print("///▞ TEST RUNNER :: Running coverage analysis")

        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pytest",
                    test_path,
                    f"--cov={source}",
                    "--cov-report=json",
                    "-q",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=300,
            )

            # Read coverage report
            cov_file = self.repo_path / "coverage.json"
            if cov_file.exists():
                with open(cov_file) as f:
                    cov_data = json.load(f)

                total_coverage = cov_data.get("totals", {}).get("percent_covered", 0)
                self.results["coverage"] = {
                    "total": round(total_coverage, 2),
                    "files": len(cov_data.get("files", {})),
                }

                return {
                    "status": "complete",
                    "coverage_percent": round(total_coverage, 2),
                    "files_covered": len(cov_data.get("files", {})),
                }

            return {"status": "no_report", "message": "Coverage report not generated"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_benchmark(self, test_path: str = "tests/") -> dict:
        """Run pytest-benchmark for performance tests."""
        print("///▞ TEST RUNNER :: Running benchmarks")

        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pytest",
                    test_path,
                    "--benchmark-only",
                    "--benchmark-json=benchmark.json",
                    "-q",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=300,
            )

            # Read benchmark report
            bench_file = self.repo_path / "benchmark.json"
            if bench_file.exists():
                with open(bench_file) as f:
                    bench_data = json.load(f)

                benchmarks = bench_data.get("benchmarks", [])
                self.results["benchmark"] = {
                    "count": len(benchmarks),
                    "results": [
                        {"name": b["name"], "mean": b["stats"]["mean"], "ops": b["stats"]["ops"]}
                        for b in benchmarks[:10]
                    ],
                }

                return {"status": "complete", "benchmarks_run": len(benchmarks)}

            return {"status": "no_benchmarks", "message": "No benchmark tests found"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def full_test_suite(self, test_path: str = "tests/") -> dict:
        """Run complete test suite with all analysis."""
        print("///▞ TEST RUNNER :: Starting full test suite")

        results = {
            "pytest": self.run_pytest(test_path),
            "coverage": self.run_coverage(test_path),
            "benchmark": self.run_benchmark(test_path),
        }

        # Calculate overall status
        all_passed = results["pytest"].get("status") == "success"
        coverage_ok = results["coverage"].get("coverage_percent", 0) >= 70

        status = "PASS" if all_passed and coverage_ok else "FAIL"

        print(f"///▞ TEST RUNNER :: Suite complete. Status: {status}")

        return {
            "status": status,
            "tests_passed": results["pytest"].get("passed", 0),
            "tests_failed": results["pytest"].get("failed", 0),
            "coverage_percent": results["coverage"].get("coverage_percent", 0),
            "details": results,
        }

    def get_report(self) -> str:
        """Generate markdown test report."""
        report = "# Test Runner Report\n\n"

        if "pytest" in self.results:
            r = self.results["pytest"]
            report += "## Test Results\n"
            report += f"- Passed: {r.get('passed', 0)}\n"
            report += f"- Failed: {r.get('failed', 0)}\n"
            report += f"- Errors: {r.get('errors', 0)}\n\n"

        if "coverage" in self.results:
            r = self.results["coverage"]
            report += "## Coverage\n"
            report += f"- Total: {r.get('total', 0)}%\n"
            report += f"- Files: {r.get('files', 0)}\n\n"

        return report


if __name__ == "__main__":
    runner = TestRunner()
    results = runner.full_test_suite()
    print(json.dumps(results, indent=2))
