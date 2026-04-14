"""Compliance Modules Package

Each module implements a specific regulation with:
- Metadata (articles, sections, jurisdiction)
- Validation rules
- Checklist templates
- Report generators
"""

from app.compliance.modules.base import ComplianceModule

__all__ = ["ComplianceModule"]
