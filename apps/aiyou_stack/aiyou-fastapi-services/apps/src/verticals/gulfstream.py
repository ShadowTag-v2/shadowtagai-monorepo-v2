# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class GulfstreamOffshore:
    """Vertical 1: Gulfstream Offshore Energy
    ARR 2030: $1.75B
    Moat: $17/MWh cost advantage + CAISO timing.
    """

    def __init__(self):
        self.capacity_gw = 1.0
        self.deployment_cost_mwh = 17.0
        self.industry_avg_cost = 70.0  # $60-80 range

    def get_metrics(self):
        return {
            "arr_projection_2030": 1_750_000_000,
            "ebitda_margin": 0.50,  # 50%
            "valuation_conservative": 7_000_000_000,  # 8x
            "valuation_optimistic": 13_125_000_000,  # 15x
            "active_platforms": 10,
            "cost_advantage_percent": 1.0 - (self.deployment_cost_mwh / self.industry_avg_cost),
        }
