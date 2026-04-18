"""DualCo Strategy Engine Core Logic"""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from .constants import (
    CONSECUTIVE_FAILURES_LIMIT,
    GATE_A_BURN_MULTIPLE,
    GATE_A_DEPLOY_TIME_HOURS,
    GATE_A_DETECTION_UPLIFT,
    GATE_A_GRR,
    GATE_A_LOGOS,
    GATE_A_NRR,
    GATE_B_CAC_PAYBACK_ENT,
    GATE_B_CAC_PAYBACK_SMB,
    GATE_C_DESIGN_PARTNERS,
    GATE_C_ERROR_RATE,
    GATE_C_LATENCY_P95_MS,
    GATE_C_THROUGHPUT_DAILY,
    GateName,
)
from .models import DualCoGateState, DualCoMetricHistory
from .schemas import DualCoStatus, GateStatus, MetricEvaluation, MetricsInput


class DualCoEngine:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_gate_state(self, gate_name: GateName) -> DualCoGateState:
        state = (
            self.db.query(DualCoGateState)
            .filter(DualCoGateState.gate_name == gate_name.value)
            .first()
        )
        if not state:
            state = DualCoGateState(
                gate_name=gate_name.value,
                status="PENDING",
                consecutive_failures=0,
            )
            self.db.add(state)
            self.db.flush()
        return state

    def evaluate_gate_a(self, metrics: MetricsInput) -> GateStatus:
        """Evaluate Gate A - ActiveShield PMF"""
        evals = [
            MetricEvaluation(
                name="Paying Logos",
                current_value=metrics.as_paying_logos,
                target_value=GATE_A_LOGOS,
                passed=metrics.as_paying_logos >= GATE_A_LOGOS,
            ),
            MetricEvaluation(
                name="Detection Uplift",
                current_value=metrics.as_detection_uplift,
                target_value=GATE_A_DETECTION_UPLIFT,
                passed=metrics.as_detection_uplift >= GATE_A_DETECTION_UPLIFT,
            ),
            MetricEvaluation(
                name="GRR",
                current_value=metrics.as_grr,
                target_value=GATE_A_GRR,
                passed=metrics.as_grr >= GATE_A_GRR,
            ),
            MetricEvaluation(
                name="NRR",
                current_value=metrics.as_nrr,
                target_value=GATE_A_NRR,
                passed=metrics.as_nrr >= GATE_A_NRR,
            ),
            MetricEvaluation(
                name="Deploy Time (Hours)",
                current_value=metrics.as_deploy_time_hours,
                target_value=GATE_A_DEPLOY_TIME_HOURS,
                passed=metrics.as_deploy_time_hours <= GATE_A_DEPLOY_TIME_HOURS,
            ),
            MetricEvaluation(
                name="Burn Multiple",
                current_value=metrics.as_burn_multiple,
                target_value=GATE_A_BURN_MULTIPLE,
                passed=metrics.as_burn_multiple <= GATE_A_BURN_MULTIPLE,
            ),
        ]

        all_passed = all(e.passed for e in evals)
        status = "PASSED" if all_passed else "FAILED"

        return GateStatus(
            gate_name=GateName.GATE_A,
            status=status,
            last_evaluated=datetime.utcnow(),
            metrics=evals,
            consecutive_failures=0,  # To be updated from DB state
        )

    def evaluate_gate_b(self, metrics: MetricsInput) -> GateStatus:
        """Evaluate Gate B - Enterprise Wedge"""
        evals = [
            MetricEvaluation(
                name="CAC Payback ENT",
                current_value=metrics.as_cac_payback_ent,
                target_value=GATE_B_CAC_PAYBACK_ENT,
                passed=metrics.as_cac_payback_ent <= GATE_B_CAC_PAYBACK_ENT,
            ),
            MetricEvaluation(
                name="CAC Payback SMB",
                current_value=metrics.as_cac_payback_smb,
                target_value=GATE_B_CAC_PAYBACK_SMB,
                passed=metrics.as_cac_payback_smb <= GATE_B_CAC_PAYBACK_SMB,
            ),
        ]

        all_passed = all(e.passed for e in evals)
        status = "PASSED" if all_passed else "FAILED"

        return GateStatus(
            gate_name=GateName.GATE_B,
            status=status,
            last_evaluated=datetime.utcnow(),
            metrics=evals,
            consecutive_failures=0,
        )

    def evaluate_gate_c(self, metrics: MetricsInput) -> GateStatus:
        """Evaluate Gate C - PNKLN Strategic Validation"""
        evals = [
            MetricEvaluation(
                name="Throughput Daily",
                current_value=metrics.pnkln_throughput_daily,
                target_value=GATE_C_THROUGHPUT_DAILY,
                passed=metrics.pnkln_throughput_daily >= GATE_C_THROUGHPUT_DAILY,
            ),
            MetricEvaluation(
                name="Latency p95 (ms)",
                current_value=metrics.pnkln_latency_p95_ms,
                target_value=GATE_C_LATENCY_P95_MS,
                passed=metrics.pnkln_latency_p95_ms <= GATE_C_LATENCY_P95_MS,
            ),
            MetricEvaluation(
                name="Error Rate",
                current_value=metrics.pnkln_error_rate,
                target_value=GATE_C_ERROR_RATE,
                passed=metrics.pnkln_error_rate <= GATE_C_ERROR_RATE,
            ),
            MetricEvaluation(
                name="Design Partners",
                current_value=metrics.pnkln_design_partners,
                target_value=GATE_C_DESIGN_PARTNERS,
                passed=metrics.pnkln_design_partners >= GATE_C_DESIGN_PARTNERS,
            ),
            MetricEvaluation(
                name="MOU Signed",
                current_value=1.0 if metrics.pnkln_signed_mou else 0.0,
                target_value=1.0,
                passed=metrics.pnkln_signed_mou,
            ),
        ]

        all_passed = all(e.passed for e in evals)
        status = "PASSED" if all_passed else "FAILED"

        return GateStatus(
            gate_name=GateName.GATE_C,
            status=status,
            last_evaluated=datetime.utcnow(),
            metrics=evals,
            consecutive_failures=0,
        )

    def run_evaluation_cycle(self, metrics: MetricsInput) -> DualCoStatus:
        """Main engine execution:
        1. Access persistence (Gate States).
        2. Evaluate all Gates against MetricsInput.
        3. Update Persistence (increment/reset failure counts).
        4. Determine Kill Switch State.
        5. Persist Metric History.
        """
        # 1. Persist History
        history = DualCoMetricHistory(
            period_start=metrics.period_start,
            period_end=metrics.period_end,
            metrics_data=json.loads(metrics.json()),
            gate_status_snapshot={},
        )
        self.db.add(history)
        self.db.commit()  # Commit to get ID for linkage

        # 2. Evaluate
        gates_results: dict[str, GateStatus] = {}
        kill_switch_active = False

        # Gate A
        gate_a_state = self._get_or_create_gate_state(GateName.GATE_A)
        gate_a_result = self.evaluate_gate_a(metrics)
        self._update_gate_state(gate_a_state, gate_a_result, history.id)
        gates_results[GateName.GATE_A.value] = gate_a_result

        # Gate B
        gate_b_state = self._get_or_create_gate_state(GateName.GATE_B)
        gate_b_result = self.evaluate_gate_b(metrics)
        self._update_gate_state(gate_b_state, gate_b_result, history.id)
        gates_results[GateName.GATE_B.value] = gate_b_result

        # Gate C
        gate_c_state = self._get_or_create_gate_state(GateName.GATE_C)
        gate_c_result = self.evaluate_gate_c(metrics)
        self._update_gate_state(gate_c_state, gate_c_result, history.id)
        gates_results[GateName.GATE_C.value] = gate_c_result

        # 3. Kill Switch Logic
        for state in [gate_a_state, gate_b_state, gate_c_state]:
            if state.consecutive_failures >= CONSECUTIVE_FAILURES_LIMIT:
                kill_switch_active = True

        # 4. Final Updates
        history.gate_status_snapshot = {k: json.loads(v.json()) for k, v in gates_results.items()}
        self.db.commit()

        return DualCoStatus(
            overall_status="RED" if kill_switch_active else "GREEN",
            gates=gates_results,
            kill_switch_active=kill_switch_active,
            active_shield_burn_multiple=metrics.as_burn_multiple,
            pnkln_burn_multiple=metrics.pnkln_burn_multiple,
            last_updated=datetime.utcnow(),
        )

    def _update_gate_state(self, state: DualCoGateState, result: GateStatus, history_id: str):
        state.last_evaluated_at = result.last_evaluated
        state.last_metric_snapshot_id = history_id

        if result.status == "FAILED":
            state.status = "FAILED"
            state.consecutive_failures += 1
        elif result.status == "PASSED":
            state.status = "PASSED"
            state.consecutive_failures = 0

        result.consecutive_failures = state.consecutive_failures
