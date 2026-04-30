"""Atomic Code Generation Pipeline
================================
Multi-model pipeline for intelligent code generation.

Architecture:
- Gemini 3 Pro: Design wizard, parsing, test generation
- Perplexity Sonar: Deep research and citation gathering
- Grok Code Fast 1: Trend analysis, X insights, rapid coding
- Opus 4.5: Integration and final output

Philosophy: "Slow is smooth, smooth is fast"
"""

from .antigravity_runner import (
    AntigravityConfig,
    AntigravityRunner,
    HeadlessInstance,
)
from .deploy_flow import (
    DeploymentResult,
    DeployReadyOrchestrator,
    DeployResult,
    DeployStage,
    DeployTarget,
    ImplementationResult,
    ScaffoldResult,
    TestResult,
)
from .orchestrator import (
    AtomicPipelineOrchestrator,
    AtomicTask,
    PipelineConfig,
    PipelineResult,
    PipelineStage,
)

__all__ = [
    # Orchestrator
    "AtomicPipelineOrchestrator",
    "PipelineConfig",
    "PipelineStage",
    "AtomicTask",
    "PipelineResult",
    # Antigravity
    "AntigravityRunner",
    "AntigravityConfig",
    "HeadlessInstance",
    # Deploy Flow
    "DeployReadyOrchestrator",
    "DeployStage",
    "DeployTarget",
    "DeployResult",
    "ScaffoldResult",
    "ImplementationResult",
    "TestResult",
    "DeploymentResult",
]

__version__ = "1.1.0"
