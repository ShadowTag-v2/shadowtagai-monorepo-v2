# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Base kernel data models."""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime, timezone


class KernelInput(BaseModel):
  """Input to a kernel in the chain."""

  data: Any
  metadata: dict[str, Any] = Field(default_factory=dict)
  trace_id: str | None = None


class KernelOutput(BaseModel):
  """Output from a kernel in the chain."""

  data: Any
  metadata: dict[str, Any] = Field(default_factory=dict)
  trace_id: str | None = None
  kernel_name: str
  success: bool = True
  error: str | None = None
  metrics: Optional["KernelMetrics"] = None


class KernelMetrics(BaseModel):
  """Performance metrics for a kernel execution."""

  latency_ms: float
  token_count_input: int | None = None
  token_count_output: int | None = None
  cost_usd: float | None = None
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  confidence: float | None = None
  input_hash: str | None = None
  output_hash: str | None = None
