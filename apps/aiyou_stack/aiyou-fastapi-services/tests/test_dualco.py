from datetime import UTC, datetime

import pytest
from src.dualco.models import Base, DualCoGateState

from src.database import SessionLocal
from src.database import engine as db_engine
from src.dualco.constants import GATE_A_LOGOS, GateName
from src.dualco.engine import DualCoEngine
from src.dualco.schemas import MetricsInput


@pytest.fixture(scope="module")
def db_session():
    # Create tables
    Base.metadata.create_all(bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()
    # Drop tables
    Base.metadata.drop_all(bind=db_engine)


def test_dualco_engine_flow(db_session):
    engine = DualCoEngine(db_session)

    # 1. Metric Input that passes Gate A
    metrics_pass = MetricsInput(
        period_start=datetime.now(UTC),
        period_end=datetime.now(UTC),
        # Gate A Passing
        as_paying_logos=GATE_A_LOGOS + 10,
        as_detection_uplift=0.35,
        as_grr=0.95,
        as_nrr=1.25,
        as_deploy_time_hours=20,
        as_burn_multiple=1.5,
        # Gate B/C (Partial/Dummy - forcing C fail)
        as_cac_payback_ent=12,
        as_cac_payback_smb=6,
        pnkln_throughput_daily=1000,  # Fail C (Target 10M)
        pnkln_latency_p95_ms=50,
        pnkln_error_rate=0.001,
        pnkln_design_partners=0,
        pnkln_signed_mou=False,
        pnkln_contracted_arr=0,
        pnkln_burn_multiple=1.0,
        pnkln_gross_margin=0.5,
        rule_of_40=30,
        uptime_pct=99.9,
        p0_mttr_minutes=10,
        as_gross_margin=0.75,
        as_arr=1000000,
    )

    status = engine.run_evaluation_cycle(metrics_pass)

    assert status.gates[GateName.GATE_A.value].status == "PASSED"
    assert status.gates[GateName.GATE_C.value].status == "FAILED"
    assert not status.kill_switch_active

    # 2. Check Persistence
    gate_a = db_session.query(DualCoGateState).filter_by(gate_name=GateName.GATE_A.value).first()
    assert gate_a.status == "PASSED"
    assert gate_a.consecutive_failures == 0

    gate_c = db_session.query(DualCoGateState).filter_by(gate_name=GateName.GATE_C.value).first()
    assert gate_c.status == "FAILED"
    assert gate_c.consecutive_failures == 1

    # 3. Fail Gate C again (Trigger Kill Switch)
    status_2 = engine.run_evaluation_cycle(metrics_pass)
    # Consecutive failures limit is 2
    assert status_2.gates[GateName.GATE_C.value].consecutive_failures == 2
    assert status_2.kill_switch_active
    assert status_2.overall_status == "RED"
