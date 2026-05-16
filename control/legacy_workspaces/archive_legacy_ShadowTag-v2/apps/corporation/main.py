# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys

# Ensure libs is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from libs.treasury.ledger import Ledger
from libs.treasury.budget import BudgetEnforcer

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
        "treasury": {
            "balance": ledger.get_balance(),
            "history_count": len(ledger.get_history()),
        },
        "governance": {
            "status": "active",
            "alert_level": "green",  # Mock signal
        },
        "operations": {
            "active_agents": 0  # Mock signal
        },
    }


@app.post("/treasury/request_funds")
def request_funds(req: TransactionRequest):
    """Agents request funds for operations."""
    approved = budget.approve_transaction(req.amount, req.requester, req.category, req.reason)

    if approved:
        return {"status": "approved", "granted": req.amount}
    else:
        raise HTTPException(status_code=402, detail="Insufficient funds or budget limit exceeded")
