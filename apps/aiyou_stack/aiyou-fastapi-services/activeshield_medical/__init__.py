"""ActiveShieldMedical - AI Liability Protection for Digital Health
================================================================

Enterprise compliance layer for AI-powered health platforms.
Designed for SB 243 (California), HIPAA, and emerging AI regulations.

Three-Tier Defense Architecture:
- Pre-hoc: Input validation, pattern matching, consent verification
- Mid-hoc: Real-time content moderation, DLP, clinical decision gating
- Post-hoc: Immutable audit logging, compliance certification, evidence packaging

Pricing:
- Phase 1 (Retrofit): $500K implementation
- Phase 2 (SaaS + Indemnification): $500K+ annually

Target Market:
- Digital health platforms with chatbots
- Mental health apps (self-harm liability)
- Symptom checkers (misdiagnosis liability)
- Telehealth intake systems

Domain: activeshieldmedical.com
"""

from activeshield_medical.core.clinical_gateway import ClinicalDecisionGateway
from activeshield_medical.core.liability_shield import LiabilityShield
from activeshield_medical.core.medical_dlp import MedicalDLPEngine
from activeshield_medical.core.sb243_compliance import SB243ComplianceEngine

__version__ = "1.0.0"
__all__ = [
    "ClinicalDecisionGateway",
    "LiabilityShield",
    "MedicalDLPEngine",
    "SB243ComplianceEngine",
]
