# ActiveShield MCF - Module Implementation Guide

## Overview

Each compliance module in the MCF implements a specific regulation and provides:


- **Metadata** - Regulation info, version, jurisdiction

- **Control definitions** - Specific requirements to assess

- **Validation rules** - Rules for content checking

- **Assessment logic** - How to evaluate compliance

- **Report generation** - Audit documentation

## Module Architecture

```

ComplianceModule (Abstract Base)
├── _define_metadata() -> ModuleMetadata
├── _define_controls() -> list[ControlDefinition]
├── _define_validation_rules() -> list[ValidationRule]
├── assess_control() -> ControlResult
├── determine_risk_tier() -> RiskTier
├── validate_content() -> list[ValidationViolation]
├── generate_checklist() -> list[dict]
└── generate_report_template() -> dict

```

## Creating a Custom Module

### Step 1: Create Module File

```python

# app/compliance/modules/my_regulation.py

from app.models.compliance import (
    AssessmentInput,
    ComplianceStatus,
    ControlDefinition,
    ControlResult,
    Jurisdiction,
    ModuleMetadata,
    RegulationId,
    RiskTier,
    ValidationRule,
    ValidationViolation,
)
from app.compliance.modules.base import ComplianceModule
from app.compliance.registry import register_module


@register_module(RegulationId.MY_REGULATION)
class MyRegulationModule(ComplianceModule):
    """My Custom Regulation Module"""

    def _define_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id=RegulationId.MY_REGULATION,
            name="My Regulation Name",
            short_name="MY REG",
            version="1.0",
            jurisdiction=Jurisdiction.US,
            description="Description of the regulation",
            effective_date=datetime(2024, 1, 1),
            articles=["Article 1", "Article 2"],
            official_url="https://example.com/regulation",
            pricing_addon_usd=50.0
        )

    def _define_controls(self) -> list[ControlDefinition]:
        return [
            ControlDefinition(
                control_id="MYREG-1.1",
                name="Control Name",
                description="What this control requires",
                article_ref="Article 1",
                required_evidence=["Evidence type 1", "Evidence type 2"]
            ),
            # Add more controls...
        ]

    def _define_validation_rules(self) -> list[ValidationRule]:
        return [
            ValidationRule(
                rule_id="MYREG-VAL-001",
                name="Rule Name",
                description="What this rule checks",
                category="category",
                severity="high",
                auto_check=True
            ),
            # Add more rules...
        ]

    async def assess_control(
        self,
        control: ControlDefinition,
        input_data: AssessmentInput
    ) -> ControlResult:
        """Assess a single control"""
        # Your assessment logic here
        return ControlResult(
            control_id=control.control_id,
            control_name=control.name,
            module_id=self.module_id,
            status=ComplianceStatus.COMPLIANT,
            score=1.0,
            evidence="Assessment evidence"
        )

    def determine_risk_tier(self, input_data: AssessmentInput) -> Optional[RiskTier]:
        """Determine risk classification"""
        if input_data.is_high_risk_decision:
            return RiskTier.HIGH
        return RiskTier.MINIMAL

```

### Step 2: Add to RegulationId Enum

```python

# app/models/compliance.py

class RegulationId(str, Enum):
    # Existing regulations...
    MY_REGULATION = "my_regulation"  # Add new ID

```

### Step 3: Register in Auto-Register

```python

# app/compliance/registry.py

def auto_register_modules() -> None:
    # Existing imports...

    try:
        from app.compliance.modules import my_regulation  # noqa: F401
        logger.info("Registered My Regulation module")
    except ImportError as e:
        logger.warning(f"Failed to import My Regulation module: {e}")

```

## Built-in Modules

### EU AI Act (`eu_ai_act`)

**Controls:** 12
**Focus:** Risk classification, transparency, human oversight

Key controls:

- EU-AI-9.1: Risk Management System

- EU-AI-50.1: AI-Generated Content Disclosure

- EU-AI-14.1: Human Oversight Mechanisms

### GDPR (`gdpr`)

**Controls:** 14
**Focus:** Data protection, privacy rights, lawful basis

Key controls:

- GDPR-5.1c: Data Minimization

- GDPR-6.1: Lawful Basis for Processing

- GDPR-35: Data Protection Impact Assessment

### DSA (`dsa`)

**Controls:** 11
**Focus:** Content moderation, platform transparency

Key controls:

- DSA-14: Notice and Action Mechanism

- DSA-27: Recommender System Transparency

- DSA-34: Systemic Risk Assessment (VLOPs)

### CA SB 243 (`ca_sb_243`)

**Controls:** 11
**Focus:** Self-harm detection, minor protection

Key controls:

- SB243-1.1: Self-Harm Detection System

- SB243-2.1: Age Verification Mechanism

- SB243-3.1: Parental Consent Collection

### HIPAA (`hipaa`)

**Controls:** 14
**Focus:** PHI handling, security, breach notification

Key controls:

- HIPAA-PR-1: PHI Use and Disclosure Policies

- HIPAA-TS-1: Access Control

- HIPAA-BA-1: Business Associate Agreements

### COPPA (`coppa`)

**Controls:** 11
**Focus:** Children's privacy, parental consent

Key controls:

- COPPA-5.1: Verifiable Parental Consent

- COPPA-4.1: Privacy Policy Posting

- COPPA-8.1: Data Security Measures

### NIST AI RMF (`nist_rmf`)

**Controls:** 15
**Focus:** AI risk management (GOVERN, MAP, MEASURE, MANAGE)

Key controls:

- NIST-GOV-1.1: AI Risk Management Policy

- NIST-MAP-1.1: AI System Context

- NIST-MEA-2.1: Trustworthiness Assessment

### ISO 42001 (`iso_42001`)

**Controls:** 22
**Focus:** AI management system (Clauses 4-10)

Key controls:

- ISO42001-5.2: AI Policy

- ISO42001-8.2: AI System Impact Assessment

- ISO42001-9.2: Internal Audit

## Validation Rules

Validation rules check LLM-generated content for compliance violations:

```python
async def _check_validation_rule(
    self,
    rule: ValidationRule,
    content: str,
    context: Optional[str]
) -> Optional[ValidationViolation]:
    """Check a single validation rule"""
    content_lower = content.lower()

    # Pattern matching example
    if "prohibited term" in content_lower:
        return ValidationViolation(
            module_id=self.module_id,
            rule_id=rule.rule_id,
            severity="high",
            description="Prohibited term detected",
            location="prohibited term",
            suggested_fix="Remove or rephrase the term",
            article_reference="Regulation Article X"
        )

    return None  # No violation

```

## Best Practices


1. **Be specific** - Each control should map to a specific regulation requirement

2. **Provide remediation** - Always include actionable remediation guidance

3. **Consider context** - Use input metadata to determine applicability

4. **Validate early** - Use validation rules for quick content checks

5. **Document evidence** - Define what evidence is needed for each control
