"""
Quality Gates Module

Implements multi-faceted quality checks:
- Items ingested per day (target: 10,000)
- Source diversity (minimum: 5 sources)
- Cost per item (target: $0.001)
- Relevance scores (minimum: 60%)
- Timeliness (< 24 hours old)
- Completeness (85% field completion)
"""

from .gates import QualityGateResult, QualityGates

__all__ = ["QualityGates", "QualityGateResult"]
