# Copyright 2026 ShadowTag AI. All rights reserved.
"""JP 3-33 Joint Task Force Staff Topology.

Maps the 8-Agent Swarm into a formal J-Staff organization per JP 3-33.
Each agent maps to a Command function with doctrinal authority.
"""

from dataclasses import dataclass
import logging

logger = logging.getLogger("JTF-Headquarters-JP3-33")


@dataclass(frozen=True)
class JStaffDesignation:
    """A single J-Staff designation mapping agent role to doctrine."""

    j_code: str
    agent_role: str
    doctrine_mandate: str


class JTFHeadquarters:
    """The 8-Agent Swarm reorganized into a JP 3-33 J-Staff.

    References:
        - JP 3-33: Joint Task Force Headquarters
        - ADP 5-0: The Operations Process
        - FM 3-0: Operations
    """

    STAFF: dict[str, JStaffDesignation] = {
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
        """Look up J-Staff designation by code."""
        return JTFHeadquarters.STAFF[j_code]

    @staticmethod
    def list_staff() -> list[JStaffDesignation]:
        """Return all J-Staff designations."""
        return list(JTFHeadquarters.STAFF.values())
