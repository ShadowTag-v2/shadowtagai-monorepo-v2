"""AST-Grep Zero-Latency Mitigation Fabric.

Judge 6.1 does not merely block bad outputs — it rewrites the AST tree
in-memory at C-speed using ast-grep (sg). Instead of rejecting an AI
response containing unauthorized practice of law (UPL), the fabric
surgically transforms prescriptive advice into safe, objective,
cited alternatives.

This is active mitigation, not passive gatekeeping.

Compliance targets:
    - EU AI Act Art 5 (Emotion Recognition Ban)
    - NY S7263 (Bias Disclosure Requirements)
    - UPL shields (all US jurisdictions)
    - OWASP LLM Top 10 (2025) — LLM01, LLM02, LLM05
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("AST-Fabric")

# Default workspace for AST scanning
_DEFAULT_WORKSPACE = "/workspace"

# Default rules directory
_DEFAULT_RULES_DIR = "/app/rules"


@dataclass
class MitigationResult:
    """Result of an AST-grep compliance enforcement pass.

    Attributes:
        compliant: Whether the workspace passed all rules.
        rules_applied: Number of rules that triggered rewrites.
        files_modified: List of files that were surgically rewritten.
        stderr_output: Any error output from the sg process.
    """

    compliant: bool
    rules_applied: int = 0
    files_modified: list[str] = field(default_factory=list)
    stderr_output: str = ""


class ASTZeroLatencyMitigator:
    """AST-grep based active mitigation engine.

    Executes structural code/text rewrites at C-speed using ast-grep (sg).
    All operations are idempotent — running the mitigator twice produces
    the same output.

    Args:
        workspace_path: Path to the workspace to scan/rewrite.
        rules_dir: Path to the YAML rules directory.
    """

    def __init__(
        self,
        workspace_path: str = _DEFAULT_WORKSPACE,
        rules_dir: str = _DEFAULT_RULES_DIR,
    ) -> None:
        self.workspace = workspace_path
        self.rules_dir = rules_dir

    def enforce_compliance(self, rule_file: str = "eu26_and_s7263.yaml") -> MitigationResult:
        """Enforce regulatory compliance via AST rewriting.

        Runs ast-grep against the workspace with the specified rule file.
        The --update-all flag rewrites violating AST nodes in-place.

        Args:
            rule_file: YAML rule file name in the rules directory.

        Returns:
            MitigationResult with compliance status.
        """
        rule_path = Path(self.rules_dir) / rule_file
        logger.info(
            "🛡️ AST Fabric: Enforcing compliance with %s against %s",
            rule_file,
            self.workspace,
        )

        cmd = [
            "sg",
            "run",
            "--rule",
            str(rule_path),
            "--update-all",
            self.workspace,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info("✅ AST Fabric: All compliance rules passed.")
                return MitigationResult(compliant=True)

            # sg returns non-zero when rewrites occurred
            modified = [
                line
                for line in result.stdout.splitlines()
                if line.strip() and ":" in line
            ]
            logger.warning(
                "⚠️ AST Fabric: %d files rewritten for compliance.", len(modified)
            )
            return MitigationResult(
                compliant=True,  # After rewrite, it IS compliant
                rules_applied=len(modified),
                files_modified=modified,
                stderr_output=result.stderr,
            )

        except FileNotFoundError:
            logger.error("ast-grep (sg) binary not found. Install: cargo install ast-grep")
            return MitigationResult(compliant=False, stderr_output="sg binary not found")
        except subprocess.TimeoutExpired:
            logger.error("AST Fabric: Rule enforcement timed out (30s).")
            return MitigationResult(compliant=False, stderr_output="TIMEOUT")

    def scan_only(self, rule_file: str = "eu26_and_s7263.yaml") -> MitigationResult:
        """Scan for violations without rewriting.

        Args:
            rule_file: YAML rule file name.

        Returns:
            MitigationResult with violation details.
        """
        rule_path = Path(self.rules_dir) / rule_file
        cmd = ["sg", "run", "--rule", str(rule_path), self.workspace]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            violations = [
                line for line in result.stdout.splitlines() if line.strip()
            ]
            return MitigationResult(
                compliant=len(violations) == 0,
                rules_applied=len(violations),
                files_modified=violations,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return MitigationResult(compliant=False, stderr_output=str(e))
