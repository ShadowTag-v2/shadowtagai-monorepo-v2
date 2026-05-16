#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Load Test Runner
Comprehensive load testing tool for AIYou FastAPI Services
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

from load_tests.scenarios import get_scenario, list_scenarios, LoadTestScenario
from load_tests.analyzer import PerformanceAnalyzer


class LoadTestRunner:
  """Main load test runner"""

  def __init__(self, host: str = "http://localhost:8000"):
    self.host = host
    self.results_dir = Path("load_test_reports")
    self.results_dir.mkdir(exist_ok=True)

  def run_scenario(self, scenario: LoadTestScenario, headless: bool = True) -> bool:
    """Run a load test scenario"""
    print("\n" + "=" * 80)
    print(f"🚀 RUNNING LOAD TEST: {scenario.name}")
    print("=" * 80)
    print(f"Description: {scenario.description}")
    print(f"Users: {scenario.users}")
    print(f"Spawn Rate: {scenario.spawn_rate}/sec")
    print(f"Duration: {scenario.duration}s")
    print(f"Target Host: {self.host}")
    print(f"User Class: {scenario.user_class}")
    print("=" * 80)

    # Prepare output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_prefix = (
      self.results_dir / f"{scenario.name.lower().replace(' ', '_')}_{timestamp}"
    )

    # Build locust command
    cmd = [
      "locust",
      "-f",
      "load_tests/locustfile.py",
      "--host",
      self.host,
      "--users",
      str(scenario.users),
      "--spawn-rate",
      str(scenario.spawn_rate),
      "--run-time",
      f"{scenario.duration}s",
      "--csv",
      str(csv_prefix),
      "--html",
      f"{csv_prefix}.html",
    ]

    if headless:
      cmd.append("--headless")

    # Add user class if specified
    if scenario.user_class and scenario.user_class != "AIYouUser":
      cmd.extend(["--class-picker", scenario.user_class])

    print(f"\n🔧 Running command: {' '.join(cmd)}\n")

    try:
      # Run locust
      result = subprocess.run(cmd, check=True)

      print("\n✅ Load test completed successfully!")

      # Analyze results
      self._analyze_results(csv_prefix, scenario)

      return True

    except subprocess.CalledProcessError as e:
      print(f"\n❌ Load test failed with exit code {e.returncode}")
      return False
    except KeyboardInterrupt:
      print("\n⚠️  Load test interrupted by user")
      return False

  def run_custom(
    self,
    users: int,
    spawn_rate: int,
    duration: int,
    user_class: str = "AIYouUser",
    headless: bool = True,
  ) -> bool:
    """Run a custom load test"""
    scenario = LoadTestScenario(
      name="Custom Test",
      description=f"Custom load test with {users} users",
      users=users,
      spawn_rate=spawn_rate,
      duration=duration,
      user_class=user_class,
      host=self.host,
    )

    return self.run_scenario(scenario, headless)

  def run_breaking_point_test(self) -> bool:
    """
    Run a breaking point test - incrementally increase load until system breaks
    """
    print("\n" + "=" * 80)
    print("🔍 BREAKING POINT TEST")
    print("=" * 80)
    print("This test will incrementally increase load to find the breaking point")
    print("=" * 80)

    # Define incremental stages
    stages = [
      (100, 10, 60),  # 100 users
      (250, 25, 60),  # 250 users
      (500, 50, 60),  # 500 users
      (1000, 100, 60),  # 1,000 users
      (2500, 250, 60),  # 2,500 users
      (5000, 500, 60),  # 5,000 users
      (7500, 500, 60),  # 7,500 users
      (10000, 500, 60),  # 10,000 users
    ]

    breaking_point_found = False
    breaking_point_users = 0

    for users, spawn_rate, duration in stages:
      print(f"\n📊 Testing with {users} users...")

      scenario = LoadTestScenario(
        name=f"Breaking Point Stage: {users} users",
        description=f"Breaking point test stage with {users} users",
        users=users,
        spawn_rate=spawn_rate,
        duration=duration,
        user_class="AIYouUser",
        host=self.host,
      )

      success = self.run_scenario(scenario, headless=True)

      if not success:
        breaking_point_found = True
        breaking_point_users = users
        print(f"\n⚠️  Breaking point found at {users} users!")
        break

      # Small pause between stages
      print("\n⏳ Waiting 10 seconds before next stage...")
      time.sleep(10)

    if breaking_point_found:
      print(f"\n🎯 BREAKING POINT DETECTED: {breaking_point_users} users")
    else:
      print(f"\n✅ System handled all stages up to {stages[-1][0]} users!")

    return True

  def _analyze_results(self, csv_prefix: Path, scenario: LoadTestScenario):
    """Analyze load test results"""
    print("\n📊 Analyzing results...")

    # Check if stats file exists
    stats_file = f"{csv_prefix}_stats.csv"

    if Path(stats_file).exists():
      analyzer = PerformanceAnalyzer(results_file=stats_file)

      # Detect breaking points
      analyzer.detect_breaking_points()

      # Generate report
      report_file = f"{csv_prefix}_report.txt"
      analyzer.generate_report(output_file=report_file)

      # Generate plots
      plot_dir = self.results_dir / f"{csv_prefix.stem}_plots"
      analyzer.plot_results(output_dir=str(plot_dir))

      print(f"\n📄 Report: {report_file}")
      print(f"📊 Plots: {plot_dir}")
      print(f"📈 HTML Report: {csv_prefix}.html")
    else:
      print("⚠️  No stats file found for analysis")

  def list_available_scenarios(self):
    """List all available scenarios"""
    print("\n" + "=" * 80)
    print("AVAILABLE LOAD TEST SCENARIOS")
    print("=" * 80)

    scenarios = list_scenarios()
    for name, scenario in scenarios.items():
      print(f"\n🎯 {name}")
      print(f"   Name: {scenario.name}")
      print(f"   Description: {scenario.description}")
      print(f"   Users: {scenario.users}")
      print(f"   Duration: {scenario.duration}s")

    print("\n" + "=" * 80)


