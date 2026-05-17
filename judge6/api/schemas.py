# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Pydantic Schemas for API Request/Response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Any


# Judge Request/Response


class JudgeRequest(BaseModel):
  """Request to judge an AI prompt"""

  prompt: str = Field(..., description="The AI request to assess")
  context: dict[str, Any] | None = Field(
    None, description="Additional context for assessment"
  )

  class Config:
    json_schema_extra = {
      "example": {
        "prompt": "Generate a personalized medical diagnosis based on symptoms",
        "context": {"user_type": "patient", "authenticated": True},
      }
    }


class JudgeResponse(BaseModel):
  """Response from Judge assessment"""

  request_id: str
  decision: str = Field(..., description="allow, deny, or warn")
  risk_level: str = Field(
    ..., description="catastrophic, critical, moderate, low, negligible"
  )
  confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
  reasoning: str = Field(..., description="Human-readable explanation")
  violated_rules: list[str] = Field(
    default_factory=list, description="List of violated rules"
  )
  latency_ms: int = Field(..., description="Total processing time in milliseconds")
  usage: dict[str, Any] = Field(..., description="Current usage statistics")

  class Config:
    json_schema_extra = {
      "example": {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "decision": "warn",
        "risk_level": "moderate",
        "confidence": 0.85,
        "reasoning": "ATP 5-19 Risk Assessment:\n• Layer 1 (Policy): Medical advice requires professional oversight\n• Layer 2 (Enforcement): No edge cases detected\n• Layer 3 (Rules): Medical information warning triggered",
        "violated_rules": [],
        "latency_ms": 73,
        "usage": {
          "requests_used": 42,
          "requests_limit": 1000,
          "tier": "free",
        },
      }
    }


# User Management


class UserCreate(BaseModel):
  """Create new user"""

  email: EmailStr
  password: str = Field(..., min_length=8)
  full_name: str | None = None
  company: str | None = None


class UserLogin(BaseModel):
  """User login credentials"""

  email: EmailStr
  password: str


class UserResponse(BaseModel):
  """User registration response"""

  id: int
  email: str
  full_name: str | None
  company: str | None
  tier: str
  api_key: str = Field(..., description="API key - save this, it won't be shown again!")
  monthly_limit: int
  current_usage: int


class UsageStats(BaseModel):
  """Usage statistics"""

  tier: str
  requests_used: int
  requests_limit: int
  overage: int
  percentage_used: float


# API Key Management


class APIKeyCreate(BaseModel):
  """Create new API key"""

  name: str = Field(..., description="User-friendly name for this key")


class APIKeyResponse(BaseModel):
  """API key response"""

  id: int
  name: str
  key: str = Field(..., description="Full API key - save this!")
  key_prefix: str
  created_at: str


# Subscription Management


class SubscriptionUpdate(BaseModel):
  """Update subscription tier"""

  tier: str = Field(..., description="free, starter, professional, or enterprise")
  stripe_subscription_id: str | None = None


# Policy Management


class PolicyCreate(BaseModel):
  """Create custom policy"""

  name: str
  description: str | None = None
  purpose: str = Field(..., description="ATP 5-19 Purpose: What is the intent?")
  reasons: list[str] = Field(..., description="ATP 5-19 Reasons: Why allow/deny?")
  brakes: list[str] = Field(
    ..., description="ATP 5-19 Brakes: What are the hard stops?"
  )


class PolicyResponse(BaseModel):
  """Policy response"""

  id: int
  name: str
  description: str | None
  purpose: str
  reasons: list[str]
  brakes: list[str]
  is_active: bool
  created_at: str
