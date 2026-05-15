"""JP 3-33 Joint Task Force Staff Topology.

The 8-Agent Swarm is NOT a flat circle. It is a Joint Task Force (JTF)
Headquarters organized per JP 3-33: Joint Task Force Headquarters.

Every agent maps to a Command function. Every handoff is governed
by Judge 6.1 Zero Trust. Every operation follows ADP 5-0.

J-Staff Mapping:
    J-1 (Vault)         → Custodian, Personnel, FedRAMP Deployments
    J-2 (Jetski/Lit)    → Intelligence Preparation of the Battlefield (ATP 2-01.3)
    J-3 (Builder/Tester) → Decisive Operations & Execution (FM 3-0)
    J-4 (Corrector)     → Logistics, Repair, Rejection Loop Sustainment
    J-5 (Architect)     → Plans & Military Decision Making Process (ADP 5-0)
    J-6 (Judge 6.1)     → Command, Control, Cyber, ZTA cATO (CSRMC/NIST)
    J-9 (Splinter)      → Civil-Military & Information Operations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import ClassVar

logger = logging.getLogger("JTF-Headquarters-JP3-33")


@dataclass(frozen=True)
class JStaffDesignation:
  """A single J-Staff billet in the Joint Task Force."""

  j_code: str
  agent_role: str
  doctrine_mandate: str


class JTFHeadquarters:
  """The 8-Agent Swarm reorganized into a JP 3-33 J-Staff.

  This is not a flat swarm. This is a military headquarters with
  defined command relationships, authorities, and responsibilities.
  """

  STAFF: ClassVar[dict[str, JStaffDesignation]] = {
    "J1": JStaffDesignation(
      "J-1",
      "Vault",
      "Custodian, Personnel, & FedRAMP Deployments",
    ),
    "J2": JStaffDesignation(
      "J-2",
      "Jetski & Literature",
      "Intelligence Preparation of the Battlefield (ATP 2-01.3)",
    ),
    "J3": JStaffDesignation(
      "J-3",
      "Builder & Tester",
      "Decisive Operations & Execution (FM 3-0)",
    ),
    "J4": JStaffDesignation(
      "J-4",
      "Corrector",
      "Logistics, Repair, & Rejection Loop Sustainment",
    ),
    "J5": JStaffDesignation(
      "J-5",
      "Architect",
      "Plans & Military Decision Making Process (ADP 5-0)",
    ),
    "J6": JStaffDesignation(
      "J-6",
      "Judge 6.1",
      "Command, Control, Cyber, & ZTA Continuous ATO (CSRMC/NIST)",
    ),
    "J9": JStaffDesignation(
      "J-9",
      "Splinter Engine",
      "Civil-Military & Information Operations",
    ),
  }

  @staticmethod
  def get_routing_authority(j_code: str) -> JStaffDesignation:
    """Resolve the J-Staff billet for a given code.

    Args:
        j_code: The J-code (e.g., "J1", "J6").

    Returns:
        The JStaffDesignation for the requested billet.

    Raises:
        KeyError: If the J-code is not recognized.
    """
    if j_code not in JTFHeadquarters.STAFF:
      logger.critical("Unknown J-code: %s. JP 3-33 violation.", j_code)
      raise KeyError(f"Unknown J-Staff code: {j_code}")
    return JTFHeadquarters.STAFF[j_code]

  @staticmethod
  def validate_handoff(source: str, destination: str) -> bool:
    """Validate that a J-Staff handoff is doctrinally authorized.

    Args:
        source: Source J-code (e.g., "J5").
        destination: Destination J-code (e.g., "J3").

    Returns:
        True if the handoff is authorized.
    """
    # Authorized handoff chains per JP 3-33
    authorized_chains: dict[str, list[str]] = {
      "J2": ["J5"],  # Intel → Plans
      "J5": ["J3", "J6"],  # Plans → Ops or Cyber
      "J3": ["J4", "J6"],  # Ops → Logistics or Cyber
      "J4": ["J3"],  # Logistics → Ops (retry)
      "J6": ["J1", "J9"],  # Cyber → Vault or Info Ops
      "J1": [],  # Vault = terminal (deploy)
      "J9": [],  # Info Ops = terminal (syndicate)
    }

    allowed = authorized_chains.get(source, [])
    if destination not in allowed:
      logger.warning(
        "UNAUTHORIZED HANDOFF: %s → %s. JP 3-33 violation.", source, destination
      )
      return False

    logger.info("JP 3-33 handoff authorized: %s → %s", source, destination)
    return True
