# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum


class ContractStatus(StrEnum):
    """Contract lifecycle status"""

    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    READY_FOR_DRAFT = "ready_for_draft"
    DRAFT_GENERATED = "draft_generated"
    ATTORNEY_REVIEW = "attorney_review"
    CUSTOMER_APPROVAL = "customer_approval"
    SIGNING = "signing"
    SIGNED = "signed"
    CANCELLED = "cancelled"


class ContractType(StrEnum):
    """Supported contract types"""

    AUTO_REPAIR = "auto_repair"
    CONTRACTOR = "contractor"
    REAL_ESTATE = "real_estate"
    EMPLOYMENT = "employment"
    NDA = "nda"
    SERVICE_AGREEMENT = "service_agreement"


class Jurisdiction(StrEnum):
    """U.S. states (subset for initial launch)"""

    TX = "TX"
    CA = "CA"
    NY = "NY"
    FL = "FL"
    IL = "IL"


class PaymentStatus(StrEnum):
    """Payment status"""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
