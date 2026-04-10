from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SalesforceContact(BaseModel):
    """Structured contact content for Salesforce."""

    token: str = Field(
        description="Verification token that MUST appear in at least one property (e.g., email)."
    )
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    mobile_phone: str | None = None
    title: str | None = None
    department: str | None = None
    description: str | None = None
    mailing_street: str | None = None
    mailing_city: str | None = None
    mailing_state: str | None = None
    mailing_postal_code: str | None = None
    mailing_country: str | None = None
    notes: str | None = None  # not posted to Salesforce; useful context
