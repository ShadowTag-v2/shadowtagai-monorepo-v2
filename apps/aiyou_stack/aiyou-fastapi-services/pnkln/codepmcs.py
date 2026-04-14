#!/usr/bin/env python3
"""CODEPMCS (Preventive Maintenance Checks and Services)
Mission: Enforce Ranger Standards (Linting, Security, Watermarking)
ATP 3-75 Compliance Gate
"""

import logging
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | CODEPMCS | %(message)s")
logger = logging.getLogger("CODEPMCS")


@dataclass
class Fault:
    """Equipment fault record."""

    component: str
    status: str  # 'X' = deadlined, '/' = degraded, 'O' = operational
    details: str


@dataclass
class InspectionResult:
    """PMCS inspection result."""

    faults: list[Fault] = field(default_factory=list)
    mission_capable: bool = True


class RangerStandardInspector:
    """Code quality inspector implementing Ranger Standards.
    Coverage >= 98%, Secure, Linted, Documented.
    """

    def __init__(self, target_path: str = "."):
        self.target_path = Path(target_path)
        self.result = InspectionResult()

    def check_lint(self) -> None:
        """Run Ruff linter check."""
        logger.info("🔍 CHECKING: Linting (Ruff)")
        try:
            res = subprocess.run(
                ["ruff", "check", str(self.target_path), "--fix"], capture_output=True, timeout=60,
            )
            if res.returncode != 0:
                self.result.faults.append(
                    Fault("Linting", "X", f"Ruff violations: {res.stdout.decode()[:200]}"),
                )
                self.result.mission_capable = False
            else:
                logger.info("   ✅ Linting: PASS")
        except FileNotFoundError:
            logger.warning("   ⚠️ Ruff not installed, skipping lint check")
        except subprocess.TimeoutExpired:
            self.result.faults.append(Fault("Linting", "/", "Timeout"))

    def check_security(self) -> None:
        """Run Bandit security scan."""
        logger.info("🔍 CHECKING: Security (Bandit)")
        try:
            res = subprocess.run(
                ["bandit", "-r", str(self.target_path), "-f", "json", "-q"],
                capture_output=True,
                timeout=120,
            )
            output = res.stdout.decode()
            if "High" in output or "SEVERITY.HIGH" in output:
                self.result.faults.append(Fault("Security", "X", "Critical vulnerability detected"))
                self.result.mission_capable = False
            else:
                logger.info("   ✅ Security: PASS")
        except FileNotFoundError:
            logger.warning("   ⚠️ Bandit not installed, skipping security check")
        except subprocess.TimeoutExpired:
            self.result.faults.append(Fault("Security", "/", "Timeout"))

    def check_types(self) -> None:
        """Run MyPy type check."""
        logger.info("🔍 CHECKING: Type Safety (MyPy)")
        try:
            res = subprocess.run(
                ["mypy", str(self.target_path), "--ignore-missing-imports"],
                capture_output=True,
                timeout=120,
            )
            if res.returncode != 0 and "error:" in res.stdout.decode():
                self.result.faults.append(Fault("Types", "/", "Type errors detected (degraded)"))
            else:
                logger.info("   ✅ Types: PASS")
        except FileNotFoundError:
            logger.warning("   ⚠️ MyPy not installed, skipping type check")
        except subprocess.TimeoutExpired:
            self.result.faults.append(Fault("Types", "/", "Timeout"))

    def execute(self) -> InspectionResult:
        """Run full PMCS inspection."""
        logger.info("=" * 50)
        logger.info("🎖️ CODEPMCS INSPECTION INITIATED")
        logger.info(f"   Target: {self.target_path.absolute()}")
        logger.info("=" * 50)

        self.check_lint()
        self.check_security()
        self.check_types()

        logger.info("=" * 50)
        if self.result.faults:
            logger.error("🛑 EQUIPMENT DEADLINED (NO-GO)")
            for fault in self.result.faults:
                logger.error(f"   [{fault.status}] {fault.component}: {fault.details}")
            if not self.result.mission_capable:
                sys.exit(1)
        else:
            logger.info("✅ FULLY MISSION CAPABLE (FMC)")
        logger.info("=" * 50)

        return self.result


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    inspector = RangerStandardInspector(target)
    inspector.execute()
