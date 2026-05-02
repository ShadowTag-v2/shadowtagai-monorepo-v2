from pydantic import BaseModel
from typing import Any


class DraftSpec(BaseModel):
    task: str
    constraints: dict[str, Any] | None = None
    style: str | None = None


class GenerateRequest(BaseModel):
    task: str
    constraints: dict[str, Any] | None = None
    style: str | None = None
