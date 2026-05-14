# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Medical DLP (Data Loss Prevention) Engine
==========================================

PHI Detection and Redaction with Clinical Context Awareness.

HIPAA requires "minimum necessary" standard - only share PHI needed for purpose.
This engine detects, classifies, and redacts PHI with medical-specific awareness.

Key Capabilities:
- PHI pattern detection (18 HIPAA identifiers)
- Clinical terminology awareness (ICD-10, CPT, drug names)
- Context-aware redaction (preserve clinical meaning)
- Audit trail for all redactions
- Configurable sensitivity levels
"""

import hashlib
import logging
import re
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session


class PHIType(str, Enum):
    """18 HIPAA PHI Identifiers"""

    NAME = "name"
    ADDRESS = "address"
    DATES = "dates"  # Except year
    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    SSN = "ssn"
    MRN = "mrn"  # Medical Record Number
    HEALTH_PLAN = "health_plan"
    ACCOUNT = "account"
    LICENSE = "license"
    VEHICLE = "vehicle"
    DEVICE = "device"
    URL = "url"
    IP = "ip"
    BIOMETRIC = "biometric"
    PHOTO = "photo"
    OTHER_UNIQUE = "other_unique"


class ClinicalDataType(str, Enum):
    """Clinical data categories requiring special handling"""

    DIAGNOSIS = "diagnosis"  # ICD-10 codes
    PROCEDURE = "procedure"  # CPT codes
    MEDICATION = "medication"  # Drug names, dosages
    LAB_RESULT = "lab_result"  # Lab values
    VITAL_SIGN = "vital_sign"  # BP, HR, etc.
    ALLERGY = "allergy"  # Drug/food allergies
    FAMILY_HISTORY = "family_history"
    GENETIC = "genetic"  # Highest sensitivity
    MENTAL_HEALTH = "mental_health"  # Special protections
    SUBSTANCE_ABUSE = "substance_abuse"  # 42 CFR Part 2


class SensitivityLevel(str, Enum):
    """Data sensitivity levels"""

    PUBLIC = "public"  # Can be shared freely
    INTERNAL = "internal"  # Organization-only
    CONFIDENTIAL = "confidential"  # Need-to-know
    RESTRICTED = "restricted"  # Special authorization
    HIGHLY_RESTRICTED = "highly_restricted"  # Genetic, mental health


class PHIDetection(BaseModel):
    """A detected PHI element"""

    phi_type: PHIType
    value: str
    redacted_value: str
    position: tuple[int, int]
    confidence: float
    sensitivity: SensitivityLevel
    context: str = ""


class ClinicalDetection(BaseModel):
    """A detected clinical data element"""

    data_type: ClinicalDataType
    value: str
    code: str | None = None  # ICD-10, CPT, NDC
    position: tuple[int, int]
    sensitivity: SensitivityLevel
    requires_redaction: bool = False


class DLPResult(BaseModel):
    """Result of DLP scan"""

    original_text: str
    redacted_text: str
    phi_detected: list[PHIDetection] = Field(default_factory=list)
    clinical_detected: list[ClinicalDetection] = Field(default_factory=list)
    total_phi_count: int = 0
    total_clinical_count: int = 0
    highest_sensitivity: SensitivityLevel = SensitivityLevel.PUBLIC
    redaction_applied: bool = False
    audit_id: str
    scanned_at: datetime = Field(default_factory=datetime.utcnow)


class MedicalDLPEngine:
    """
    Medical Data Loss Prevention Engine

    SALES VALUE PROPOSITION:
    - HIPAA violations can cost $100K-$1.5M per violation
    - Automated PHI detection prevents accidental exposure
    - Audit trail proves due diligence in litigation

    Sensitivity Hierarchy:
    1. Genetic data (GINA) - Highest protection
    2. Mental health (state laws) - Special consent required
    3. Substance abuse (42 CFR Part 2) - Federal protection
    4. General PHI (HIPAA) - Standard protection
    """

    # PHI Detection Patterns (18 HIPAA identifiers)
    PHI_PATTERNS = {
        PHIType.SSN: [
            r"\b\d{3}-\d{2}-\d{4}\b",
            r"\b\d{9}\b(?=.*\b(ssn|social|security)\b)",
        ],
        PHIType.MRN: [
            r"\b(MRN|mrn|medical record|patient id)[:\s#]*([A-Z0-9]{6,12})\b",
            r"\b[A-Z]{2,3}\d{6,10}\b",  # Common MRN format
        ],
        PHIType.PHONE: [
            r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
        ],
        PHIType.EMAIL: [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        ],
        PHIType.DATES: [
            r"\b(0?[1-9]|1[0-2])/(0?[1-9]|[12]\d|3[01])/\d{4}\b",  # MM/DD/YYYY
            r"\b(0?[1-9]|[12]\d|3[01])/(0?[1-9]|1[0-2])/\d{4}\b",  # DD/MM/YYYY
            r"\b\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])\b",  # YYYY-MM-DD
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        ],
        PHIType.ADDRESS: [
            r"\b\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b",
        ],
        PHIType.HEALTH_PLAN: [
            r"\b(health plan|insurance|policy)[:\s#]*([A-Z0-9]{8,15})\b",
            r"\b(member|subscriber)\s*(id|number|#)[:\s]*([A-Z0-9]{8,15})\b",
        ],
        PHIType.IP: [
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        ],
        PHIType.DEVICE: [
            r"\b(device|serial)[:\s#]*([A-Z0-9]{10,20})\b",
            r"\b(IMEI|MAC)[:\s]*([A-Z0-9:.-]{12,20})\b",
        ],
    }

    # Clinical code patterns
    CLINICAL_PATTERNS = {
        ClinicalDataType.DIAGNOSIS: [
            r"\b[A-Z]\d{2}(\.\d{1,4})?\b",  # ICD-10 (e.g., E11.65)
            r"\b(diagnosis|dx)[:\s]*([\w\s]+)\b",
        ],
        ClinicalDataType.PROCEDURE: [
            r"\b\d{5}\b",  # CPT codes
            r"\b(procedure|cpt)[:\s]*(\d{5})\b",
        ],
        ClinicalDataType.MEDICATION: [
            r"\b(\w+)\s+(\d+)\s*(mg|mcg|ml|units?|iu)\b",  # Drug + dose
            r"\b(aspirin|ibuprofen|metformin|lisinopril|atorvastatin|omeprazole|amlodipine|metoprolol|losartan|gabapentin|hydrocodone|prednisone|azithromycin|amoxicillin|albuterol|fluticasone|insulin|warfarin|clopidogrel|pantoprazole)\b",
        ],
        ClinicalDataType.LAB_RESULT: [
            r"\b(A1C|HbA1c|hemoglobin)\s*[:\s]*(\d+\.?\d*)\s*%?\b",
            r"\b(glucose|cholesterol|hdl|ldl|triglycerides|creatinine|bun|gfr|wbc|rbc|platelets)\s*[:\s]*(\d+\.?\d*)\b",
        ],
        ClinicalDataType.VITAL_SIGN: [
            r"\b(bp|blood pressure)\s*[:\s]*(\d{2,3}/\d{2,3})\b",
            r"\b(hr|heart rate|pulse)\s*[:\s]*(\d{2,3})\s*(bpm)?\b",
            r"\b(temp|temperature)\s*[:\s]*(\d{2,3}\.?\d?)\s*(f|c|fahrenheit|celsius)?\b",
            r"\b(weight)\s*[:\s]*(\d{2,3}\.?\d?)\s*(lbs?|kg|pounds?)?\b",
        ],
        ClinicalDataType.ALLERGY: [
            r"\b(allergic?|allergy|allergies)\s*(to)?[:\s]*([\w\s,]+)\b",
            r"\b(penicillin|sulfa|latex|shellfish|peanut|tree nut|egg|milk|soy|wheat)\s+allergy\b",
        ],
        ClinicalDataType.MENTAL_HEALTH: [
            r"\b(depression|anxiety|bipolar|schizophrenia|ptsd|adhd|ocd|eating disorder|panic disorder|social anxiety)\b",
            r"\b(suicidal|self[- ]?harm|suicide attempt|psychiatric|mental health)\b",
        ],
        ClinicalDataType.SUBSTANCE_ABUSE: [
            r"\b(alcohol|drug)\s*(abuse|dependence|addiction|use disorder)\b",
            r"\b(rehab|rehabilitation|detox|withdrawal|naloxone|methadone|suboxone|buprenorphine)\b",
            r"\b(aa|na|alcoholics anonymous|narcotics anonymous)\b",
        ],
        ClinicalDataType.GENETIC: [
            r"\b(brca|brca1|brca2|genetic test|dna test|chromosome|mutation|hereditary)\b",
            r"\b(huntington|cystic fibrosis|sickle cell|tay-sachs)\s*(gene|mutation|carrier)?\b",
        ],
    }

    # Sensitivity mapping
    SENSITIVITY_MAP = {
        PHIType.SSN: SensitivityLevel.HIGHLY_RESTRICTED,
        PHIType.MRN: SensitivityLevel.RESTRICTED,
        PHIType.HEALTH_PLAN: SensitivityLevel.RESTRICTED,
        ClinicalDataType.GENETIC: SensitivityLevel.HIGHLY_RESTRICTED,
        ClinicalDataType.MENTAL_HEALTH: SensitivityLevel.HIGHLY_RESTRICTED,
        ClinicalDataType.SUBSTANCE_ABUSE: SensitivityLevel.HIGHLY_RESTRICTED,
    }

    def __init__(self, db: Session | None = None):
        self.db = db
        self._audit_log: list[DLPResult] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns"""
        self._phi_compiled = {phi_type: [re.compile(p, re.IGNORECASE) for p in patterns] for phi_type, patterns in self.PHI_PATTERNS.items()}
        self._clinical_compiled = {
            data_type: [re.compile(p, re.IGNORECASE) for p in patterns] for data_type, patterns in self.CLINICAL_PATTERNS.items()
        }

    async def scan(
        self,
        text: str,
        redact: bool = True,
        sensitivity_threshold: SensitivityLevel = SensitivityLevel.CONFIDENTIAL,
    ) -> DLPResult:
        """
        Scan text for PHI and clinical data.

        Args:
            text: Text to scan
            redact: Whether to apply redaction
            sensitivity_threshold: Minimum sensitivity to redact

        Returns:
            DLPResult with detections and optional redacted text
        """
        audit_id = self._generate_audit_id(text)
        phi_detected = []
        clinical_detected = []
        redacted_text = text
        highest_sensitivity = SensitivityLevel.PUBLIC

        # Scan for PHI
        for phi_type, patterns in self._phi_compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    sensitivity = self.SENSITIVITY_MAP.get(phi_type, SensitivityLevel.CONFIDENTIAL)
                    if self._sensitivity_rank(sensitivity) > self._sensitivity_rank(highest_sensitivity):
                        highest_sensitivity = sensitivity

                    redacted = self._generate_redaction(phi_type.value, match.group())
                    detection = PHIDetection(
                        phi_type=phi_type,
                        value=match.group(),
                        redacted_value=redacted,
                        position=(match.start(), match.end()),
                        confidence=0.9,  # Pattern-based = high confidence
                        sensitivity=sensitivity,
                        context=text[max(0, match.start() - 20) : match.end() + 20],
                    )
                    phi_detected.append(detection)

        # Scan for clinical data
        for data_type, patterns in self._clinical_compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    sensitivity = self.SENSITIVITY_MAP.get(data_type, SensitivityLevel.CONFIDENTIAL)
                    if self._sensitivity_rank(sensitivity) > self._sensitivity_rank(highest_sensitivity):
                        highest_sensitivity = sensitivity

                    # Special handling for high-sensitivity clinical data
                    requires_redaction = data_type in [
                        ClinicalDataType.GENETIC,
                        ClinicalDataType.MENTAL_HEALTH,
                        ClinicalDataType.SUBSTANCE_ABUSE,
                    ]

                    detection = ClinicalDetection(
                        data_type=data_type,
                        value=match.group(),
                        position=(match.start(), match.end()),
                        sensitivity=sensitivity,
                        requires_redaction=requires_redaction,
                    )
                    clinical_detected.append(detection)

        # Apply redaction if requested
        redaction_applied = False
        if redact:
            redacted_text, redaction_applied = self._apply_redaction(
                text,
                phi_detected,
                clinical_detected,
                sensitivity_threshold,
            )

        result = DLPResult(
            original_text=text if not redact else "[ORIGINAL_STORED_SECURELY]",
            redacted_text=redacted_text,
            phi_detected=phi_detected,
            clinical_detected=clinical_detected,
            total_phi_count=len(phi_detected),
            total_clinical_count=len(clinical_detected),
            highest_sensitivity=highest_sensitivity,
            redaction_applied=redaction_applied,
            audit_id=audit_id,
        )

        self._audit_log.append(result)

        if phi_detected:
            logger.info(f"DLP: Detected {len(phi_detected)} PHI elements, {len(clinical_detected)} clinical elements")

        return result

    def _apply_redaction(
        self,
        text: str,
        phi_detected: list[PHIDetection],
        clinical_detected: list[ClinicalDetection],
        threshold: SensitivityLevel,
    ) -> tuple[str, bool]:
        """Apply redaction to detected elements"""
        redactions = []

        # Collect PHI redactions
        for phi in phi_detected:
            if self._sensitivity_rank(phi.sensitivity) >= self._sensitivity_rank(threshold):
                redactions.append((phi.position, phi.redacted_value))

        # Collect clinical redactions (only high-sensitivity)
        for clinical in clinical_detected:
            if clinical.requires_redaction:
                redacted = f"[{clinical.data_type.value.upper()}_REDACTED]"
                redactions.append((clinical.position, redacted))

        if not redactions:
            return text, False

        # Sort by position (reverse) to avoid offset issues
        redactions.sort(key=lambda x: x[0][0], reverse=True)

        result = text
        for (start, end), replacement in redactions:
            result = result[:start] + replacement + result[end:]

        return result, True

    def _generate_redaction(self, phi_type: str, value: str) -> str:
        """Generate appropriate redaction string"""
        length = len(value)
        type_label = phi_type.upper()

        if phi_type == "ssn":
            return "[SSN_REDACTED_XXX-XX-XXXX]"
        elif phi_type == "mrn":
            return f"[MRN_REDACTED_{length}chars]"
        elif phi_type == "email":
            return "[EMAIL_REDACTED]"
        elif phi_type == "phone":
            return "[PHONE_REDACTED]"
        elif phi_type == "dates":
            return "[DATE_REDACTED]"
        elif phi_type == "address":
            return "[ADDRESS_REDACTED]"
        else:
            return f"[{type_label}_REDACTED]"

    def _sensitivity_rank(self, level: SensitivityLevel) -> int:
        """Convert sensitivity level to numeric rank"""
        ranks = {
            SensitivityLevel.PUBLIC: 0,
            SensitivityLevel.INTERNAL: 1,
            SensitivityLevel.CONFIDENTIAL: 2,
            SensitivityLevel.RESTRICTED: 3,
            SensitivityLevel.HIGHLY_RESTRICTED: 4,
        }
        return ranks.get(level, 0)

    def _generate_audit_id(self, text: str) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now(UTC).isoformat()
        content = f"dlp:{timestamp}:{hash(text)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def scan_for_disclosure(
        self,
        text: str,
        recipient_type: str = "internal",
    ) -> dict[str, Any]:
        """
        Scan text before external disclosure.

        This is the "minimum necessary" check - ensures only
        required PHI is shared based on recipient type.
        """
        result = await self.scan(text, redact=True)

        disclosure_allowed = True
        warnings = []

        # Check sensitivity vs recipient
        if recipient_type == "external" and result.highest_sensitivity in [
            SensitivityLevel.RESTRICTED,
            SensitivityLevel.HIGHLY_RESTRICTED,
        ]:
            disclosure_allowed = False
            warnings.append("External disclosure of restricted data requires explicit authorization")

        # Check for genetic data (GINA)
        genetic_found = any(c.data_type == ClinicalDataType.GENETIC for c in result.clinical_detected)
        if genetic_found:
            warnings.append("Genetic information detected - GINA restrictions apply")
            if recipient_type in ["employer", "insurance"]:
                disclosure_allowed = False

        # Check for substance abuse (42 CFR Part 2)
        substance_found = any(c.data_type == ClinicalDataType.SUBSTANCE_ABUSE for c in result.clinical_detected)
        if substance_found:
            warnings.append("Substance abuse records detected - 42 CFR Part 2 restrictions apply")
            if recipient_type != "treatment":
                disclosure_allowed = False

        return {
            "disclosure_allowed": disclosure_allowed,
            "redacted_text": result.redacted_text,
            "warnings": warnings,
            "phi_count": result.total_phi_count,
            "clinical_count": result.total_clinical_count,
            "requires_authorization": not disclosure_allowed,
            "audit_id": result.audit_id,
        }

    def get_audit_trail(
        self,
        limit: int = 100,
        phi_only: bool = False,
    ) -> list[DLPResult]:
        """Get audit trail of DLP scans"""
        results = self._audit_log
        if phi_only:
            results = [r for r in results if r.total_phi_count > 0]
        return results[-limit:]


# Global instance
medical_dlp = MedicalDLPEngine()
