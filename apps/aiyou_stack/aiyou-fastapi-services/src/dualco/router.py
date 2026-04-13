"""
DualCo REST API Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db

from .engine import DualCoEngine
from .schemas import BoardResolution, DecisionLogCreate, DecisionLogRead, DualCoStatus, MetricsInput
from .service import DualCoService

router = APIRouter(prefix="/dualco", tags=["DualCo Strategy"])


@router.post("/metrics", response_model=DualCoStatus)
def ingest_metrics(metrics: MetricsInput, db: Session = Depends(get_db)):
    engine = DualCoEngine(db)
    return engine.ingest_metrics(metrics)


@router.get("/board-packet", response_model=BoardResolution)
def get_board_packet(db: Session = Depends(get_db)):
    engine = DualCoEngine(db)
    return engine.generate_board_resolution()


@router.post("/decisions", response_model=DecisionLogRead)
def log_decision(decision: DecisionLogCreate, db: Session = Depends(get_db)):
    return DualCoService.log_decision(db, decision.dict())


@router.get("/decisions", response_model=list[DecisionLogRead])
def get_decisions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return DualCoService.list_decisions(db, skip, limit)
