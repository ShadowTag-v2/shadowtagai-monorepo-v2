# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
California AI Compliance Engine
===============================
Public-facing engine wrapping the NS-JR-Cor framework.

This is the main entry point for California AI compliance checks.
Provides a clean API for SDK users and internal services.

Features:
- Single message assessment
- Batch assessment
- Compliance reporting
- Usage metering
- Webhook notifications
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.models.california_ai import (
  BatchAssessmentRequest,
  BatchAssessmentResult,
  CaliforniaAIAssessmentRequest,
  CaliforniaAIAssessmentResult,
  ComplianceReport,
  ComplianceReportRequest,
  UsageMetrics,
  UsageTier,
)
from app.services.cor_orchestrator import CorOrchestrator, get_cor_orchestrator

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class CaliforniaAIEngineConfig:
  """California AI Engine configuration"""

  # API key tiers
  free_tier_limit: int = 1000  # Per month
  starter_tier_limit: int = 10000
  growth_tier_limit: int = 100000

  # Pricing per assessment (for metering)
  price_per_assessment: float = 0.001
  price_per_cached: float = 0.0001

  # Webhook settings
  webhook_enabled: bool = False
  webhook_url: str | None = None

  # Rate limiting
  rate_limit_enabled: bool = True
  rate_limit_per_minute: int = 100


# =============================================================================
# Usage Tracker
# =============================================================================


class UsageTracker:
  """Tracks API usage for billing and rate limiting"""

  def __init__(self, config: CaliforniaAIEngineConfig):
    self.config = config
    self._usage: dict[str, dict] = {}  # platform_id -> usage data

  def record_assessment(
    self,
    platform_id: str,
    cached: bool = False,
    api_calls: dict[str, int] = None,
  ) -> None:
    """Record an assessment for usage tracking"""
    if platform_id not in self._usage:
      self._usage[platform_id] = {
        "total_assessments": 0,
        "cached_assessments": 0,
        "api_calls_google": 0,
        "api_calls_hive": 0,
        "api_calls_gemini": 0,
        "period_start": datetime.utcnow(),
      }

    self._usage[platform_id]["total_assessments"] += 1
    if cached:
      self._usage[platform_id]["cached_assessments"] += 1

    if api_calls:
      for api, count in api_calls.items():
        key = f"api_calls_{api}"
        if key in self._usage[platform_id]:
          self._usage[platform_id][key] += count

  def get_usage(self, platform_id: str) -> UsageMetrics:
    """Get usage metrics for a platform"""
    data = self._usage.get(
      platform_id,
      {
        "total_assessments": 0,
        "cached_assessments": 0,
        "api_calls_google": 0,
        "api_calls_hive": 0,
        "api_calls_gemini": 0,
        "period_start": datetime.utcnow(),
      },
    )

    # Calculate costs
    regular = data["total_assessments"] - data["cached_assessments"]
    cached = data["cached_assessments"]

    estimated_cost = (
      regular * self.config.price_per_assessment + cached * self.config.price_per_cached
    )

    total = data["total_assessments"]

    return UsageMetrics(
      period_start=data["period_start"],
      period_end=datetime.utcnow(),
      platform_id=platform_id,
      total_assessments=total,
      cached_assessments=cached,
      api_calls_google=data["api_calls_google"],
      api_calls_hive=data["api_calls_hive"],
      api_calls_gemini=data["api_calls_gemini"],
      estimated_cost_usd=estimated_cost,
      cost_per_assessment=estimated_cost / total if total > 0 else 0.0,
    )

  def check_tier_limit(self, platform_id: str, tier: UsageTier) -> bool:
    """Check if platform is within tier limits"""
    data = self._usage.get(platform_id, {"total_assessments": 0})
    total = data["total_assessments"]

    limits = {
      UsageTier.FREE: self.config.free_tier_limit,
      UsageTier.STARTER: self.config.starter_tier_limit,
      UsageTier.GROWTH: self.config.growth_tier_limit,
      UsageTier.ENTERPRISE: float("inf"),
    }

    return total < limits.get(tier, 0)


# =============================================================================
# Report Generator
# =============================================================================


