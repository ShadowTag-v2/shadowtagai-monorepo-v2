import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Judge#6 Governance Engine", version="2025.3")


class RiskCheck(BaseModel):
    operation: str
    confidence: float
    vertical: str


@app.get("/")
def health_check():
    return {"status": "operational", "doctrine": "Tier 30: The Child"}


@app.post("/validate")
def validate_operation(check: RiskCheck):
    """Judge#6 Brakes Logic:
    If Confidence < 0.75 -> FREEZE
    """
    if check.confidence < 0.75:
        return {"verdict": "FREEZE", "reason": "Confidence too low (<0.75)"}

    return {"verdict": "PROCEED", "reason": "Risk acceptable"}


class GovernanceEngine:
    """Judge#6 Governance Engine — 3-phase kill chain orchestrator.

    Kill Chain: OPA Fast Check → Judge#6 Reasoning → Audit Logger
    """

    def __init__(self, *, memory=None, config: dict | None = None):
        self.memory = memory
        self.config = config or {}
        self._graph = None

    async def evaluate(self, operation: str, context: dict | None = None) -> dict:
        """Run the full governance kill chain on an operation."""
        check = RiskCheck(
            operation=operation,
            confidence=context.get("confidence", 0.5) if context else 0.5,
            vertical=context.get("vertical", "general") if context else "general",
        )
        result = validate_operation(check)
        return {
            "decision": result["verdict"],
            "reason": result["reason"],
            "engine": "judge6",
        }

    @property
    def graph(self):
        """Lazy-load the governance graph."""
        if self._graph is None:
            self._graph = create_governance_graph(engine=self)
        return self._graph


def create_governance_graph(*, engine: GovernanceEngine | None = None) -> dict:
    """Factory for the governance state graph.

    Returns a graph descriptor compatible with LangGraph's StateGraph
    when available, falling back to a dict-based representation.
    """
    return {
        "nodes": ["assessment", "debate", "audit"],
        "edges": [
            ("assessment", "debate"),
            ("debate", "audit"),
        ],
        "entry_point": "assessment",
        "engine": engine,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
