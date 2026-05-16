import os
import sys

# Add root to python path
sys.path.append(os.getcwd())

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.dualco.constants import GATE_A_LOGOS
from src.dualco.engine import DualCoEngine, GateName
from src.dualco.models import DualCoGateState, DualCoMetricHistory
from src.dualco.schemas import MetricsInput

# Import ONLY DualCo dependencies to avoid potential import errors in other parts of the app
from src.models.agent_models import Base


def verify():
    print("Initializing In-Memory Database...")
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)

    print(f"Registered tables: {list(Base.metadata.tables.keys())}")

    # Debug Base identity
    print(f"Base ID: {id(Base)}")
    print(f"Model Base ID: {id(DualCoMetricHistory.__base__)}")

    # Explicit creation if needed
    if "dualco_metric_history" not in Base.metadata.tables:
        print("WARNING: Table not in Base.metadata. Creating explicitly via __table__.")
        DualCoMetricHistory.__table__.create(bind=engine)
        DualCoGateState.__table__.create(bind=engine)
    else:
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    dualco_engine = DualCoEngine(db)

    print("Creating Metrics Input...")
    metrics_pass = MetricsInput(
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow(),
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

    print("Running Evaluation Cycle...")
    status = dualco_engine.run_evaluation_cycle(metrics_pass)

    print(f"Gate A Status: {status.gates[GateName.GATE_A.value].status}")
    assert status.gates[GateName.GATE_A.value].status == "PASSED", "Gate A should pass"

    print(f"Gate C Status: {status.gates[GateName.GATE_C.value].status}")
    assert status.gates[GateName.GATE_C.value].status == "FAILED", "Gate C should fail"

    print(f"Kill Switch Active: {status.kill_switch_active}")
    assert not status.kill_switch_active, "Kill Switch should be inactive (0 failures)"

    # Check Persistence
    gate_c = db.query(DualCoGateState).filter_by(gate_name=GateName.GATE_C.value).first()
    print(f"Gate C Consecutive Failures (DB): {gate_c.consecutive_failures}")
    assert gate_c.consecutive_failures == 1

    print("Running Cycle 2 (Trigger Kill Switch)...")
    status_2 = dualco_engine.run_evaluation_cycle(metrics_pass)
    print(f"Kill Switch Active: {status_2.kill_switch_active}")
    assert status_2.kill_switch_active, "Kill Switch should be active (2 failures)"
    assert status_2.overall_status == "RED"

    print("\n✅ VERIFICATION SUCCESSFUL: DualCo Engine logic verified.")


if __name__ == "__main__":
    verify()
