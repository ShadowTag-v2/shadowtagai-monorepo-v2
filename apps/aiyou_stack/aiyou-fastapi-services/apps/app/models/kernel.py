"""Base kernel data models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


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
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float | None = None
    input_hash: str | None = None
    output_hash: str | None = None
