"""ShadowTag-v2JR Core Framework
PRISM Kernel, Business Plan, Operating Framework, and Context Management

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

from .business.plan import (
    AgentDesignPattern,
    BusinessMetrics,
    KillSwitch,
    KillSwitchGates,
    TechStack,
    Vertical,
    VerticalPortfolio,
    VerticalType,
)
from .context.rollup import (
    ImmediateAction,
    RestartPrompt,
    StateSummary,
    ThreadContext,
    TransferPackage,
)
from .framework.execution import (
    DecisionProtocol,
    DevelopmentConstraints,
    FrameworkReference,
    OperatingFramework,
    RiskAssessmentMatrix,
    RiskLevel,
    RiskProbability,
    RiskSeverity,
)
from .prism.kernel import FlowSymbol, PicoTrace, PrismKernel, PrismRuntime, ValueLock

__all__ = [
    # PRISM Kernel
    "FlowSymbol",
    "PicoTrace",
    "PrismKernel",
    "ValueLock",
    "PrismRuntime",
    # Business Plan
    "VerticalType",
    "BusinessMetrics",
    "Vertical",
    "VerticalPortfolio",
    "TechStack",
    "AgentDesignPattern",
    "KillSwitch",
    "KillSwitchGates",
    # Operating Framework
    "RiskProbability",
    "RiskSeverity",
    "RiskLevel",
    "RiskAssessmentMatrix",
    "DecisionProtocol",
    "DevelopmentConstraints",
    "FrameworkReference",
    "OperatingFramework",
    # Context Management
    "ImmediateAction",
    "StateSummary",
    "ThreadContext",
    "RestartPrompt",
    "TransferPackage",
]

__version__ = "1.0.0"
__author__ = "ShadowTag-v2JR System"
"""
Core Gemini Function Calling Implementation
AutoGen → Native Gemini Migration
"""

from .function_registry import FunctionRegistry  # noqa: E402
from .gemini_function_calling import (  # noqa: E402
    FunctionResult,
    FunctionTool,
    GeminiFunctionCaller,
)

__all__ = [
    "FunctionRegistry",
    "FunctionResult",
    "FunctionTool",
    "GeminiFunctionCaller",
]
