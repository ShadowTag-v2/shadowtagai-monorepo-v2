"""
GamePort API Routes.

Handles game sessions, matchmaking, and SDK integration.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.gameport import Game, GameSession
from ..models.user import User

router = APIRouter(prefix="/gameport", tags=["gameport"])


class GameSessionCreate(BaseModel):
    game_id: str
    gpu_region: str | None = "us-east-1"


class GameSessionResponse(BaseModel):
    session_id: str
    game_id: str
    status: str
    connect_url: str | None
    created_at: datetime


@router.get("/games", response_model=list[dict])
async def list_games(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List available games."""
    games = db.query(Game).filter(Game.is_active).offset(skip).limit(limit).all()
    return [{"id": g.id, "title": g.title, "genre": g.genre} for g in games]


@router.post("/sessions", response_model=GameSessionResponse)
async def create_session(
    session_in: GameSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new cloud gaming session."""
    game = db.query(Game).filter(Game.id == session_in.game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # In production: Call GPUOrchestrator here
    # node_id = orchestrator.request_compute("gaming", session_in.gpu_region)

    session = GameSession(
        game_id=game.id,
        user_id=current_user.id,
        gpu_node_id="mock-node-1",  # Mocked
        started_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return GameSessionResponse(
        session_id=session.id,
        game_id=session.game_id,
        status="active",
        connect_url=f"wss://stream.gameport.ai/connect/{session.id}",
        created_at=session.started_at,
    )
