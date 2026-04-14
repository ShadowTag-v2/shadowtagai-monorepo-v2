"""DualCo Strategy Constants (Bourne/160)
"""

from enum import StrEnum


class GateName(StrEnum):
    GATE_A = "Gate A - ActiveShield PMF"
    GATE_B = "Gate B - Enterprise Wedge"
    GATE_C = "Gate C - PNKLN Strategic Validation"
    GATE_D = "Gate D - Financing Hygiene"


# Gate A Thresholds
GATE_A_LOGOS = 250
GATE_A_DETECTION_UPLIFT = 0.30  # 30%
GATE_A_GRR = 0.90  # 90%
GATE_A_NRR = 1.20  # 120%
GATE_A_DEPLOY_TIME_HOURS = 24  # 1 day
GATE_A_BURN_MULTIPLE = 2.0

# Gate B Thresholds
GATE_B_REF_WINS = 10
GATE_B_REF_SEATS = 2000
GATE_B_INTEGRATIONS_LIVE = 3
GATE_B_PLAYBOOKS_AUTO = 2
GATE_B_SALES_RAMP_AES = 8
GATE_B_CAC_PAYBACK_ENT = 12
GATE_B_CAC_PAYBACK_SMB = 6

# Gate C Thresholds
GATE_C_THROUGHPUT_DAILY = 10_000_000
GATE_C_LATENCY_P95_MS = 20
GATE_C_ERROR_RATE = 1e-6
GATE_C_DESIGN_PARTNERS = 5

# Financial Bounds
RULE_OF_40_TARGET = 40.0
AS_GM_TARGET = 0.75
PNKLN_GM_TARGET = 0.78
UPTIME_SLA = 99.9
P0_MTTR_MINUTES = 60

# Kill Switch Defaults
CONSECUTIVE_FAILURES_LIMIT = 2
