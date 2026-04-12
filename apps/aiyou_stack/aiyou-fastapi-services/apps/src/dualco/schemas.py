"""
DualCo Pydantic Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .constants import GateName


class MetricEvaluation(BaseModel):
    name: str
    current_value: float
    target_value: float
    passed: bool
    notes: str | None = None


class GateStatus(BaseModel):
    gate_name: GateName
    status: str = Field(..., description="PENDING, PASSED, FAILED")
    last_evaluated: datetime
    metrics: list[MetricEvaluation]
    consecutive_failures: int = 0


class DualCoStatus(BaseModel):
    overall_status: str  # GREEN, YELLOW, RED (Kill Switch)
    gates: dict[str, GateStatus]
    kill_switch_active: bool = False
    active_shield_burn_multiple: float
    pnkln_burn_multiple: float
    last_updated: datetime


class DecisionLogCreate(BaseModel):
    context: str
    options_considered: list[str]
    chosen_option: str
    why_first_principles: str
    metrics_to_watch: list[str]
    kill_criteria: str
    owner: str


class DecisionLogRead(DecisionLogCreate):
    id: str
    decision_date: datetime
    review_cadence: str = "Monthly"


class MetricsInput(BaseModel):
    """Monthly Metrics Input"""

    period_start: datetime
    period_end: datetime

    # ActiveShield
    as_paying_logos: int
    as_detection_uplift: float
    as_grr: float
    as_nrr: float
    as_deploy_time_hours: float
    as_burn_multiple: float
    as_gross_margin: float
    as_arr: float
    as_cac_payback_ent: float
    as_cac_payback_smb: float

    # PNKLN
    pnkln_throughput_daily: int
    pnkln_latency_p95_ms: float
    pnkln_error_rate: float
    pnkln_design_partners: int
    pnkln_signed_mou: bool
    pnkln_contracted_arr: float
    pnkln_burn_multiple: float
    pnkln_gross_margin: float

    # Shared
    rule_of_40: float
    uptime_pct: float
    p0_mttr_minutes: float


class BoardResolution(BaseModel):
    resolution_text: str
    generated_at: datetime
    gate_status_summary: str
