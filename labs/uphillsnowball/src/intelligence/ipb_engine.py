"""ATP 2-01.3 Intelligence Preparation of the Battlefield (IPB).

The J-2 (Jetski/Deep Research) does NOT scrape blindly. It executes a
strict 4-step IPB process per ATP 2-01.3:

    1. Define the Operational Environment (OE)
    2. Describe Environmental Effects (MCOO)
    3. Evaluate the Threat
    4. Determine Threat Courses of Action (COAs)

Data gathering without IPB is just noise. The IPB engine returns
High-Payoff Targets (HPTs) and a synthesized Modified Combined
Obstacle Overlay (MCOO) for the J-5 Architect to plan against.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from temporalio import activity

logger = logging.getLogger("J2-IPB-Engine")


@dataclass
class OperationalEnvironment:
  """Step 1 output: boundaries, areas of interest, named areas of interest."""

  boundaries: dict[str, Any] = field(default_factory=dict)
  areas_of_interest: list[str] = field(default_factory=list)
  named_areas_of_interest: list[str] = field(default_factory=list)


@dataclass
class MCOO:
  """Modified Combined Obstacle Overlay — Step 2 output.

  Maps friction points, terrain advantages, and environmental constraints.
  """

  friction_points: list[str] = field(default_factory=list)
  terrain_advantages: list[str] = field(default_factory=list)
  regulatory_constraints: list[str] = field(default_factory=list)


@dataclass
class ThreatModel:
  """Step 3 output: evaluated adversary capabilities and dispositions."""

  adversary_name: str = ""
  capability_level: str = "UNKNOWN"  # PEER, NEAR_PEER, IRREGULAR
  known_ttps: list[str] = field(default_factory=list)


@dataclass
class IPBResult:
  """Complete IPB intelligence product for J-5 consumption."""

  oe: OperationalEnvironment
  mcoo: MCOO
  threat_models: list[ThreatModel]
  high_payoff_target_list: list[str]
  mdcoa_description: str  # Most Dangerous Course of Action
  mlcoa_description: str  # Most Likely Course of Action
  status: str = "IPB_COMPLETE"


class ATP_2_01_3_IPB:
  """Intelligence Preparation of the Battlefield.

  Temporal activity. The J-2 directorate executes this before any
  operation begins. The output feeds the J-5 Architect's MDMP.
  """

  @activity.defn(name="j2_execute_ipb")
  async def execute_ipb(self, call_of_question: dict) -> dict:
    """Execute the complete 4-step IPB process.

    Args:
        call_of_question: Serialized CallOfQuestion dict.

    Returns:
        IPB result dict with MCOO, HPTs, MDCOA, and MLCOA.
    """
    logger.info("🗺️ J-2 Executing ATP 2-01.3 IPB...")

    # Step 1: Define the Operational Environment (OE)
    oe = self._define_oe(call_of_question)
    logger.info(
      "  Step 1 ✓ OE defined: %d areas of interest", len(oe.areas_of_interest)
    )

    # Step 2: Describe Environmental Effects (MCOO)
    mcoo = self._describe_effects(oe)
    logger.info("  Step 2 ✓ MCOO: %d friction points", len(mcoo.friction_points))

    # Step 3: Evaluate the Threat
    threat_models = self._evaluate_threat(call_of_question)
    logger.info("  Step 3 ✓ %d threat models evaluated", len(threat_models))

    # Step 4: Determine Threat COAs → High-Payoff Target List (HPTL)
    hptl, mdcoa, mlcoa = self._determine_coas(threat_models, mcoo)
    logger.info("  Step 4 ✓ HPTL: %d targets. IPB COMPLETE.", len(hptl))

    result = IPBResult(
      oe=oe,
      mcoo=mcoo,
      threat_models=threat_models,
      high_payoff_target_list=hptl,
      mdcoa_description=mdcoa,
      mlcoa_description=mlcoa,
    )

    return {
      "mcoo": {
        "friction_points": result.mcoo.friction_points,
        "regulatory_constraints": result.mcoo.regulatory_constraints,
      },
      "hptl": result.high_payoff_target_list,
      "mdcoa": result.mdcoa_description,
      "mlcoa": result.mlcoa_description,
      "status": result.status,
    }

  def _define_oe(self, coq: dict) -> OperationalEnvironment:
    """Step 1: Define the Operational Environment."""
    purpose = coq.get("purpose", "")
    return OperationalEnvironment(
      boundaries={"domain": purpose, "scope": "ENTERPRISE"},
      areas_of_interest=[
        "Regulatory landscape",
        "Competitor positioning",
        "Technical debt surface",
      ],
      named_areas_of_interest=[
        "EU AI Act compliance gap",
        "HIPAA Safe Harbor boundary",
        "FedRAMP authorization status",
      ],
    )

  def _describe_effects(self, oe: OperationalEnvironment) -> MCOO:
    """Step 2: Describe Environmental Effects (the terrain)."""
    return MCOO(
      friction_points=[
        "API rate limits on PACER/CourtListener",
        "Stripe webhook latency under load",
        "gVisor sandbox cold start overhead",
      ],
      terrain_advantages=[
        "Temporal.io durable execution (crash-proof)",
        "BYOC model = zero compute cost to us",
        "SHA-256 immutable missions prevent drift",
      ],
      regulatory_constraints=[
        "EU AI Act Art 5 (emotion recognition ban)",
        "NY S7263 (bias disclosure requirements)",
        "HIPAA Safe Harbor (de-identification standard)",
      ],
    )

  def _evaluate_threat(self, coq: dict) -> list[ThreatModel]:
    """Step 3: Evaluate the Threat."""
    return [
      ThreatModel(
        adversary_name="AI Hallucination (Internal)",
        capability_level="PEER",
        known_ttps=[
          "Fabricated citations (S&C vector)",
          "Confident but wrong statistical claims",
          "Context window overflow causing amnesia",
        ],
      ),
      ThreatModel(
        adversary_name="Prompt Injection (External)",
        capability_level="NEAR_PEER",
        known_ttps=[
          "Indirect injection via RAG documents",
          "System prompt extraction attempts",
          "Role-playing jailbreak patterns",
        ],
      ),
      ThreatModel(
        adversary_name="Regulatory Enforcement (Environmental)",
        capability_level="PEER",
        known_ttps=[
          "EU AI Act €35M penalty actions",
          "RAISE Act $3M per-violation fines",
          "State AG UPL enforcement actions",
        ],
      ),
    ]

  def _determine_coas(
    self, threats: list[ThreatModel], mcoo: MCOO
  ) -> tuple[list[str], str, str]:
    """Step 4: Determine Threat COAs and derive the HPTL."""
    hptl = [
      "Hallucinated legal citations (ScholarEval intercept)",
      "UPL boundary violations (AST-grep rewrite)",
      "Bias in generated content (permutation testing)",
    ]

    mdcoa = (
      "MOST DANGEROUS: AI generates a fabricated Supreme Court citation "
      "in a filing submitted to a federal judge, triggering sanctions, "
      "malpractice liability, and catastrophic reputational damage "
      "(Sullivan & Cromwell vector, April 2026)."
    )

    mlcoa = (
      "MOST LIKELY: AI provides subtly incorrect statutory interpretation "
      "that passes surface-level human review but creates liability exposure "
      "discovered only during opposing counsel's due diligence."
    )

    return hptl, mdcoa, mlcoa
