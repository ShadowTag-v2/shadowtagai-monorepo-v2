# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Judge #6 HITL System
Binary enforcement engine with ATP 5-19 risk assessment.

Verticals:
- FinJudge: Financial transactions ($50K+ wire transfers)
- CaseJudge: Legal case assessment
- LawJudge: Legal compliance validation (EU AI Act, GDPR, CA SB 53)
- FraudJudge: Fraud detection & risk scoring

Decision Framework: Purpose=AiYouJR • Reason=Doctrine • Brakes=Army RM
Target Latency: p99 ≤90ms
"""

from src.judges.base_judge import BaseJudge
from src.judges.case_judge import CaseJudge
from src.judges.fin_judge import FinJudge
from src.judges.fraud_judge import FraudJudge
from src.judges.law_judge import LawJudge
from src.judges.models import (
  ApprovalGate,
  AuditTrail,
  JudgeDecision,
  JudgeRequest,
  JudgeResponse,
  JudgeType,
  PerformanceMetrics,
)


class JudgeFactory:
  """Factory for creating judge instances."""

  _judges = {
    JudgeType.FIN: None,
    JudgeType.CASE: None,
    JudgeType.LAW: None,
    JudgeType.FRAUD: None,
  }

  @classmethod
  def get_judge(cls, judge_type: JudgeType) -> BaseJudge:
    """
    Get or create judge instance (singleton per type).

    Args:
        judge_type: Judge vertical type

    Returns:
        Judge instance
    """
    if cls._judges[judge_type] is None:
      if judge_type == JudgeType.FIN:
        cls._judges[judge_type] = FinJudge()
      elif judge_type == JudgeType.CASE:
        cls._judges[judge_type] = CaseJudge()
      elif judge_type == JudgeType.LAW:
        cls._judges[judge_type] = LawJudge()
      elif judge_type == JudgeType.FRAUD:
        cls._judges[judge_type] = FraudJudge()
      else:
        raise ValueError(f"Unknown judge type: {judge_type}")

    return cls._judges[judge_type]

  @classmethod
  def reset(cls):
    """Reset all judge instances (for testing)."""
    cls._judges = {
      JudgeType.FIN: None,
      JudgeType.CASE: None,
      JudgeType.LAW: None,
      JudgeType.FRAUD: None,
    }


__all__ = [
  "JudgeDecision",
  "ApprovalGate",
  "JudgeType",
  "JudgeRequest",
  "JudgeResponse",
  "AuditTrail",
  "PerformanceMetrics",
  "BaseJudge",
  "FinJudge",
  "CaseJudge",
  "LawJudge",
  "FraudJudge",
  "JudgeFactory",
]