class ReportGenerator:
  """Generates compliance reports"""

  def __init__(self, orchestrator: CorOrchestrator):
    self.orchestrator = orchestrator
    self._assessment_history: list[CaliforniaAIAssessmentResult] = []

  def record_assessment(self, result: CaliforniaAIAssessmentResult) -> None:
    """Record assessment for reporting"""
    self._assessment_history.append(result)

    # Keep history manageable
    if len(self._assessment_history) > 100000:
      self._assessment_history = self._assessment_history[-50000:]

  def generate_report(self, request: ComplianceReportRequest) -> ComplianceReport:
    """Generate compliance report for period"""
    # Filter assessments by period
    assessments = [
      a
      for a in self._assessment_history
      if request.start_date <= a.timestamp <= request.end_date
    ]

    if request.platform_id:
      # Would need platform_id in result to filter
      pass

    total = len(assessments)
    compliant = sum(1 for a in assessments if a.is_compliant)
    non_compliant = total - compliant

    # Violations by regulation
    violations_by_reg: dict[str, int] = {}
    violations_by_severity: dict[str, int] = {}

    for a in assessments:
      for v in a.violations:
        reg = v.regulation_type.value
        violations_by_reg[reg] = violations_by_reg.get(reg, 0) + 1

        sev = v.severity.value
        violations_by_severity[sev] = violations_by_severity.get(sev, 0) + 1

    # Recommendations based on violations
    recommendations = []
    if violations_by_reg.get("self_harm_detection", 0) > 0:
      recommendations.append("Implement additional self-harm detection safeguards")
    if violations_by_reg.get("explicit_content", 0) > 0:
      recommendations.append("Review content filtering policies for minor protection")
    if violations_by_reg.get("medical_impersonation", 0) > 0:
      recommendations.append("Add medical disclaimer prompts to AI responses")

    return ComplianceReport(
      period_start=request.start_date,
      period_end=request.end_date,
      total_assessments=total,
      compliant_count=compliant,
      non_compliant_count=non_compliant,
      compliance_rate=compliant / total if total > 0 else 1.0,
      violations_by_regulation=violations_by_reg,
      violations_by_severity=violations_by_severity,
      assessments_by_age_category={},  # Would need tracking
      top_violations=[],  # Would aggregate top violations
      recommendations=recommendations,
    )


# =============================================================================
# Main California AI Engine
# =============================================================================


