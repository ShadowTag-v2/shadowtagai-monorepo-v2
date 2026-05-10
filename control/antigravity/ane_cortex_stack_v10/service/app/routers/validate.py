# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter
from pydantic import BaseModel

from ..adapters.code_graph import build_code_graph, validate_reference
from ..config import load_settings

router = APIRouter(prefix="/api")


class ValidateRequest(BaseModel):
  query: str
  repo_root: str | None = None


@router.post("/validate-reference")
def validate_reference_api(req: ValidateRequest):
  s = load_settings()
  graph = build_code_graph(req.repo_root or s.repo_root)
  return validate_reference(graph, req.query)
