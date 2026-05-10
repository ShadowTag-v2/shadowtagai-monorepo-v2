import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Ensure libs is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from libs.treasury.budget import BudgetEnforcer
from libs.treasury.ledger import Ledger

app = FastAPI(title="ShadowTag Corporation", version="1.0.0")

# Initialize Singletons
ledger = Ledger()
budget = BudgetEnforcer(ledger)


class TransactionRequest(BaseModel):
    requester: str
    amount: float
    category: str
    reason: str


@app.get("/")
def health_check():
    return {"status": "operational", "service": "Corporation HQ"}


@app.get("/boardroom")
def boardroom_status():
    """Returns the high-level status of the Sovereign Corporation."""
    return {
        "treasury": {"balance": ledger.get_balance(), "history_count": len(ledger.get_history())},
        "governance": {
            "status": "active",
            "alert_level": "green",  # Mock signal
        },
        "operations": {
            "active_agents": 0,  # Mock signal
        },
    }


@app.post("/treasury/request_funds")
def request_funds(req: TransactionRequest):
    """Agents request funds for operations."""
    approved = budget.approve_transaction(req.amount, req.requester, req.category, req.reason)

    if approved:
        return {"status": "approved", "granted": req.amount}
    raise HTTPException(status_code=402, detail="Insufficient funds or budget limit exceeded")
