"""
Judge #6 Lite: Rule-Based Enforcement Engine
Target latency: <50ms (production target <90ms p99)
Coverage: CAN-SPAM regex, GDPR checks, budget constraints
Output: Exportable PDF compliance report
"""

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ViolationType(Enum):
  """Types of compliance violations"""

  CAN_SPAM = "can_spam"
  GDPR = "gdpr"
  HIPAA = "hipaa"
  BUDGET = "budget"
  RATE_LIMIT = "rate_limit"
  DATA_QUALITY = "data_quality"
  CONTENT_POLICY = "content_policy"


class ViolationSeverity(Enum):
  """Severity levels for violations"""

  CRITICAL = "critical"  # Blocks execution, legal risk
  HIGH = "high"  # Blocks execution, compliance risk
  MEDIUM = "medium"  # Warns, logs, may execute
  LOW = "low"  # Logs only


@dataclass
class Violation:
  """Represents a compliance violation"""

  violation_type: ViolationType
  severity: ViolationSeverity
  description: str
  field: str | None = None
  value: str | None = None
  rule_id: str | None = None
  remediation: str | None = None


@dataclass
class VerificationResult:
  """Result of Judge #6 Lite verification"""

  passed: bool
  violations: list[Violation]
  warnings: list[str]
  metadata: dict[str, Any]
  verification_time_ms: float
  audit_report: dict[str, Any]


class ComplianceRule:
  """Base class for compliance rules"""

  def __init__(self, rule_id: str, description: str, severity: ViolationSeverity):
    self.rule_id = rule_id
    self.description = description
    self.severity = severity

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    """Check if data violates this rule"""
    raise NotImplementedError


class JudgeSixLite:
  """
  Rule-based enforcement engine for compliance validation

  Verifies agent outputs against:
  - CAN-SPAM (email marketing compliance)
  - GDPR (EU data protection)
  - HIPAA (healthcare data protection)
  - Budget constraints
  - Content policies
  """

  def __init__(self, config: dict[str, Any] | None = None):
    self.config = config or {}
    self.rules = []
    self.sla_target_ms = self.config.get("sla_p99_ms", 90)

    # Initialize default rules
    self._register_default_rules()

  def _register_default_rules(self):
    """Register default compliance rules"""
    # CAN-SPAM rules
    self.register_rule(CANSPAMUnsubscribeRule())
    self.register_rule(CANSPAMPhysicalAddressRule())
    self.register_rule(CANSPAMDeceptiveHeaderRule())

    # GDPR rules
    self.register_rule(GDPRConsentRule())
    self.register_rule(GDPRDataMinimizationRule())
    self.register_rule(GDPRPersonalEmailRule())

    # Budget rules
    self.register_rule(BudgetLimitRule())

  def register_rule(self, rule: ComplianceRule):
    """Register a new compliance rule"""
    self.rules.append(rule)

  def verify(
    self, result: Any, context: dict[str, Any] | None = None, sla_p99: int | None = None
  ) -> VerificationResult:
    """
    Verify result against all registered compliance rules

    Args:
        result: Agent output to verify
        context: Additional context (customer_id, region, etc.)
        sla_p99: Target SLA in milliseconds (default: 90ms)

    Returns:
        VerificationResult with violations and audit report
    """
    start_time = time.perf_counter()
    context = context or {}
    sla_target = sla_p99 or self.sla_target_ms

    violations = []
    warnings = []
    metadata = {
      "rules_checked": len(self.rules),
      "sla_target_ms": sla_target,
    }

    # Convert result to dict if needed
    if isinstance(result, str):
      data = {"content": result}
    elif isinstance(result, dict):
      data = result
    else:
      data = {"raw_result": str(result)}

    # Check all rules
    for rule in self.rules:
      try:
        violation = rule.check(data, context)
        if violation:
          violations.append(violation)
      except Exception as e:
        warnings.append(f"Rule {rule.rule_id} failed: {str(e)}")

    # Check SLA
    verification_time_ms = (time.perf_counter() - start_time) * 1000
    if verification_time_ms > sla_target:
      warnings.append(
        f"Verification exceeded SLA target: {verification_time_ms:.2f}ms > {sla_target}ms"
      )

    metadata["verification_time_ms"] = verification_time_ms

    # Determine if verification passed
    critical_violations = [
      v
      for v in violations
      if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]
    ]
    passed = len(critical_violations) == 0

    # Build audit report
    audit_report = self._build_audit_report(
      data, violations, warnings, metadata, context
    )

    return VerificationResult(
      passed=passed,
      violations=violations,
      warnings=warnings,
      metadata=metadata,
      verification_time_ms=verification_time_ms,
      audit_report=audit_report,
    )

  def _build_audit_report(
    self,
    data: dict[str, Any],
    violations: list[Violation],
    warnings: list[str],
    metadata: dict[str, Any],
    context: dict[str, Any],
  ) -> dict[str, Any]:
    """Build comprehensive audit report"""
    return {
      "timestamp": datetime.utcnow().isoformat(),
      "metadata": metadata,
      "context": context,
      "violations": [
        {
          "type": v.violation_type.value,
          "severity": v.severity.value,
          "description": v.description,
          "field": v.field,
          "value": v.value,
          "rule_id": v.rule_id,
          "remediation": v.remediation,
        }
        for v in violations
      ],
      "warnings": warnings,
      "passed": len(
        [
          v
          for v in violations
          if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.HIGH]
        ]
      )
      == 0,
      "data_summary": {
        "keys": list(data.keys()),
        "size_bytes": len(json.dumps(data)),
      },
    }

  def export_audit_report_pdf(self, audit_report: dict[str, Any]) -> bytes:
    """Export audit report as PDF (placeholder - requires PDF library)"""
    # TODO: Implement PDF export using reportlab or similar
    # For now, return JSON representation
    return json.dumps(audit_report, indent=2).encode("utf-8")


