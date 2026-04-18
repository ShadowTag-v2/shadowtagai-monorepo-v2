"""Antigravity Orchestrator (The Nervous System)
Implements the "Courtroom" and "Explain-to-Peer" patterns via LangGraph.
"""

import logging
import operator
from typing import Annotated, Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.llm_clients import get_cheap_llm, get_strong_llm
from app.risk_router import calculate_risk
from app.schemas import RiskLevel, TaskRequest, TaskType
from app.tools import run_bugbot, run_policy_gate

logger = logging.getLogger(__name__)


# --- State Definition (The World Model) ---
class AgentState(TypedDict):
    # Inputs
    task: TaskRequest

    # Internal State
    risk_level: RiskLevel
    draft: str | None
    critique: str | None
    policy_issues: list[str]
    messages: Annotated[list[Any], operator.add]

    # Outputs
    final_output: str | None
    cost_usd: float


# --- Nodes (The Agents) ---


def node_router(state: AgentState) -> dict:
    """Judge #6 Router: Determines Risk Level"""
    risk = calculate_risk(state["task"])
    logger.info(f"Router assigned risk level: {risk}")
    return {"risk_level": risk}


def node_drafter(state: AgentState) -> dict:
    """Tier 0 Agent (Cheap LLM): Drafts initial solution"""
    llm = get_cheap_llm(temperature=0.3)
    response = llm.invoke(
        [
            SystemMessage(content="You are a precise coding assistant. Draft a solution."),
            HumanMessage(content=state["task"].description),
        ],
    )
    return {"draft": response.content}


def node_critic(state: AgentState) -> dict:
    """Tier 1 Agent (Strong LLM): E2P Critique"""
    llm = get_strong_llm(temperature=0.1)
    response = llm.invoke(
        [
            SystemMessage(
                content="You are a hostile critic. Find security flaws and logic errors.",
            ),
            HumanMessage(content=f"Review this draft:\n{state['draft']}"),
        ],
    )
    return {"critique": response.content}


def node_policy_gate(state: AgentState) -> dict:
    """Deterministic Policy Gate (Hard Rails)"""
    # 1. Content Safety
    policy_result = run_policy_gate(state["draft"])
    issues = policy_result.get("issues", [])

    # 2. Syntax/Bug check if code
    if state["task"].task_type == TaskType.CODE_GEN:
        bug_result = run_bugbot(state["draft"])
        if not bug_result["passed"]:
            issues.append(f"Bugbot Failed: {bug_result['output']}")

    return {"policy_issues": issues}


def node_arbiter(state: AgentState) -> dict:
    """Tier 2 Agent (Strongest LLM): Final Judgment"""
    llm = get_strong_llm(temperature=0.0)

    prompt = f"""
    You are the Arbiter (Judge #6).
    TASK: {state["task"].description}
    DRAFT: {state["draft"]}
    CRITIQUE: {state["critique"]}
    POLICY ISSUES: {state["policy_issues"]}

    Synthesize a final, safe, high-quality answer.
    If policy issues exist, FIX THEM explicitly.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_output": response.content}


# --- Edges (The Logic) ---


def route_after_draft(state: AgentState):
    # If high risk, go to critique. If low risk, maybe skip?
    # strictly following doctrine: All code gets gates.
    return "policy_gate"


def route_after_gate(state: AgentState):
    if state["policy_issues"] or state["risk_level"] in [RiskLevel.RED, RiskLevel.AMBER]:
        return "critic"
    return "arbiter"  # Fast track for GREEN with no issues? Or just finalize.


# --- Graph Compilation ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("router", node_router)
workflow.add_node("drafter", node_drafter)
workflow.add_node("policy_gate", node_policy_gate)
workflow.add_node("critic", node_critic)
workflow.add_node("arbiter", node_arbiter)

# Set Entry Point
workflow.set_entry_point("router")

# Add Edges
workflow.add_edge("router", "drafter")
workflow.add_edge("drafter", "policy_gate")

workflow.add_conditional_edges(
    "policy_gate",
    route_after_gate,
    {"critic": "critic", "arbiter": "arbiter"},
)

workflow.add_edge("critic", "arbiter")
workflow.add_edge("arbiter", END)

# Compile
app_orchestrator = workflow.compile()
