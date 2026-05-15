"""C-Suite Swarm Dispatcher — MCP-First Persona Routing Engine.

Routes Cor.71 C-Suite troop activations through MCP servers.
Each troop is a persona-constrained agent slice that loads only
the context relevant to its domain, cutting token usage by ~40%.

Integration points:
  - Jules MCP: Task orchestration (GitHub issues, Cloud Tasks)
  - Pomelli MCP: A/B swarm testing of troop outputs
  - 5 Antigravity MCP servers: Primary execution layer

Reference KIs:
  - knowledge/csuite-swarm-headfade-strategy/artifacts/strategy.md
  - knowledge/v26-zenith-obsidian-cloudrun/artifacts/implementation_plan.md
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Troop definitions
# ---------------------------------------------------------------------------


class TroopID(str, Enum):
  """C-Suite troop identifiers from the Cor.71 Cognitive Stack."""

  ALPHA = "alpha"  # CEO Squadron — Strategy + Distribution
  BRAVO = "bravo"  # JD Squadron — Legal + Compliance
  CHARLIE = "charlie"  # CTO Squadron — Architecture + Performance
  DELTA = "delta"  # CFO Squadron — Revenue + Profit
  ECHO = "echo"  # MD Squadron — Scientific Verification


@dataclass(frozen=True)
class MCPRoute:
  """An MCP server routing target with priority ordering."""

  server: str
  domain: str
  priority: int  # 1 = primary, 2 = secondary, 3 = tertiary


@dataclass(frozen=True)
class TroopConfig:
  """Configuration for a single C-Suite troop."""

  troop_id: TroopID
  name: str
  role: str
  persona: str
  frameworks: tuple[str, ...]
  mcp_routes: tuple[MCPRoute, ...]
  context_scope: tuple[str, ...]
  milestone_owner: str | None = None
  deliverable: str | None = None

  def primary_mcp(self) -> str:
    """Return the primary MCP server for this troop."""
    for route in self.mcp_routes:
      if route.priority == 1:
        return route.server
    return self.mcp_routes[0].server if self.mcp_routes else "sequential-thinking"


# ---------------------------------------------------------------------------
# Troop registry — singleton, immutable
# ---------------------------------------------------------------------------

TROOP_REGISTRY: dict[TroopID, TroopConfig] = {
  TroopID.ALPHA: TroopConfig(
    troop_id=TroopID.ALPHA,
    name="CEO Squadron",
    role="Strategy + Distribution",
    persona="Visionary scaling, market dominance",
    frameworks=("Strategy Diamond", "Blue Ocean"),
    mcp_routes=(
      MCPRoute("StitchMCP", "design", 1),
      MCPRoute("firebase-mcp-server", "deploy", 2),
      MCPRoute("sequential-thinking", "strategy", 3),
    ),
    context_scope=(
      "design specs",
      "Firebase Data Connect docs",
      "market analysis",
    ),
    milestone_owner="M4: Distribution Play ($50k MRR)",
    deliverable="HeadFade Embed <iframe> Player via Firebase Data Connect",
  ),
  TroopID.BRAVO: TroopConfig(
    troop_id=TroopID.BRAVO,
    name="JD Squadron",
    role="Legal + Compliance",
    persona="Proactive legal auditor, liability shield",
    frameworks=("Heppner compliance", "privilege-preservation"),
    mcp_routes=(
      MCPRoute("google-developer-knowledge", "legal research", 1),
      MCPRoute("sequential-thinking", "risk assessment", 2),
      MCPRoute("firebase-mcp-server", "security rules", 3),
    ),
    context_scope=(
      "security rules",
      "legal frameworks",
      "BUSINESS_CONTEXT_LOCKED.md",
    ),
    milestone_owner="M3: Risk Simulation (supporting)",
    deliverable="Legal compliance gates on all revenue-touching code",
  ),
  TroopID.CHARLIE: TroopConfig(
    troop_id=TroopID.CHARLIE,
    name="CTO Squadron",
    role="Architecture + Performance",
    persona="Scale-to-Zero architect, Boy Scout constraints",
    frameworks=("Cloud Run serverless", "p99≤90ms SLA"),
    mcp_routes=(
      MCPRoute("chrome-devtools-mcp", "perf/Lighthouse", 1),
      MCPRoute("firebase-mcp-server", "infra", 2),
      MCPRoute("sequential-thinking", "architecture", 3),
    ),
    context_scope=(
      "Cloud Run docs",
      "Lighthouse baselines",
      "kernel_chain/ code",
      "Dockerfile",
    ),
    milestone_owner="M1: Beachhead Baseline ($3k MRR)",
    deliverable="kernel_chain/executor.py on Cloud Run with Judge#6",
  ),
  TroopID.DELTA: TroopConfig(
    troop_id=TroopID.DELTA,
    name="CFO Squadron",
    role="Revenue + Profit",
    persona="Wealth Strategist, Profit Hawk",
    frameworks=("LTV:CAC optimization", "Monte Carlo simulation"),
    mcp_routes=(
      MCPRoute("firebase-mcp-server", "Firestore analytics", 1),
      MCPRoute("sequential-thinking", "Monte Carlo", 2),
      MCPRoute("stripe-mcp", "billing", 3),
    ),
    context_scope=(
      "Stripe config",
      "Firestore analytics schema",
      "pricing models",
      "BUSINESS_CONTEXT_LOCKED.md",
    ),
    milestone_owner="M2: Upsell ($15k) + M3: Risk Sim ($10k)",
    deliverable="High-converting upsell funnel, churn retention patches",
  ),
  TroopID.ECHO: TroopConfig(
    troop_id=TroopID.ECHO,
    name="MD Squadron",
    role="Scientific Verification",
    persona="Double-verification against scientific methods",
    frameworks=("HIPAA/PII protocols", "strict compliance"),
    mcp_routes=(
      MCPRoute("sequential-thinking", "verification", 1),
      MCPRoute("google-developer-knowledge", "medical compliance", 2),
    ),
    context_scope=(
      "HIPAA requirements",
      "data flow diagrams",
      "PII inventory",
    ),
    milestone_owner="Cross-cutting verification",
    deliverable="Compliance attestation on all data-touching features",
  ),
}


# ---------------------------------------------------------------------------
# Activation keyword parser
# ---------------------------------------------------------------------------

_KEYWORD_MAP: dict[str, TroopID] = {
  "alpha": TroopID.ALPHA,
  "ceo": TroopID.ALPHA,
  "distribution": TroopID.ALPHA,
  "embed": TroopID.ALPHA,
  "iframe": TroopID.ALPHA,
  "bravo": TroopID.BRAVO,
  "jd": TroopID.BRAVO,
  "legal": TroopID.BRAVO,
  "compliance": TroopID.BRAVO,
  "charlie": TroopID.CHARLIE,
  "cto": TroopID.CHARLIE,
  "architecture": TroopID.CHARLIE,
  "perf": TroopID.CHARLIE,
  "lighthouse": TroopID.CHARLIE,
  "delta": TroopID.DELTA,
  "cfo": TroopID.DELTA,
  "revenue": TroopID.DELTA,
  "upsell": TroopID.DELTA,
  "funnel": TroopID.DELTA,
  "profit": TroopID.DELTA,
  "echo": TroopID.ECHO,
  "md": TroopID.ECHO,
  "medical": TroopID.ECHO,
  "verification": TroopID.ECHO,
  "hipaa": TroopID.ECHO,
}


def resolve_troop(prompt: str) -> TroopID | None:
  """Resolve a user prompt to a troop ID via keyword matching.

  Returns None if no troop keyword is detected.
  """
  prompt_lower = prompt.lower()
  for keyword, troop_id in _KEYWORD_MAP.items():
    if keyword in prompt_lower:
      return troop_id
  return None


# ---------------------------------------------------------------------------
# Dispatch result
# ---------------------------------------------------------------------------


@dataclass
class DispatchResult:
  """Result of routing a troop activation through MCP servers."""

  troop: TroopConfig
  mcp_calls: list[dict[str, Any]] = field(default_factory=list)
  jules_tasks: list[dict[str, Any]] = field(default_factory=list)
  pomelli_ab_tests: list[dict[str, Any]] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    """Serialize for logging/beads."""
    return {
      "troop_id": self.troop.troop_id.value,
      "troop_name": self.troop.name,
      "mcp_calls_count": len(self.mcp_calls),
      "jules_tasks_count": len(self.jules_tasks),
      "pomelli_ab_tests_count": len(self.pomelli_ab_tests),
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class CSuiteDispatcher:
  """MCP-first persona routing engine for the C-Suite Swarm.

  Usage::

      dispatcher = CSuiteDispatcher()
      troop_id = resolve_troop("Activate Troop Delta for upsell redesign")
      if troop_id:
          result = dispatcher.prepare_dispatch(troop_id, prompt="...")
          # result.mcp_calls contains the ordered MCP server calls
          # result.jules_tasks contains Jules task queue items
          # result.pomelli_ab_tests contains Pomelli A/B configurations
  """

  def __init__(self, registry: dict[TroopID, TroopConfig] | None = None) -> None:
    self.registry = registry or TROOP_REGISTRY

  def prepare_dispatch(
    self,
    troop_id: TroopID,
    prompt: str,
    *,
    include_jules: bool = True,
    include_pomelli: bool = True,
  ) -> DispatchResult:
    """Prepare MCP dispatch plan for a troop activation.

    This does NOT execute the MCP calls — it produces the routing plan
    that the orchestrator (Antigravity/Jules) will execute.
    """
    troop = self.registry[troop_id]
    result = DispatchResult(troop=troop)

    # Build ordered MCP call plan
    for route in sorted(troop.mcp_routes, key=lambda r: r.priority):
      result.mcp_calls.append(
        {
          "server": route.server,
          "domain": route.domain,
          "priority": route.priority,
          "prompt": prompt,
          "context_scope": list(troop.context_scope),
        }
      )

    # Jules integration — task queue items
    if include_jules:
      result.jules_tasks.append(
        {
          "type": "troop_activation",
          "troop_id": troop_id.value,
          "troop_name": troop.name,
          "prompt": prompt,
          "deliverable": troop.deliverable,
        }
      )

    # Pomelli integration — A/B testing
    if include_pomelli and troop_id in (TroopID.ALPHA, TroopID.DELTA):
      result.pomelli_ab_tests.append(
        {
          "type": "ui_variant",
          "troop_id": troop_id.value,
          "source": "StitchMCP",
          "prompt": prompt,
          "variants_requested": 3,
        }
      )
    elif include_pomelli and troop_id == TroopID.CHARLIE:
      result.pomelli_ab_tests.append(
        {
          "type": "performance_variant",
          "troop_id": troop_id.value,
          "source": "chrome-devtools-mcp",
          "prompt": prompt,
          "metric": "lighthouse_score",
        }
      )

    logger.info(
      "Dispatch prepared: %s → %d MCP calls, %d Jules tasks, %d Pomelli tests",
      troop.name,
      len(result.mcp_calls),
      len(result.jules_tasks),
      len(result.pomelli_ab_tests),
    )
    return result

  def list_troops(self) -> list[dict[str, Any]]:
    """Return all troop configs for status display."""
    return [
      {
        "id": t.troop_id.value,
        "name": t.name,
        "role": t.role,
        "primary_mcp": t.primary_mcp(),
        "milestone": t.milestone_owner,
      }
      for t in self.registry.values()
    ]


# ---------------------------------------------------------------------------
# Milestone execution plans
# ---------------------------------------------------------------------------

MILESTONE_PLANS: dict[str, dict[str, Any]] = {
  "M1_BEACHHEAD": {
    "name": "Beachhead Baseline",
    "mrr_target": 3_000,
    "lead_troop": TroopID.CHARLIE,
    "steps": [
      {"server": "firebase-mcp-server", "action": "deploy kernel_chain/executor.py"},
      {"server": "chrome-devtools-mcp", "action": "lighthouse_audit p99≤90ms"},
      {
        "server": "sequential-thinking",
        "action": "validate Judge#6 at 10M decisions/yr",
      },
      {"integration": "jules", "action": "create monitoring Cloud Task"},
    ],
  },
  "M2_UPSELL": {
    "name": "Upsell Redesign",
    "mrr_target": 15_000,
    "lead_troop": TroopID.DELTA,
    "steps": [
      {
        "server": "firebase-mcp-server",
        "action": "query Firestore user journey analytics",
      },
      {"server": "sequential-thinking", "action": "Monte Carlo conversion simulation"},
      {"server": "StitchMCP", "action": "generate funnel screen variants"},
      {"integration": "pomelli", "action": "A/B test top 3 variants"},
      {"integration": "jules", "action": "deploy winner to production"},
    ],
  },
  "M3_RISK_SIM": {
    "name": "Risk Simulation",
    "mrr_target": 10_000,
    "lead_troop": TroopID.DELTA,
    "support_troop": TroopID.BRAVO,
    "steps": [
      {
        "server": "sequential-thinking",
        "action": "Monte Carlo churn sim (10K iterations)",
      },
      {"server": "google-developer-knowledge", "action": "research retention patterns"},
      {"server": "firebase-mcp-server", "action": "query Firestore churn indicators"},
      {
        "server": "sequential-thinking",
        "action": "CFO + Lawyer vote on countermeasures",
      },
      {"integration": "jules", "action": "deploy retention patches as Cloud Tasks"},
    ],
  },
  "M4_DISTRIBUTION": {
    "name": "Distribution Play",
    "mrr_target": 50_000,
    "lead_troop": TroopID.ALPHA,
    "steps": [
      {
        "server": "sequential-thinking",
        "action": "Strategy Diamond + Blue Ocean analysis",
      },
      {"server": "StitchMCP", "action": "design HeadFade Embed <iframe> Player"},
      {"server": "firebase-mcp-server", "action": "Firebase Data Connect setup"},
      {"server": "chrome-devtools-mcp", "action": "Lighthouse audit on embed widget"},
      {"integration": "pomelli", "action": "A/B test embed placement strategies"},
      {"integration": "jules", "action": "create publisher outreach task queue"},
    ],
  },
}


def get_milestone_plan(milestone_key: str) -> dict[str, Any] | None:
  """Retrieve a milestone execution plan by key."""
  return MILESTONE_PLANS.get(milestone_key)


def save_dispatch_bead(result: DispatchResult, beads_dir: Path) -> Path:
  """Persist a dispatch result to the beads audit trail."""
  import time

  beads_dir.mkdir(parents=True, exist_ok=True)
  bead_path = beads_dir / f"csuite_dispatch_{int(time.time() * 1000)}.json"
  bead_path.write_text(json.dumps(result.to_dict(), indent=2))
  logger.info("Dispatch bead saved: %s", bead_path)
  return bead_path
