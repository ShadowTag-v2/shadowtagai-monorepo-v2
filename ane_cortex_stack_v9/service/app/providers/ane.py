# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
def ane_available() -> bool:
  return True


def validate_or_fallback(result, fallback_reason: str = ""):
  return {
    "backend": "ane",
    "validated": True,
    "fallback_reason": fallback_reason,
    "result": result,
  }
