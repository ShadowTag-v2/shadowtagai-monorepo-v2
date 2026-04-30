from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, confloat, conlist

# Define the allowed literal values for stricter validation
SourceType = Literal[
    "regulation",
    "news",
    "rfp",
    "competitor-doc",
    "blog",
    "draft_bill",
    "lawsuit",
    "guidance",
]
ChangeType = Literal["new_law", "amendment", "guidance", "ruling", "proposal", "cancellation"]
RiskTag = Literal[
    "compliance_deadline",
    "fine_per_violation",
    "reputational_risk",
    "operational_impact",
    "new_opportunity",
]


class IntelEvent(BaseModel):
    """A structured, comparable intelligence event generated from a raw source document."""

    source_type: SourceType = Field(..., description="The classification of the source document.")
    jurisdiction: str = Field(
        ...,
        description="The ISO 3166-2 code for the relevant jurisdiction (e.g., 'US-CA', 'EU', 'GB').",
    )
    effective_date: date | None = Field(
        None,
        description="The date when the event (e.g., a law) becomes effective, in YYYY-MM-DD format.",
    )
    topic: conlist(str, min_length=1) = Field(
        ...,
        description="A list of specific, machine-readable topics covered (e.g., 'ai_disclosure', 'chatbot_labeling').",
    )
    change_type: ChangeType = Field(..., description="The nature of the change being reported.")
    summary: str = Field(
        ...,
        description="A concise, human-readable summary of the event (2-3 sentences).",
    )
    impacts: conlist(str, min_length=1) = Field(
        ...,
        description="A list of direct, first-order consequences or requirements.",
    )
    risk_tags: list[RiskTag] = Field(
        default_factory=list,
        description="A list of standardized risk tags associated with the event.",
    )
    confidence: confloat(ge=0.0, le=1.0) = Field(
        ...,
        description="The model's confidence in the accuracy of the extracted data (0.0 to 1.0).",
    )