def main():
  """Main entry point"""
  parser = argparse.ArgumentParser(
    description="Load Test Runner for AIYou FastAPI Services",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Run a predefined scenario
  python run_load_test.py --scenario smoke

  # Run a custom test
  python run_load_test.py --users 500 --spawn-rate 25 --duration 120

  # Run breaking point test
  python run_load_test.py --breaking-point

  # List available scenarios
  python run_load_test.py --list-scenarios

  # Run with web UI (non-headless)
  python run_load_test.py --scenario medium --no-headless
        """,
  )

  parser.add_argument(
    "--host",
    default="http://localhost:8000",
    help="Target host URL (default: http://localhost:8000)",
  )

  parser.add_argument(
    "--scenario",
    choices=[
      "smoke",
      "light",
      "medium",
      "heavy",
      "stress",
      "spike",
      "endurance",
      "breaking_point",
    ],
    help="Predefined scenario to run",
  )

  parser.add_argument("--users", type=int, help="Number of concurrent users")

  parser.add_argument("--spawn-rate", type=int, help="User spawn rate per second")

  parser.add_argument("--duration", type=int, help="Test duration in seconds")

  parser.add_argument(
    "--user-class",
    default="AIYouUser",
    choices=["AIYouUser", "QuickLoadUser", "StressTestUser"],
    help="User class to use for testing",
  )

  parser.add_argument(
    "--breaking-point",
    action="store_true",
    help="Run breaking point test (incrementally increase load)",
  )

  parser.add_argument(
    "--list-scenarios", action="store_true", help="List all available scenarios"
  )

  parser.add_argument(
    "--no-headless",
    action="store_true",
    help="Run with web UI instead of headless mode",
  )

  args = parser.parse_args()

  # Create runner
  runner = LoadTestRunner(host=args.host)

  # List scenarios
  if args.list_scenarios:
    runner.list_available_scenarios()
    return 0

  # Breaking point test
  if args.breaking_point:
    success = runner.run_breaking_point_test()
    return 0 if success else 1

  # Run scenario
  if args.scenario:
    scenario = get_scenario(args.scenario)
    if scenario:
      scenario.host = args.host
      success = runner.run_scenario(scenario, headless=not args.no_headless)
      return 0 if success else 1
    else:
      print(f"❌ Unknown scenario: {args.scenario}")
      return 1

  # Custom test
  if args.users and args.spawn_rate and args.duration:
    success = runner.run_custom(
      users=args.users,
      spawn_rate=args.spawn_rate,
      duration=args.duration,
      user_class=args.user_class,
      headless=not args.no_headless,
    )
    return 0 if success else 1

  # No valid arguments
  parser.print_help()
  return 1


if __name__ == "__main__":
  sys.exit(main())
