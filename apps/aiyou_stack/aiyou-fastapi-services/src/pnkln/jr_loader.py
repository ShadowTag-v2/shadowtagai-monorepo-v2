"""
JR Rules Loader - Policy-as-Code for Judge #6

Loads JR validation rules from YAML configuration, enabling policy changes
without code deployment.

Usage:
    from pnkln.jr_loader import load_jr_config, JRConfig

    config = load_jr_config("jr_rules.yaml")
    # Use config.purpose_allowlist, config.thresholds, etc.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class JRThresholds:
    """Validation score thresholds."""

    purpose: float = 0.6
    reasons: float = 0.7
    brakes: float = 0.8


@dataclass
class JRAuditConfig:
    """Audit logging configuration."""

    log_path: str = "./logs/jr_audit.log"
    retention_days: int = 90
    alert_on_blocked: bool = True


@dataclass
class JREscalation:
    """Escalation contacts for violations."""

    governance: str = "governance@pnkln.ai"
    security: str = "security@pnkln.ai"
    finance: str = "finance@pnkln.ai"


@dataclass
class JRConfig:
    """
    Complete JR configuration loaded from YAML.

    Attributes:
        purpose_allowlist: Valid purposes that advance the mission
        min_expected_roi: Minimum ROI for REASONS validation
        min_ltv_cac: Minimum LTV:CAC ratio
        max_cost_without_erik: Max USD cost without erik_approved
        require_coverage: Required test coverage (0.0-1.0)
        thresholds: Validation score thresholds
        dangerous_keywords: Keywords that trigger BRAKES block
        sql_injection_patterns: SQL patterns that trigger BRAKES block
        audit: Audit logging configuration
        escalation: Escalation contacts
    """

    purpose_allowlist: list[str] = field(
        default_factory=lambda: [
            "shadowtag_development",
            "customer_acquisition",
            "google_partnership",
            "gate_progress",
        ]
    )
    min_expected_roi: float = 3.0
    min_ltv_cac: float = 4.0
    max_cost_without_erik: float = 10000.0
    require_coverage: float = 0.98
    thresholds: JRThresholds = field(default_factory=JRThresholds)
    dangerous_keywords: list[str] = field(
        default_factory=lambda: [
            "delete",
            "remove",
            "drop",
            "destroy",
            "kill",
            "terminate",
            "admin",
            "root",
            "sudo",
            "exec",
            "eval",
            "system",
        ]
    )
    sql_injection_patterns: list[str] = field(
        default_factory=lambda: ["drop table", "delete from", "1=1", "or 1=1"]
    )
    audit: JRAuditConfig = field(default_factory=JRAuditConfig)
    escalation: JREscalation = field(default_factory=JREscalation)

    def evaluate_purpose(self, action: dict[str, Any]) -> bool:
        """Check if action purpose is in allowlist."""
        return action.get("purpose") in set(self.purpose_allowlist)

    def evaluate_reasons(self, action: dict[str, Any]) -> bool:
        """Check if action meets financial thresholds."""
        roi = action.get("expected_roi", 0)
        ltv_cac = action.get("ltv_cac_ratio", 0)
        return roi >= self.min_expected_roi and ltv_cac >= self.min_ltv_cac

    def evaluate_brakes(self, action: dict[str, Any]) -> list[str]:
        """Check for safety violations. Returns list of violation codes."""
        violations: list[str] = []

        cost = float(action.get("cost_usd", 0))
        if cost > self.max_cost_without_erik and not action.get("erik_approved"):
            violations.append("HIGH_COST_NO_APPROVAL")

        if action.get("handles_pii") and not action.get("encryption_enabled"):
            violations.append("PII_WITHOUT_ENCRYPTION")

        if action.get("code_change"):
            coverage = action.get("test_coverage", 0.0)
            if coverage < self.require_coverage:
                violations.append(f"TEST_COVERAGE_LOW:{coverage}")

        return violations


def load_jr_config(path: str | Path | None = None) -> JRConfig:
    """
    Load JR configuration from YAML file.

    Args:
        path: Path to YAML file. If None, looks for jr_rules.yaml in:
              1. Current directory
              2. Same directory as this module
              3. Environment variable JR_RULES_PATH

    Returns:
        JRConfig instance with loaded values

    Raises:
        FileNotFoundError: If config file not found
        yaml.YAMLError: If YAML parsing fails
    """
    if path is None:
        # Try multiple locations
        candidates = [
            Path("jr_rules.yaml"),
            Path(__file__).parent / "jr_rules.yaml",
            Path(os.environ.get("JR_RULES_PATH", "")),
        ]
        for candidate in candidates:
            if candidate.exists():
                path = candidate
                break
        else:
            raise FileNotFoundError(
                "jr_rules.yaml not found. Set JR_RULES_PATH or place in current directory."
            )

    path = Path(path)
    cfg_dict = yaml.safe_load(path.read_text())

    # Parse thresholds
    thresholds_dict = cfg_dict.get("thresholds", {})
    thresholds = JRThresholds(
        purpose=thresholds_dict.get("purpose", 0.6),
        reasons=thresholds_dict.get("reasons", 0.7),
        brakes=thresholds_dict.get("brakes", 0.8),
    )

    # Parse audit config
    audit_dict = cfg_dict.get("audit", {})
    audit = JRAuditConfig(
        log_path=audit_dict.get("log_path", "./logs/jr_audit.log"),
        retention_days=audit_dict.get("retention_days", 90),
        alert_on_blocked=audit_dict.get("alert_on_blocked", True),
    )

    # Parse escalation
    esc_dict = cfg_dict.get("escalation", {})
    escalation = JREscalation(
        governance=esc_dict.get("governance", "governance@pnkln.ai"),
        security=esc_dict.get("security", "security@pnkln.ai"),
        finance=esc_dict.get("finance", "finance@pnkln.ai"),
    )

    return JRConfig(
        purpose_allowlist=cfg_dict.get("purpose_allowlist", []),
        min_expected_roi=cfg_dict.get("min_expected_roi", 3.0),
        min_ltv_cac=cfg_dict.get("min_ltv_cac", 4.0),
        max_cost_without_erik=cfg_dict.get("max_cost_without_erik", 10000.0),
        require_coverage=cfg_dict.get("require_coverage", 0.98),
        thresholds=thresholds,
        dangerous_keywords=cfg_dict.get("dangerous_keywords", []),
        sql_injection_patterns=cfg_dict.get("sql_injection_patterns", []),
        audit=audit,
        escalation=escalation,
    )


# Convenience: pre-flight check function
def jr_preflight_check(action: dict[str, Any], config: JRConfig | None = None) -> tuple[bool, str]:
    """
    Run JR pre-flight validation on an action.

    Args:
        action: Action dict with keys like purpose, expected_roi, cost_usd, etc.
        config: JRConfig instance. If None, loads from default location.

    Returns:
        (approved: bool, message: str)
    """
    if config is None:
        config = load_jr_config()

    # PURPOSE check
    if not config.evaluate_purpose(action):
        return False, f"REJECTED: Purpose '{action.get('purpose')}' not in allowlist"

    # REASONS check
    if not config.evaluate_reasons(action):
        return False, (
            f"REQUIRES_REVIEW: ROI={action.get('expected_roi')}, "
            f"LTV:CAC={action.get('ltv_cac_ratio')}"
        )

    # BRAKES check
    violations = config.evaluate_brakes(action)
    if violations:
        return False, f"REJECTED: Safety violations: {violations}"

    return True, "APPROVED: All JR checks passed"
