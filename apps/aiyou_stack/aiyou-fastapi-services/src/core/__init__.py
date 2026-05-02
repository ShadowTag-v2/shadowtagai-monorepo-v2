"""Core RAG, PRISM, Business, Framework, and Context components."""

from .retriever import RetrievedChunk, VertexRAGRetriever
from .router import RouteResponse, RoutingMethod, SelfRouteController

# Names re-exported lazily to avoid heavy module-level side-effects
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # business
    "BusinessMetrics": (".business.plan", "BusinessMetrics"),
    "KillSwitchGates": (".business.plan", "KillSwitchGates"),
    "VerticalPortfolio": (".business.plan", "VerticalPortfolio"),
    "VerticalType": (".business.plan", "VerticalType"),
    # context
    "ImmediateAction": (".context.rollup", "ImmediateAction"),
    "StateSummary": (".context.rollup", "StateSummary"),
    "TransferPackage": (".context.rollup", "TransferPackage"),
    # framework
    "OperatingFramework": (".framework.execution", "OperatingFramework"),
    "RiskLevel": (".framework.execution", "RiskLevel"),
    "RiskProbability": (".framework.execution", "RiskProbability"),
    "RiskSeverity": (".framework.execution", "RiskSeverity"),
    # function registry
    "FunctionRegistry": (".function_registry", "FunctionRegistry"),
    # gemini function calling
    "FunctionTool": (".gemini_function_calling", "FunctionTool"),
    "GeminiFunctionCaller": (".gemini_function_calling", "GeminiFunctionCaller"),
    # prism
    "PicoTrace": (".prism.kernel", "PicoTrace"),
    "PrismKernel": (".prism.kernel", "PrismKernel"),
    "PrismRuntime": (".prism.kernel", "PrismRuntime"),
    "ValueLock": (".prism.kernel", "ValueLock"),
}


def __getattr__(name: str):
    """Lazy attribute access for subpackage classes."""
    if name in _LAZY_IMPORTS:
        module_path, attr = _LAZY_IMPORTS[name]
        import importlib

        mod = importlib.import_module(module_path, __package__)
        return getattr(mod, attr)
    raise AttributeError(f"module 'src.core' has no attribute {name!r}")


__all__ = [
    "RetrievedChunk",
    "RouteResponse",
    "RoutingMethod",
    "SelfRouteController",
    "VertexRAGRetriever",
    *_LAZY_IMPORTS.keys(),
]