class CaliforniaAIEngine:
  """
  California AI Compliance Engine.

  Main entry point for California AI regulation compliance.
  Wraps the NS-JR-Cor framework with a clean public API.

  Usage:
      engine = CaliforniaAIEngine()

      # Single assessment
      result = await engine.assess(CaliforniaAIAssessmentRequest(
          content="User message here",
          user_age=15,
      ))

      # Batch assessment
      batch_result = await engine.batch_assess(BatchAssessmentRequest(
          items=[...],
          parallel=True,
      ))

      # Generate report
      report = engine.generate_report(ComplianceReportRequest(
          start_date=...,
          end_date=...,
      ))
  """

  def __init__(
    self,
    config: CaliforniaAIEngineConfig | None = None,
    orchestrator: CorOrchestrator | None = None,
  ):
    self.config = config or CaliforniaAIEngineConfig()
    self.orchestrator = orchestrator or get_cor_orchestrator()

    # Usage and reporting
    self.usage_tracker = UsageTracker(self.config)
    self.report_generator = ReportGenerator(self.orchestrator)

    logger.info("California AI Engine initialized")

  async def assess(
    self,
    request: CaliforniaAIAssessmentRequest,
    api_key: str | None = None,
    tier: UsageTier = UsageTier.FREE,
  ) -> CaliforniaAIAssessmentResult:
    """
    Assess content for California AI compliance.

    Args:
        request: Assessment request with content and context
        api_key: Optional API key for authentication
        tier: Usage tier for rate limiting

    Returns:
        CaliforniaAIAssessmentResult with compliance decision

    Raises:
        ValueError: If content is invalid
        RateLimitError: If tier limit exceeded
    """
    # Validate request
    if not request.content or not request.content.strip():
      raise ValueError("Content cannot be empty")

    # Check tier limits
    if not self.usage_tracker.check_tier_limit(request.platform_id, tier):
      raise ValueError(f"Usage limit exceeded for tier: {tier.value}")

    # Run assessment
    result = await self.orchestrator.assess(request)

    # Track usage
    self.usage_tracker.record_assessment(
      platform_id=request.platform_id,
      cached=result.cache_hit,
    )

    # Record for reporting
    self.report_generator.record_assessment(result)

    return result

  async def batch_assess(
    self,
    request: BatchAssessmentRequest,
    api_key: str | None = None,
    tier: UsageTier = UsageTier.GROWTH,
  ) -> BatchAssessmentResult:
    """
    Batch assess multiple content items.

    Args:
        request: Batch request with items
        api_key: Optional API key
        tier: Usage tier (batch requires at least GROWTH)

    Returns:
        BatchAssessmentResult with all results
    """
    if tier == UsageTier.FREE:
      raise ValueError("Batch assessment requires STARTER tier or higher")

    result = await self.orchestrator.batch_assess(request)

    # Track usage for each item
    for item_result in result.results:
      self.usage_tracker.record_assessment(
        platform_id=request.items[0].platform_id if request.items else "default",
        cached=item_result.cache_hit,
      )
      self.report_generator.record_assessment(item_result)

    return result

  async def quick_check(
    self,
    content: str,
    user_age: int | None = None,
  ) -> dict[str, Any]:
    """
    Quick compliance check with minimal input.

    Convenience method for simple checks.

    Returns:
        Dict with is_compliant, risk_tier, and required_actions
    """
    request = CaliforniaAIAssessmentRequest(
      content=content,
      user_age=user_age,
    )

    result = await self.assess(request)

    return {
      "is_compliant": result.is_compliant,
      "go_decision": result.go_decision,
      "risk_tier": result.risk_tier.value,
      "required_actions": [a.value for a in result.required_actions],
      "self_harm_detected": result.self_harm_detected,
      "disclosure_required": result.disclosure_required,
      "latency_ms": result.total_latency_ms,
    }

  def generate_report(
    self,
    request: ComplianceReportRequest,
  ) -> ComplianceReport:
    """Generate compliance report for period"""
    return self.report_generator.generate_report(request)

  def get_usage(self, platform_id: str) -> UsageMetrics:
    """Get usage metrics for platform"""
    return self.usage_tracker.get_usage(platform_id)

  def get_stats(self) -> dict[str, Any]:
    """Get engine statistics"""
    return self.orchestrator.get_stats()


# =============================================================================
# Factory and Global Instance
# =============================================================================


def create_california_ai_engine() -> CaliforniaAIEngine:
  """Create California AI Engine instance"""
  return CaliforniaAIEngine()


_engine: CaliforniaAIEngine | None = None


def get_california_ai_engine() -> CaliforniaAIEngine:
  """Get or create global California AI Engine instance"""
  global _engine
  if _engine is None:
    _engine = create_california_ai_engine()
  return _engine


# =============================================================================
# SDK-Style Convenience Functions
# =============================================================================


async def assess_content(
  content: str,
  user_age: int | None = None,
  platform_id: str = "default",
) -> CaliforniaAIAssessmentResult:
  """
  SDK convenience function for content assessment.

  Usage:
      from app.services.california_ai_engine import assess_content

      result = await assess_content(
          "Hello, how are you?",
          user_age=15,
      )

      if result.is_compliant:
          # Content is safe
          pass
      else:
          # Handle violations
          for violation in result.violations:
              print(f"Violation: {violation.description}")
  """
  engine = get_california_ai_engine()
  request = CaliforniaAIAssessmentRequest(
    content=content,
    user_age=user_age,
    platform_id=platform_id,
  )
  return await engine.assess(request)


async def check_self_harm(content: str) -> dict[str, Any]:
  """
  SDK convenience function for self-harm detection.

  Returns:
      Dict with detected (bool), confidence, and crisis_resources
  """
  engine = get_california_ai_engine()
  request = CaliforniaAIAssessmentRequest(
    content=content,
    strict_mode=True,
  )
  result = await engine.assess(request)

  return {
    "detected": result.self_harm_detected,
    "confidence": result.ns_output.overall_risk_score if result.ns_output else 0.0,
    "crisis_resources": result.crisis_resources,
    "crisis_response": result.action_details.get("crisis_response"),
  }
