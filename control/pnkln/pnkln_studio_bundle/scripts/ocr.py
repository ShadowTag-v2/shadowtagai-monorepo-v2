# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""OCR using Cloud Vision and summarization via Gemini."""

from __future__ import annotations
from collections.abc import Iterable
from google.cloud import vision
from vertexai.generative_models import Part
from .vertex import gemini

_vc = vision.ImageAnnotatorClient()
_gm = gemini()


def ocr_path(path: str) -> str:
  with open(path, "rb") as f:
    img = vision.Image(content=f.read())
  r = _vc.document_text_detection(image=img)
  if r.full_text_annotation and r.full_text_annotation.text:
    return r.full_text_annotation.text
  return r.text_annotations[0].description if r.text_annotations else ""


def summarize_ocr(paths: Iterable[str]) -> str:
  texts = []
  for p in paths:
    try:
      texts.append(ocr_path(p))
    except Exception:
      texts.append("")
  joined = "\n\n".join(texts)
  return _gm.generate_content(
    [Part.from_text("Summarize the following OCR content:"), Part.from_text(joined)]
  ).text
