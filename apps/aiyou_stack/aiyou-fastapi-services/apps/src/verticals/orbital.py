# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.


class AiUOrbital:
    """Vertical 5: AiU Orbital (Connectivity)
    ARR 2030: $3.5B
    Moat: Global LEO ground station mesh + Aircraft Relay.
    """

    def get_metrics(self):
        return {
            "arr_projection_2030": 3_500_000_000,
            "ebitda_margin": 0.40,
            "valuation_conservative": 8_400_000_000,  # 6x
            "valuation_optimistic": 15_400_000_000,  # 11x
            "coverage_global": True,
            "relay_altitude_ft": 35000,
        }
