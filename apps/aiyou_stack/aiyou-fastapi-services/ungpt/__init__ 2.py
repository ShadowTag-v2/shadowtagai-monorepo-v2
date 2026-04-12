"""
UnGPT v2.0 - Static vs Dynamic Multi-Model Pipeline

Architecture:
- Static Truth (SuperGrok): L0, L3, L5, L7 - Intent validation
- Dynamic Execution (Claude): L1, L4, L6 - Code execution
- Infinite Loop (Gemini/GPT): L2 - Generation

Usage:
    from ungpt import UnGPTOrchestrator

    orchestrator = UnGPTOrchestrator()
    result = await orchestrator.run("Your research query")
"""

from .orchestrator import PipelineResult, UnGPTOrchestrator

__version__ = "2.0.0"
__all__ = ["UnGPTOrchestrator", "PipelineResult"]
