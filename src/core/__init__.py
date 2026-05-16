# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Core Gemini Function Calling Implementation
AutoGen → Native Gemini Migration.
"""

from .function_registry import FunctionRegistry
from .gemini_function_calling import (
  FunctionResult,
  FunctionTool,
  GeminiFunctionCaller,
)

__all__ = [
  "GeminiFunctionCaller",
  "FunctionTool",
  "FunctionResult",
  "FunctionRegistry",
]
