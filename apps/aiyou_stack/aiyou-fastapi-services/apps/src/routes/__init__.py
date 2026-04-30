"""API routes for the agent system."""

from .agent_routes import router as agent_router
from .growth_routes import router as growth_router

__all__ = ["agent_router", "growth_router"]
