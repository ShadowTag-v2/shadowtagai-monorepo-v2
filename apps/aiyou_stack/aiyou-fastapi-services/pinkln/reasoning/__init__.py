"""
Reasoning frameworks for the pinkln Agent Architecture System.

Implements multiple reasoning strategies:
- CoT (Chain of Thought): Linear step-by-step reasoning
- ToT (Tree of Thoughts): Branching exploration
- RCR (Reflect-Critique-Refine): Self-improvement cycle
- MAD (Multi-Agent Debate): Collaborative refinement
- DTE (Debate-Train-Evolve): Evolutionary optimization
- PanelGPT: Expert panel simulation
"""

from .cot import ChainOfThought
from .mad import MultiAgentDebate
from .rcr import ReflectCritiqueRefine
from .tot import TreeOfThoughts
from .ultrathink import UltrathinkEngine

__all__ = [
    "ChainOfThought",
    "TreeOfThoughts",
    "ReflectCritiqueRefine",
    "MultiAgentDebate",
    "UltrathinkEngine",
]
