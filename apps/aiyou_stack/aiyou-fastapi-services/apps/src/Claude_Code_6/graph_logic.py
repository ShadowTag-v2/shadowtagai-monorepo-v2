# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

# Placeholder for Gemini integration - assuming standard LangChain or Google Gen AI SDK
# from langchain_google_vertexai import ChatVertexAI


# --- 1. State Definition (The "Dossier") ---
class FinancialDecisionState(TypedDict):
    transaction_id: str
    amount: float
    currency: str
    merchant: str
    risk_score: float | None
    decision: Literal["APPROVED", "DENIED", "MANUAL_REVIEW"] | None
    reasoning: str | None
    path_taken: Literal["FAST_OPA", "SLOW_LLM"] | None


# --- 2. Nodes (The "Agents") ---


def opa_fast_check(state: FinancialDecisionState):
    """Simulates Open Policy Agent (OPA) deterministic rules.
    Doctrine: ATP 3-60 (Targeting - Fast Fires)
    """
    print(f"⚡ [OPA] Checking transaction: ${state['amount']} to {state['merchant']}")

    # Rule 1: Auto-Deny High Value without KYC (Simulated)
    if state["amount"] > 10000:
        return {
            "decision": "DENIED",
            "reasoning": "Amount exceeds auto-approval limit ($10k)",
            "path_taken": "FAST_OPA",
        }

    # Rule 2: Auto-Approve Micro-transactions
    if state["amount"] < 50:
        return {
            "decision": "APPROVED",
            "reasoning": "Micro-transaction within safe limits",
            "path_taken": "FAST_OPA",
        }

    # Otherwise: Uncertain, escalate to Judge#6
    return {"decision": None}  # Signals need for escalation


def Cor_Claude_Code_6_reasoning(state: FinancialDecisionState):
    """The LLM-as-a-Judge for complex financial reasoning.
    Doctrine: FM 6-0 (Mission Command - Commander's Intent)
    """
    print("🧠 [Judge#6] Deliberating on complex case...")

    # TODO: Replace with actual Gemini call
    # model = ChatVertexAI(model="gemini-3.1-flash-lite-preview")
    # response = model.invoke(...)

    # Mock logic for "Gucci" demo
    risk_score = 0.45  # Calculated from "GraphRAG" context

    if state["merchant"] == "Unknown Vendor":
        decision = "DENIED"
        reasoning = "Vendor trust score too low based on GraphRAG analysis."
    else:
        decision = "APPROVED"
        reasoning = "Transaction fits user's spending pattern (Mem0 verified)."

    return {
        "decision": decision,
        "reasoning": reasoning,
        "risk_score": risk_score,
        "path_taken": "SLOW_LLM",
    }


def audit_logger(state: FinancialDecisionState):
    """Logs decision to Sovereign Memory (Mem0 + GraphRAG).
    Doctrine: ATP 2-01.3 (Intelligence)
    """
    print(f"📝 [Audit] Logging decision: {state['decision']} via {state['path_taken']}")
    # TODO: Integrate Mem0.add() here
    return state


# --- 3. Graph Construction (The "Kill Chain") ---


def route_decision(state: FinancialDecisionState):
    """Determines the next step based on OPA result."""
    if state["decision"] is not None:
        return "audit"
    return "Cor_Claude_Code_6"


workflow = StateGraph(FinancialDecisionState)

# Add Nodes
workflow.add_node("opa", opa_fast_check)
workflow.add_node("Cor_Claude_Code_6", Cor_Claude_Code_6_reasoning)
workflow.add_node("audit", audit_logger)

# Set Entry Point
workflow.set_entry_point("opa")

# Add Edges
workflow.add_conditional_edges(
    "opa", route_decision, {"audit": "audit", "Cor_Claude_Code_6": "Cor_Claude_Code_6"}
)
workflow.add_edge("Cor_Claude_Code_6", "audit")
workflow.add_edge("audit", END)

# Compile
app = workflow.compile()

# --- 4. Execution Demo ---
if __name__ == "__main__":
    # Test Case 1: Fast Path (Micro-transaction)
    print("\n--- TEST CASE 1: COFFEE ---")
    inputs = {
        "transaction_id": "tx_1",
        "amount": 4.50,
        "currency": "USD",
        "merchant": "Starbucks",
    }
    app.invoke(inputs)

    # Test Case 2: Slow Path (Mid-size transaction)
    print("\n--- TEST CASE 2: NEW LAPTOP ---")
    inputs = {
        "transaction_id": "tx_2",
        "amount": 2500.00,
        "currency": "USD",
        "merchant": "Best Buy",
    }
    app.invoke(inputs)