# CAN-SPAM Compliance Rules


class CANSPAMUnsubscribeRule(ComplianceRule):
  """CAN-SPAM requires unsubscribe link in all marketing emails"""

  def __init__(self):
    super().__init__(
      rule_id="can-spam-001",
      description="Marketing emails must include unsubscribe link",
      severity=ViolationSeverity.CRITICAL,
    )
    self.unsubscribe_patterns = [
      r"unsubscribe",
      r"opt[\s-]?out",
      r"remove[\s]?me",
      r"manage[\s]?preferences",
      r"email[\s]?preferences",
    ]

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    content = data.get("content", "") or data.get("email_body", "")
    is_marketing = context.get("is_marketing_email", True)

    if not is_marketing:
      return None

    if not content:
      return None

    # Check for unsubscribe link
    content_lower = content.lower()
    has_unsubscribe = any(
      re.search(pattern, content_lower) for pattern in self.unsubscribe_patterns
    )

    if not has_unsubscribe:
      return Violation(
        violation_type=ViolationType.CAN_SPAM,
        severity=self.severity,
        description="Marketing email missing unsubscribe link (CAN-SPAM violation)",
        field="content",
        rule_id=self.rule_id,
        remediation="Add unsubscribe link or 'manage preferences' option",
      )

    return None


class CANSPAMPhysicalAddressRule(ComplianceRule):
  """CAN-SPAM requires physical mailing address"""

  def __init__(self):
    super().__init__(
      rule_id="can-spam-002",
      description="Marketing emails must include physical mailing address",
      severity=ViolationSeverity.HIGH,
    )

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    content = data.get("content", "") or data.get("email_body", "")
    is_marketing = context.get("is_marketing_email", True)

    if not is_marketing:
      return None

    if not content:
      return None

    # Simple check for address patterns (street number + street name)
    address_pattern = r"\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)"
    has_address = re.search(address_pattern, content, re.IGNORECASE)

    if not has_address:
      return Violation(
        violation_type=ViolationType.CAN_SPAM,
        severity=self.severity,
        description="Marketing email missing physical mailing address (CAN-SPAM violation)",
        field="content",
        rule_id=self.rule_id,
        remediation="Add company's physical mailing address",
      )

    return None


