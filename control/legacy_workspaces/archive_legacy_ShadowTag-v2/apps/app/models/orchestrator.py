# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from typing import Any

from pydantic import BaseModel


class DraftSpec(BaseModel):
  task: str
  constraints: dict[str, Any] | None = None
  style: str | None = None


class GenerateRequest(BaseModel):
  task: str
  constraints: dict[str, Any] | None = None
  style: str | None = None
