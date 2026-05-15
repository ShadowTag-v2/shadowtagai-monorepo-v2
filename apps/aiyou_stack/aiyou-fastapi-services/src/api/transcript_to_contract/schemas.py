from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from .enums import ContractType, Jurisdiction


class SwarmQueryPayload(BaseModel):
    task: str
    target: str | None = None


class GCPServiceIdentityJWT(BaseModel):
    """Pydantic parsing layer enforcing Zero-Trust JWT structure."""

    iss: str | None = None
    sub: str | None = None
    email: EmailStr
    aud: str | None = None


class UploadAudioRequest(BaseModel):
    """Request to upload negotiation audio"""

    contract_type: ContractType
    jurisdiction: Jurisdiction
    customer_location_state: Jurisdiction
    consent_obtained: bool = Field(
        ...,
        description="Whether all-party consent was obtained for recording",
    )


class UploadAudioResponse(BaseModel):
    """Response after audio upload"""

    job_id: UUID
    upload_url: str = Field(..., description="Signed URL for audio file upload (valid 1 hour)")
    consent_form_url: str | None = Field(None, description="URL to download consent form PDF")
    message: str


class TranscriptSegment(BaseModel):
    """Individual segment of transcript"""

    speaker: str
    start_time: float
    end_time: float
    text: str
    confidence: float = Field(..., ge=0, le=1)


class Party(BaseModel):
    """Party to contract"""

    name: str
    contact: str | None = None
    address: str | None = None


class PaymentTerms(BaseModel):
    """Payment terms"""

    total_cents: int
    currency: str = "USD"
    due_date: date | None = None
    payment_method: str | None = None


class ContractDraft(BaseModel):
    """AI-generated contract draft"""

    contract_id: UUID
    title: str
    parties: dict[str, Party]
    services: list[str]
    payment: PaymentTerms
    timeline: dict[str, Any]
    draft_markdown: str
    ai_reasoning: str = Field(..., description="Explanation of how AI generated this contract")
    validation_warnings: list[str] = []
