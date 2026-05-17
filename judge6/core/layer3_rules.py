# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Layer 3: Rules Engine (Hard Gates)
Black-and-white enforcement of compliance rules
No AI, no ambiguity - just deterministic gates
"""

import re
from typing import Any
import yaml
from pathlib import Path

from ..models.database import RiskLevel
from ..core.config import settings


class Rule:
  """Single enforcement rule"""

  def __init__(self, name: str, pattern: str, risk_level: str, action: str):
    self.name = name
    self.pattern = re.compile(pattern, re.IGNORECASE)
    self.risk_level = RiskLevel[risk_level.upper()]
    self.action = action  # "deny" or "warn"

  def check(self, text: str) -> bool:
    """Check if rule is violated"""
    return bool(self.pattern.search(text))


class RulesEngineLayer:
  """
  Layer 3: Hard gates using deterministic rules
  Final enforcement layer - most restrictive
  """

  def __init__(self):
    """Initialize rules from policy corpus"""
    self.rules: list[Rule] = []
    self._load_default_rules()

  def _load_default_rules(self):
    """Load default ATP 5-19 rules"""
    # Check if custom policy file exists
    policy_path = Path(settings.DEFAULT_POLICY_CORPUS_PATH)

    if policy_path.exists():
      try:
        with open(policy_path) as f:
          policies = yaml.safe_load(f)
          self._parse_policies(policies)
        print(f"Layer 3: Loaded {len(self.rules)} rules from {policy_path}")
      except Exception as e:
        print(f"Layer 3: Failed to load policies: {e}")
        self._load_fallback_rules()
    else:
      print("Layer 3: Using fallback built-in rules")
      self._load_fallback_rules()

  def _parse_policies(self, policies: dict[str, Any]):
    """Parse YAML policies into Rule objects"""
    for policy in policies.get("rules", []):
      rule = Rule(
        name=policy["name"],
        pattern=policy["pattern"],
        risk_level=policy["risk_level"],
        action=policy["action"],
      )
      self.rules.append(rule)

  def _load_fallback_rules(self):
    """Load hard-coded fallback rules (for development)"""
    # ATP 5-19 BRAKES (Hard Stops)
    fallback_rules = [
      # CATASTROPHIC: Physical harm
      {
        "name": "Physical Harm",
        "pattern": r"\b(kill|murder|harm|weapon|bomb|explosive|poison)\b",
        "risk_level": "catastrophic",
        "action": "deny",
      },
      # CATASTROPHIC: Illegal activity
      {
        "name": "Illegal Activity",
        "pattern": r"\b(illegal|fraud|money laundering|tax evasion|terrorism)\b",
        "risk_level": "catastrophic",
        "action": "deny",
      },
      # CRITICAL: PII exposure
      {
        "name": "SSN Exposure",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "risk_level": "critical",
        "action": "deny",
      },
      {
        "name": "Credit Card Exposure",
        "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        "risk_level": "critical",
        "action": "deny",
      },
      # CRITICAL: Prompt injection
      {
        "name": "Prompt Injection",
        "pattern": r"\b(ignore previous|ignore all instructions|disregard|new instructions)\b",
        "risk_level": "critical",
        "action": "deny",
      },
      # CRITICAL: Credentials
      {
        "name": "Password Exposure",
        "pattern": r"\b(password|passwd|pwd)\s*[:=]\s*\S+",
        "risk_level": "critical",
        "action": "deny",
      },
      # MODERATE: Sensitive data
      {
        "name": "Medical Information",
        "pattern": r"\b(diagnosis|prescription|medical record|health condition)\b",
        "risk_level": "moderate",
        "action": "warn",
      },
      # MODERATE: Discrimination
      {
        "name": "Discrimination",
        "pattern": r"\b(discriminate|racist|sexist|ageist)\b",
        "risk_level": "moderate",
        "action": "warn",
      },
    ]

    for rule_data in fallback_rules:
      rule = Rule(
        name=rule_data["name"],
        pattern=rule_data["pattern"],
        risk_level=rule_data["risk_level"],
        action=rule_data["action"],
      )
      self.rules.append(rule)

  async def assess(
    self,
    prompt: str,
    context: dict[str, Any] | None,
    layer1_result: Any,
    layer2_result: Any,
  ) -> dict[str, Any]:
    """
    Run all rules against prompt

    Args:
        prompt: The AI request
        context: Additional context
        layer1_result: Result from Layer 1
        layer2_result: Result from Layer 2

    Returns:
        Dict with risk_level, confidence, reasoning, metadata
    """
    violated_rules: list[str] = []
    highest_risk = RiskLevel.NEGLIGIBLE

    # Check all rules
    for rule in self.rules:
      if rule.check(prompt):
        violated_rules.append(rule.name)
        # Track highest risk level
        if self._risk_severity(rule.risk_level) > self._risk_severity(highest_risk):
          highest_risk = rule.risk_level

    # Build result
    if violated_rules:
      reasoning = f"Hard gates violated: {', '.join(violated_rules)}"
      confidence = 1.0  # Rules are deterministic
    else:
      reasoning = "All hard gates passed"
      confidence = 1.0
      highest_risk = RiskLevel.NEGLIGIBLE

    return {
      "risk_level": highest_risk,
      "confidence": confidence,
      "reasoning": reasoning,
      "metadata": {
        "violated_rules": violated_rules,
        "total_rules_checked": len(self.rules),
      },
    }

  def _risk_severity(self, risk_level: RiskLevel) -> int:
    """Convert risk level to numeric severity for comparison"""
    severity_map = {
      RiskLevel.NEGLIGIBLE: 0,
      RiskLevel.LOW: 1,
      RiskLevel.MODERATE: 2,
      RiskLevel.CRITICAL: 3,
      RiskLevel.CATASTROPHIC: 4,
    }
    return severity_map.get(risk_level, 0)

  def add_custom_rule(self, rule: Rule):
    """Add a custom rule at runtime (for user-defined policies)"""
    self.rules.append(rule)

  def remove_rule(self, rule_name: str):
    """Remove a rule by name"""
    self.rules = [r for r in self.rules if r.name != rule_name]