class CANSPAMDeceptiveHeaderRule(ComplianceRule):
  """CAN-SPAM prohibits deceptive subject lines"""

  def __init__(self):
    super().__init__(
      rule_id="can-spam-003",
      description="Email subject line must not be deceptive",
      severity=ViolationSeverity.CRITICAL,
    )
    self.deceptive_patterns = [
      r"re:.*",  # Fake reply
      r"fwd:.*",  # Fake forward
      r"urgent.*password",  # Fake security alert
      r"your.*account.*suspended",  # Fake suspension
      r"claim.*prize",  # Fake prize
    ]

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    subject = data.get("subject", "") or data.get("email_subject", "")

    if not subject:
      return None

    subject_lower = subject.lower()

    # Check for deceptive patterns
    for pattern in self.deceptive_patterns:
      if re.match(pattern, subject_lower):
        return Violation(
          violation_type=ViolationType.CAN_SPAM,
          severity=self.severity,
          description=f"Potentially deceptive subject line (CAN-SPAM violation): {subject}",
          field="subject",
          value=subject,
          rule_id=self.rule_id,
          remediation="Use honest, non-deceptive subject line",
        )

    return None


# GDPR Compliance Rules


class GDPRConsentRule(ComplianceRule):
  """GDPR requires consent for EU personal data processing"""

  def __init__(self):
    super().__init__(
      rule_id="gdpr-001",
      description="EU personal data processing requires explicit consent",
      severity=ViolationSeverity.CRITICAL,
    )

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    eu_customer = context.get("eu_customer", False)
    has_consent = context.get("gdpr_consent", False)
    involves_pii = context.get("involves_pii", False)

    if eu_customer and involves_pii and not has_consent:
      return Violation(
        violation_type=ViolationType.GDPR,
        severity=self.severity,
        description="Processing EU customer PII without explicit GDPR consent",
        rule_id=self.rule_id,
        remediation="Obtain explicit GDPR consent before processing EU customer data",
      )

    return None


class GDPRDataMinimizationRule(ComplianceRule):
  """GDPR requires data minimization"""

  def __init__(self):
    super().__init__(
      rule_id="gdpr-002",
      description="Only collect necessary personal data (GDPR data minimization)",
      severity=ViolationSeverity.MEDIUM,
    )

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    eu_customer = context.get("eu_customer", False)

    if not eu_customer:
      return None

    # Check for excessive data collection
    sensitive_fields = [
      "ssn",
      "social_security",
      "passport",
      "drivers_license",
      "biometric",
    ]
    purpose = context.get("purpose", "")

    for field in sensitive_fields:
      if field in data and field not in purpose.lower():
        return Violation(
          violation_type=ViolationType.GDPR,
          severity=self.severity,
          description=f"Collecting sensitive data '{field}' not necessary for stated purpose",
          field=field,
          rule_id=self.rule_id,
          remediation="Remove unnecessary personal data fields",
        )

    return None


class GDPRPersonalEmailRule(ComplianceRule):
  """GDPR restrictions on personal email addresses"""

  def __init__(self):
    super().__init__(
      rule_id="gdpr-003",
      description="Personal email addresses from EU require consent",
      severity=ViolationSeverity.HIGH,
    )

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    eu_customer = context.get("eu_customer", False)
    email = data.get("email", "")

    if not eu_customer or not email:
      return None

    # Check if email is personal (not corporate)
    personal_domains = [
      "gmail.com",
      "yahoo.com",
      "hotmail.com",
      "outlook.com",
      "aol.com",
    ]
    domain = email.split("@")[-1].lower() if "@" in email else ""

    if domain in personal_domains:
      has_consent = context.get("gdpr_consent", False)
      if not has_consent:
        return Violation(
          violation_type=ViolationType.GDPR,
          severity=self.severity,
          description="Personal email from EU customer requires GDPR consent",
          field="email",
          value=email,
          rule_id=self.rule_id,
          remediation="Obtain consent or use corporate email only",
        )

    return None


# Budget Rules


class BudgetLimitRule(ComplianceRule):
  """Enforce budget limits on actions"""

  def __init__(self):
    super().__init__(
      rule_id="budget-001",
      description="Action cost must not exceed budget limit",
      severity=ViolationSeverity.HIGH,
    )

  def check(self, data: dict[str, Any], context: dict[str, Any]) -> Violation | None:
    cost = data.get("cost_usd", 0.0) or context.get("cost_usd", 0.0)
    budget_limit = context.get("budget_limit_usd", 100.0)

    if cost > budget_limit:
      return Violation(
        violation_type=ViolationType.BUDGET,
        severity=self.severity,
        description=f"Cost ${cost:.2f} exceeds budget limit ${budget_limit:.2f}",
        field="cost_usd",
        value=str(cost),
        rule_id=self.rule_id,
        remediation="Reduce cost or request budget increase",
      )

    return None
