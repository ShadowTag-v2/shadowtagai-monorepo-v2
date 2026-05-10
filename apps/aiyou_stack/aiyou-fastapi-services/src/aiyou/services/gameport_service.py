"""GamePort service layer.

Extracts all database operations from gameport routes
into a proper service/repository pattern.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from ..models.gameport import Game, GameSession
from ..models.user import User


class GameportService:
    """Service layer for gameport operations."""

    @staticmethod
    def list_games(db: Session, skip: int = 0, limit: int = 100) -> list[dict]:
        """List active games."""
        games = db.query(Game).filter(Game.is_active).offset(skip).limit(limit).all()
        return [{"id": g.id, "title": g.title, "genre": g.genre} for g in games]

    @staticmethod
    def get_game(db: Session, game_id: str) -> Game | None:
        """Get a game by ID."""
        return db.query(Game).filter(Game.id == game_id).first()

    @staticmethod
    def create_session(
        db: Session,
        game: Game,
        user: User,
        gpu_region: str | None = "us-east-1",
    ) -> GameSession:
        """Create a new cloud gaming session."""
        session = GameSession(
            game_id=game.id,
            user_id=user.id,
            gpu_node_id=f"mock-node-{gpu_region or 'us-east-1'}",
            started_at=datetime.utcnow(),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
