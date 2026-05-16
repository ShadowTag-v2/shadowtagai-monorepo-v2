# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
JR (Judgment Rule) Policy Engine
================================
Second layer of the NS-JR-Cor compliance framework.

Responsibilities:
- Evaluate NS signals against policy rules
- Apply California AI regulation requirements
- Generate compliance decisions (go/no-go)
- Determine required actions (block, warn, disclose, etc.)

Policy Sources:
- California AI regulations (statutes)
- Platform-specific policies (configurable)
- Age-based rules (minor protection)
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.models.california_ai import (
  CARegulationType,
  ComplianceAction,
  JRPolicyOutput,
  NSDetectionOutput,
  PolicyEvaluation,
  PolicyViolation,
  RiskTier,
  UserAgeCategory,
  ViolationSeverity,
)
from corp_engine.governance.regulations.california_ai_comprehensive import (
  CALIFORNIA_AI_REGULATIONS,
  ActionType,
  MinorProtectionLevel,
  RegulationRule,
  TriggerCondition,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class JRConfig:
  """JR Policy Engine configuration"""

  # Enforcement mode
  strict_mode: bool = True

  # Thresholds
  self_harm_threshold: float = 0.5
  explicit_threshold: float = 0.6
  medical_threshold: float = 0.7

  # Human review thresholds
  human_review_threshold: float = 0.4
  ambiguous_range: tuple = (0.4, 0.7)

  # Policy file paths
  custom_policies_path: str | None = None


# =============================================================================
# Policy Rule Evaluator
# =============================================================================


class PolicyRuleEvaluator:
  """Evaluates individual policy rules against NS output"""

  def __init__(self, config: JRConfig):
    self.config = config

  def evaluate(
    self,
    rule: RegulationRule,
    ns_output: NSDetectionOutput,
    user_age: UserAgeCategory,
    session_duration_minutes: int = 0,
    is_conversation_start: bool = False,
    data_collection: bool = False,
  ) -> PolicyEvaluation:
    """
    Evaluate a single policy rule.

    Returns:
        PolicyEvaluation with pass/fail and any violations
    """
    # Map UserAgeCategory to MinorProtectionLevel
    protection_level = self._map_age_to_protection(user_age)

    # Check if rule applies to this user
    if not rule.applies_to_user(protection_level):
      return PolicyEvaluation(
        policy_id=rule.rule_id,
        policy_name=rule.name,
        passed=True,
        violations=[],
        required_action=ComplianceAction.PASS,
        notes="Rule not applicable to user age category",
      )

    # Check trigger conditions
    triggered = False
    trigger_details = {}

    if rule.trigger == TriggerCondition.ALWAYS:
      triggered = True

    elif rule.trigger == TriggerCondition.SELF_HARM_DETECTED:
      if ns_output.self_harm_signals:
        max_confidence = max(s.confidence for s in ns_output.self_harm_signals)
        if max_confidence >= self.config.self_harm_threshold:
          triggered = True
          trigger_details["confidence"] = max_confidence
          trigger_details["signals"] = len(ns_output.self_harm_signals)

    elif rule.trigger == TriggerCondition.EXPLICIT_CONTENT_DETECTED:
      if ns_output.explicit_content_signals:
        max_confidence = max(s.confidence for s in ns_output.explicit_content_signals)
        if max_confidence >= self.config.explicit_threshold:
          triggered = True
          trigger_details["confidence"] = max_confidence
          trigger_details["categories"] = [
            s.content_categories for s in ns_output.explicit_content_signals
          ]

    elif rule.trigger == TriggerCondition.MEDICAL_CLAIM_DETECTED:
      if ns_output.medical_claim_signals:
        max_confidence = max(s.confidence for s in ns_output.medical_claim_signals)
        if max_confidence >= self.config.medical_threshold:
          triggered = True
          trigger_details["confidence"] = max_confidence

    elif rule.trigger == TriggerCondition.CONVERSATION_START:
      if is_conversation_start:
        triggered = True

    elif rule.trigger == TriggerCondition.SESSION_DURATION_EXCEEDED:
      threshold = rule.parameters.get("threshold_minutes", 60)
      if session_duration_minutes >= threshold:
        triggered = True
        trigger_details["duration"] = session_duration_minutes
        trigger_details["threshold"] = threshold

    elif rule.trigger == TriggerCondition.MINOR_USER:
      if user_age in [UserAgeCategory.UNDER_13, UserAgeCategory.TEEN_13_17]:
        triggered = True

    elif rule.trigger == TriggerCondition.DATA_COLLECTION:
      if data_collection:
        triggered = True

    # Build result
    if not triggered:
      return PolicyEvaluation(
        policy_id=rule.rule_id,
        policy_name=rule.name,
        passed=True,
        violations=[],
        required_action=ComplianceAction.PASS,
      )

    # Rule was triggered - create violation
    violation = PolicyViolation(
      regulation_type=self._map_rule_to_regulation(rule),
      rule_id=rule.rule_id,
      description=rule.description,
      severity=self._map_severity(rule.severity),
      evidence=str(trigger_details),
      remediation=rule.remediation,
      reference=rule.legal_reference,
    )

    return PolicyEvaluation(
      policy_id=rule.rule_id,
      policy_name=rule.name,
      passed=False,
      violations=[violation],
      required_action=self._map_action(rule.action),
      notes=f"Triggered: {trigger_details}",
    )

  def _map_age_to_protection(self, age: UserAgeCategory) -> MinorProtectionLevel:
    """Map UserAgeCategory to MinorProtectionLevel"""
    mapping = {
      UserAgeCategory.UNDER_13: MinorProtectionLevel.UNDER_13,
      UserAgeCategory.TEEN_13_17: MinorProtectionLevel.TEEN_13_15,  # Use stricter
      UserAgeCategory.ADULT: MinorProtectionLevel.ADULT,
      UserAgeCategory.UNKNOWN: MinorProtectionLevel.UNDER_13,  # Default to strictest
    }
    return mapping.get(age, MinorProtectionLevel.UNDER_13)

  def _map_rule_to_regulation(self, rule: RegulationRule) -> CARegulationType:
    """Map rule to regulation type"""
    rule_id = rule.rule_id.upper()

    if "SELF_HARM" in rule_id:
      return CARegulationType.SELF_HARM_DETECTION
    elif "DISCLOSURE" in rule_id:
      return CARegulationType.AI_DISCLOSURE
    elif "BREAK" in rule_id:
      return CARegulationType.BREAK_REMINDER
    elif "EXPLICIT" in rule_id:
      return CARegulationType.EXPLICIT_CONTENT
    elif "MEDICAL" in rule_id:
      return CARegulationType.MEDICAL_IMPERSONATION
    elif "PRIVACY" in rule_id:
      return CARegulationType.DATA_PRIVACY
    else:
      return CARegulationType.MINOR_PROTECTION

  def _map_severity(self, severity: str) -> ViolationSeverity:
    """Map string severity to enum"""
    mapping = {
      "info": ViolationSeverity.INFO,
      "low": ViolationSeverity.LOW,
      "medium": ViolationSeverity.MEDIUM,
      "high": ViolationSeverity.HIGH,
      "critical": ViolationSeverity.CRITICAL,
    }
    return mapping.get(severity.lower(), ViolationSeverity.MEDIUM)

  def _map_action(self, action: ActionType) -> ComplianceAction:
    """Map ActionType to ComplianceAction"""
    mapping = {
      ActionType.PASS: ComplianceAction.PASS,
      ActionType.BLOCK: ComplianceAction.BLOCK,
      ActionType.WARN: ComplianceAction.WARN,
      ActionType.DISCLOSE_AI: ComplianceAction.DISCLOSE,
      ActionType.RESPOND_WITH_RESOURCES: ComplianceAction.RESPOND_WITH_RESOURCES,
      ActionType.BREAK_REMINDER: ComplianceAction.REMIND,
      ActionType.REQUIRE_CONSENT: ComplianceAction.REQUIRE_PARENTAL_CONSENT,
      ActionType.FLAG_REVIEW: ComplianceAction.FLAG_FOR_REVIEW,
    }
    return mapping.get(action, ComplianceAction.PASS)


# =============================================================================
# Main JR Policy Engine
# =============================================================================


class JRPolicyEngine:
  """
  Judgment Rule Policy Engine.

  Second layer of NS-JR-Cor framework.
  Evaluates NS detection signals against California AI regulations
  and platform policies to determine compliance actions.
  """

  def __init__(self, config: JRConfig | None = None):
    self.config = config or JRConfig()
    self.evaluator = PolicyRuleEvaluator(self.config)

    # Load regulations
    self.regulations = CALIFORNIA_AI_REGULATIONS

    # Load custom policies if configured
    self.custom_policies: list[RegulationRule] = []
    if self.config.custom_policies_path:
      self._load_custom_policies(self.config.custom_policies_path)

    # Stats
    self._stats = {
      "total_evaluations": 0,
      "compliant": 0,
      "non_compliant": 0,
      "human_review": 0,
      "actions_by_type": {},
    }

  def _load_custom_policies(self, path: str) -> None:
    """Load custom policies from YAML file"""
    try:
      policy_file = Path(path)
      if policy_file.exists():
        with open(policy_file) as f:
          data = yaml.safe_load(f)
          # Convert to RegulationRule objects
          for rule_data in data.get("policies", []):
            rule = RegulationRule(
              rule_id=rule_data["id"],
              name=rule_data["name"],
              description=rule_data.get("description", ""),
              trigger=TriggerCondition(rule_data["trigger"]),
              action=ActionType(rule_data["action"]),
              severity=rule_data.get("severity", "medium"),
              parameters=rule_data.get("parameters", {}),
            )
            self.custom_policies.append(rule)
        logger.info(f"Loaded {len(self.custom_policies)} custom policies")
    except Exception as e:
      logger.warning(f"Failed to load custom policies: {e}")

  async def evaluate(
    self,
    content_id: str,
    ns_output: NSDetectionOutput,
    user_age: UserAgeCategory = UserAgeCategory.UNKNOWN,
    session_duration_minutes: int = 0,
    is_conversation_start: bool = False,
    data_collection: bool = False,
  ) -> JRPolicyOutput:
    """
    Evaluate NS output against all policies.

    Args:
        content_id: Content identifier
        ns_output: Output from NS detection layer
        user_age: User's age category
        session_duration_minutes: Session duration for break reminders
        is_conversation_start: Whether this is conversation start
        data_collection: Whether data collection is occurring

    Returns:
        JRPolicyOutput with compliance decision
    """
    import time

    start_time = time.time()

    self._stats["total_evaluations"] += 1

    evaluations: list[PolicyEvaluation] = []
    all_violations: list[PolicyViolation] = []
    required_actions: set[ComplianceAction] = set()

    # Evaluate all regulations
    all_rules = self.regulations + self.custom_policies

    for rule in all_rules:
      evaluation = self.evaluator.evaluate(
        rule=rule,
        ns_output=ns_output,
        user_age=user_age,
        session_duration_minutes=session_duration_minutes,
        is_conversation_start=is_conversation_start,
        data_collection=data_collection,
      )

      evaluations.append(evaluation)

      if not evaluation.passed:
        all_violations.extend(evaluation.violations)
        required_actions.add(evaluation.required_action)

        # Track action stats
        action_name = evaluation.required_action.value
        self._stats["actions_by_type"][action_name] = (
          self._stats["actions_by_type"].get(action_name, 0) + 1
        )

    # Determine go/no-go decision
    # Block actions = no-go
    # Warn, disclose, remind = go with modifications
    blocking_actions = {
      ComplianceAction.BLOCK,
      ComplianceAction.REQUIRE_PARENTAL_CONSENT,
    }

    go_decision = not any(a in blocking_actions for a in required_actions)

    # Calculate risk tier
    risk_tier = self._calculate_risk_tier(ns_output, all_violations)

    # Determine if human review needed
    human_review = ComplianceAction.FLAG_FOR_REVIEW in required_actions or (
      self.config.ambiguous_range[0]
      <= ns_output.overall_risk_score
      <= self.config.ambiguous_range[1]
    )

    if human_review:
      self._stats["human_review"] += 1

    # Update compliance stats
    if go_decision and len(all_violations) == 0:
      self._stats["compliant"] += 1
    else:
      self._stats["non_compliant"] += 1

    # Generate reasoning
    reasoning = self._generate_reasoning(evaluations, all_violations, go_decision)

    processing_time = (time.time() - start_time) * 1000

    return JRPolicyOutput(
      content_id=content_id,
      user_age_category=user_age,
      evaluations=evaluations,
      all_violations=all_violations,
      go_decision=go_decision,
      risk_tier=risk_tier,
      required_actions=list(required_actions),
      human_review_required=human_review,
      confidence=1.0 - ns_output.overall_risk_score,
      reasoning=reasoning,
      processing_time_ms=processing_time,
    )

  def _calculate_risk_tier(
    self, ns_output: NSDetectionOutput, violations: list[PolicyViolation]
  ) -> RiskTier:
    """Calculate risk tier based on signals and violations"""
    # Critical violations = Tier 5
    critical_count = sum(
      1 for v in violations if v.severity == ViolationSeverity.CRITICAL
    )
    if critical_count > 0 or ns_output.has_critical_signals:
      return RiskTier.TIER_5_CRITICAL

    # High violations = Tier 4
    high_count = sum(1 for v in violations if v.severity == ViolationSeverity.HIGH)
    if high_count > 0 or ns_output.overall_risk_score > 0.8:
      return RiskTier.TIER_4_HIGH

    # Medium violations or moderate risk = Tier 3
    medium_count = sum(1 for v in violations if v.severity == ViolationSeverity.MEDIUM)
    if medium_count > 0 or ns_output.overall_risk_score > 0.5:
      return RiskTier.TIER_3_MODERATE

    # Low violations = Tier 2
    low_count = sum(1 for v in violations if v.severity == ViolationSeverity.LOW)
    if low_count > 0 or ns_output.overall_risk_score > 0.2:
      return RiskTier.TIER_2_LOW

    return RiskTier.TIER_1_MINIMAL

  def _generate_reasoning(
    self,
    evaluations: list[PolicyEvaluation],
    violations: list[PolicyViolation],
    go_decision: bool,
  ) -> str:
    """Generate human-readable reasoning for decision"""
    if not violations:
      return "Content passed all policy checks. No violations detected."

    violation_summary = []
    for v in violations:
      violation_summary.append(
        f"- {v.rule_id}: {v.description} (severity: {v.severity.value})"
      )

    action = "ALLOWED with modifications" if go_decision else "BLOCKED"

    return f"""Decision: {action}

Violations detected:
{chr(10).join(violation_summary)}

Legal references: {", ".join(set(v.reference for v in violations if v.reference))}"""

  def get_stats(self) -> dict[str, Any]:
    """Get policy engine statistics"""
    total = self._stats["total_evaluations"]
    return {
      **self._stats,
      "compliance_rate": (self._stats["compliant"] / total if total > 0 else 1.0),
      "human_review_rate": (self._stats["human_review"] / total if total > 0 else 0.0),
    }


# =============================================================================
# Factory Function
# =============================================================================


def create_jr_engine(
  strict_mode: bool = True,
  custom_policies_path: str | None = None,
) -> JRPolicyEngine:
  """Create configured JR Policy Engine"""
  config = JRConfig(
    strict_mode=strict_mode,
    custom_policies_path=custom_policies_path,
  )
  return JRPolicyEngine(config=config)


# Global instance
_jr_engine: JRPolicyEngine | None = None


def get_jr_engine() -> JRPolicyEngine:
  """Get or create global JR engine instance"""
  global _jr_engine
  if _jr_engine is None:
    _jr_engine = create_jr_engine()
  return _jr_engine
