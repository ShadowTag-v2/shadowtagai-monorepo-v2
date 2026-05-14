# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Core Gemini Function Calling Implementation
AutoGen → Native Gemini Migration
"""

from .gemini_function_calling import (
    GeminiFunctionCaller,
    FunctionTool,
    FunctionResult,
)
from .function_registry import FunctionRegistry

__all__ = [
    "GeminiFunctionCaller",
    "FunctionTool",
    "FunctionResult",
    "FunctionRegistry",
]
