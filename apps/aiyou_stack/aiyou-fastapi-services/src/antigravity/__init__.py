"""Antigravity - The Central Brain with Kosmos Cavalry Squadron
=============================================================

Orchestrates all LLMs with embedded Kosmos AI Scientist instances.
Each stage has 430 agents aligned to ATP 3-20.96 Cavalry Squadron doctrine.

Pipeline: Gemini+Kosmos → Perplexity+Kosmos → Grok+Kosmos → 10×GeminiCode+Kosmos → CodePMCS → Deploy

Total: 5,590 agents (430 × 13 Kosmos instances)
- Full ATP 3-20.96 alignment: HHT(115) + RECON(180) + SURV(60) + MFRC(60) + Mortar(15)
- Differentiated reconnaissance: Zone/Area/Route/Force (ATP Ch.3)
- Differentiated security: Screen/Guard/Cover (ATP Ch.4)
- No separate voting step - consensus embedded per stage

Army Doctrine Integration (v3.0.0):
- FM 6-0: MDMP 7-step planning, TLP 8-step rapid planning
- ATP 5-19: 5-step CRM (Composite Risk Management)
- FM 3-0: Six Warfighting Functions (C2, Intel, Fires, Movement, Sustainment, Protection)
- FM 7-8: Battle Drills for error handling (React to Contact, Break Contact, etc.)
- ADP 6-22: Agent attributes and competencies (CHARACTER, PRESENCE, INTELLECT)
"""

from .deploy import DeployManager
from .execute import GeminiCodeAssistPool, create_execution_pool
from .intake import Atom, GeminiIntake, JuraTier, RiskLevel
from .pipeline import AntigravityPipeline, PipelineResult

# ResearchChain removed in v2.0

__all__ = [
    "AntigravityPipeline",
    "Atom",
    "DeployManager",
    "GeminiCodeAssistPool",
    "GeminiIntake",
    "JuraTier",
    "PipelineResult",
    "RiskLevel",
    "create_execution_pool",
]

__version__ = "3.0.0"  # Major version bump: Full Army Doctrine Integration
