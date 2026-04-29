# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
from enum import Enum

logger = logging.getLogger("Cor.Claude_Code_6-CSRMC")


class Phase(Enum):
    DESIGN = 1
    BUILD_IOC = 2
    TEST_FOC = 3
    ONBOARD = 4
    OPERATIONS = 5


class SurvivabilityState(Enum):
    GREEN = "SECURE"
    YELLOW = "VULNERABLE_MONITORED"
    RED = "COMPROMISED"


class MissionCriticality(Enum):
    ROUTINE = 1
    TACTICAL = 2
    COMBAT = 3


class CSRMCEngine:
    def __init__(self):
        self.name = "CSRMC Defender"
        self.cssp_signoff = False

    def validate_phase_transition(self, current_phase: Phase, telemetry: dict) -> bool:
        if current_phase == Phase.BUILD_IOC and not telemetry.get("critical_controls"):
            return False
        return not (current_phase == Phase.ONBOARD and not self.cssp_signoff)

    def evaluate_survivability(self, system_id: str, telemetry: dict) -> SurvivabilityState:
        if telemetry.get("active_threats", 0) > 0:
            return SurvivabilityState.RED
        if telemetry.get("vuln_score", 0) > 7.0:
            return SurvivabilityState.YELLOW
        return SurvivabilityState.GREEN

    def execute_operational_logic(
        self,
        system_id: str,
        survivability: SurvivabilityState,
        criticality: MissionCriticality,
    ) -> str:
        if survivability == SurvivabilityState.GREEN:
            return "MAINTAIN_ATO"
        if survivability == SurvivabilityState.YELLOW:
            return "EXECUTE_AUTO_PATCH"
        if survivability == SurvivabilityState.RED:
            return (
                "ISOLATE_ENCLAVE_AND_FIGHT"
                if criticality == MissionCriticality.COMBAT
                else "REVOKE_ATO_IMMEDIATE_DISCONNECT"
            )
        return "UNKNOWN"
