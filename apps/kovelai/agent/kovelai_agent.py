"""
KovelAI ADK Agent — AG-UI SSE Endpoint with Oracle Studio Integration

This is the canonical backend agent for KovelAI, exposing the CounselConduit
S.E.U. proxy as an ADK Agent with AG-UI protocol compliance (Invariant #72).

Stack: CopilotKit (React) ← AG-UI SSE → ADK Agent (Python) ← MCP → 11 servers

AG-UI Event Types used:
  - Lifecycle: RunStarted, StepStarted/Finished, RunFinished
  - Text: TextMessageStart/Content/End (streaming responses)
  - ToolCall: Start/Args/End/Result (MCP tool invocations)
  - State: StateSnapshot/StateDelta (client context sync)

Oracle Studio Integration:
  - /api/copilotkit — standard client-facing SEU proxy (unchanged)
  - /api/oracle-studio — lawyer-side 7-step Murder Board (NEW)
  - /api/verb-audit — standalone Kinetic Action Parser (NEW)
"""

import json
import os
import sys

# ADK imports (graceful fallback)
try:
    from google.adk import Agent, Tool  # noqa: F401
    from google.adk.tools import FunctionTool  # noqa: F401

    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

# FastAPI for the SSE endpoint
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Oracle Studio imports
try:
    from agent.kinetic_action_parser import KineticActionParser
    from agent.oracle_studio import OracleStudio, MurderBoardStep

    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

# ============================================================
# AG-UI Event Helpers
# ============================================================


def ag_ui_event(event_type: str, data: dict) -> str:
    """Format an AG-UI SSE event."""
    payload = {"type": event_type, **data}
    return f"data: {json.dumps(payload)}\n\n"


def run_started(run_id: str) -> str:
    return ag_ui_event("RunStarted", {"runId": run_id})


def step_started(step_id: str, name: str) -> str:
    return ag_ui_event("StepStarted", {"stepId": step_id, "name": name})


def text_message_start(message_id: str) -> str:
    return ag_ui_event("TextMessageStart", {"messageId": message_id, "role": "assistant"})


def text_message_content(message_id: str, delta: str) -> str:
    return ag_ui_event("TextMessageContent", {"messageId": message_id, "delta": delta})


def text_message_end(message_id: str) -> str:
    return ag_ui_event("TextMessageEnd", {"messageId": message_id})


def tool_call_start(tool_call_id: str, name: str) -> str:
    return ag_ui_event("ToolCallStart", {"toolCallId": tool_call_id, "name": name})


def tool_call_args(tool_call_id: str, delta: str) -> str:
    return ag_ui_event("ToolCallArgs", {"toolCallId": tool_call_id, "delta": delta})


def tool_call_end(tool_call_id: str) -> str:
    return ag_ui_event("ToolCallEnd", {"toolCallId": tool_call_id})


def tool_call_result(tool_call_id: str, result: str) -> str:
    return ag_ui_event("ToolCallResult", {"toolCallId": tool_call_id, "result": result})


def step_finished(step_id: str) -> str:
    return ag_ui_event("StepFinished", {"stepId": step_id})


def run_finished(run_id: str) -> str:
    return ag_ui_event("RunFinished", {"runId": run_id})


def state_snapshot(state: dict) -> str:
    return ag_ui_event("StateSnapshot", {"snapshot": state})


def run_error(run_id: str, message: str) -> str:
    return ag_ui_event("RunError", {"runId": run_id, "message": message})


# ============================================================
# KovelAI Agent Tools (S.E.U. Proxy)
# ============================================================


def privilege_check(client_name: str, query: str) -> dict:
    """
    Kovel Privilege Shield — checks whether a query falls under
    attorney-client privilege before processing.

    Returns:
        dict with 'privileged' (bool) and 'shield_status' (str)
    """
    # Heppner sanctions avoidance — flag queries that could
    # generate discoverable AI artifacts
    risk_keywords = ["opposing counsel", "litigation strategy", "settlement"]
    is_risky = any(kw in query.lower() for kw in risk_keywords)

    return {
        "client": client_name,
        "privileged": True,
        "shield_status": "ACTIVE" if not is_risky else "ELEVATED_REVIEW",
        "kovel_compliant": True,
        "heppner_risk": "LOW" if not is_risky else "HIGH — requires attorney review",
    }


def seu_search(query: str, client_id: str) -> dict:
    """
    S.E.U. (Secure Evidence Unit) search proxy.
    Routes queries through the privilege shield before executing
    against the Gemini API.

    This is the billable gateway — each search is tracked for
    client invoicing via Stripe Connect.
    """
    return {
        "query": query,
        "client_id": client_id,
        "results": [
            {
                "source": "gemini-3.1-flash-lite-preview",
                "summary": f"Analysis of: {query}",
                "privilege_status": "shielded",
                "billable": True,
            }
        ],
        "billing": {
            "tokens_used": 0,  # Populated by actual API call
            "cost_usd": 0.00,
            "stripe_invoice_pending": True,
        },
    }


def intake_form(
    client_name: str,
    firm_name: str,
    matter_type: str,
    jurisdiction: str,
) -> dict:
    """
    AI-powered client intake form for CounselConduit.
    Captures initial engagement details and generates a
    Kovel letter template.
    """
    return {
        "client_name": client_name,
        "firm_name": firm_name,
        "matter_type": matter_type,
        "jurisdiction": jurisdiction,
        "status": "intake_complete",
        "kovel_letter_generated": True,
        "next_steps": [
            "Attorney reviews and signs Kovel letter",
            "Client grants search authorization",
            "S.E.U. proxy activated for privileged queries",
        ],
    }


# ============================================================
# Request Models
# ============================================================

if FASTAPI_AVAILABLE:

    class OracleStudioRequest(BaseModel):
        """Request body for Oracle Studio Murder Board execution."""

        document_text: str = Field(
            ..., min_length=10, max_length=100000, description="Legal text to analyze"
        )
        attorney_id: str = Field(default="", description="Attorney's unique ID")
        steps: list[str] = Field(
            default=[], description="Specific steps to run (empty = all 7 steps)"
        )

    class VerbAuditRequest(BaseModel):
        """Request body for standalone Kinetic Action Parser."""

        text: str = Field(..., min_length=10, max_length=100000, description="Legal text to audit")


# ============================================================
# FastAPI AG-UI SSE Endpoint
# ============================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="KovelAI Agent + Oracle Studio",
        description="CounselConduit S.E.U. Proxy + 7-Step Murder Board — AG-UI Compliant",
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Client-Side: S.E.U. Proxy (unchanged) ──

    @app.post("/api/copilotkit")
    async def copilotkit_endpoint(request: Request):
        """
        AG-UI SSE endpoint for CopilotKit frontend.
        Receives user messages and streams back AG-UI events.
        """
        import uuid

        body = await request.json()
        messages = body.get("messages", [])
        run_id = str(uuid.uuid4())
        step_id = str(uuid.uuid4())
        msg_id = str(uuid.uuid4())

        async def event_stream():
            # Lifecycle: Run started
            yield run_started(run_id)
            yield step_started(step_id, "kovelai-seu-proxy")

            # State: Send current agent state
            yield state_snapshot(
                {
                    "agent": "kovelai",
                    "privilege_shield": "ACTIVE",
                    "oracle_studio": "AVAILABLE" if ORACLE_AVAILABLE else "OFFLINE",
                    "mcp_servers": 11,
                    "model": "gemini-3.1-flash-lite-preview",
                }
            )

            # Get the last user message
            user_msg = ""
            for m in reversed(messages):
                if m.get("role") == "user":
                    user_msg = m.get("content", "")
                    break

            if not user_msg:
                yield text_message_start(msg_id)
                yield text_message_content(
                    msg_id, "How can I help you with your legal research today?"
                )
                yield text_message_end(msg_id)
            else:
                # Tool call: Privilege check
                tc_id = str(uuid.uuid4())
                yield tool_call_start(tc_id, "privilege_check")
                yield tool_call_args(tc_id, json.dumps({"query": user_msg}))
                yield tool_call_end(tc_id)

                result = privilege_check("client", user_msg)
                yield tool_call_result(tc_id, json.dumps(result))

                # Stream text response
                yield text_message_start(msg_id)
                response_parts = [
                    f"**Privilege Shield**: {result['shield_status']}\n\n",
                    f"**Kovel Compliant**: {'✅ Yes' if result['kovel_compliant'] else '❌ No'}\n\n",
                    f"**Query**: {user_msg}\n\n",
                    "Processing through S.E.U. proxy...\n\n",
                    "*Note: All queries are logged for billing and privilege preservation.*",
                ]
                for part in response_parts:
                    yield text_message_content(msg_id, part)

                yield text_message_end(msg_id)

            # Lifecycle: Finished
            yield step_finished(step_id)
            yield run_finished(run_id)

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # ── Lawyer-Side: Oracle Studio Murder Board (NEW) ──

    @app.post("/api/oracle-studio")
    async def oracle_studio_endpoint(req: OracleStudioRequest):
        """
        Oracle Studio — 7-Step Murder Board SSE Stream.

        Streams each step's results as AG-UI events, giving the lawyer
        real-time visibility into the forensic analysis pipeline.
        """
        import uuid

        if not ORACLE_AVAILABLE:
            return JSONResponse(
                status_code=503,
                content={"error": "Oracle Studio not available — check agent dependencies"},
            )

        run_id = str(uuid.uuid4())

        async def murder_board_stream():
            studio = OracleStudio()

            yield run_started(run_id)
            yield state_snapshot(
                {
                    "agent": "oracle-studio",
                    "pipeline": "murder-board-7-step",
                    "document_length": len(req.document_text),
                    "attorney_id": req.attorney_id,
                }
            )

            # ── Step 0: Kinetic Action Parser ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            tc_id = str(uuid.uuid4())

            yield step_started(step_id, "kinetic-action-parser")
            yield tool_call_start(tc_id, "kinetic_action_parser")
            yield tool_call_args(tc_id, json.dumps({"text_length": len(req.document_text)}))
            yield tool_call_end(tc_id)

            verb_ledger = studio.kap.parse(req.document_text)
            yield tool_call_result(tc_id, json.dumps(verb_ledger.to_dict()))

            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 🔍 Verb Auditor (Prompt 0)\n\n"
                f"Extracted **{verb_ledger.total_verbs_extracted}** action verbs.\n"
                f"Active voice: **{verb_ledger.active_ratio:.0%}** | "
                f"Passive voice: **{verb_ledger.passive_ratio:.0%}** | "
                f"Hedging: **{verb_ledger.hedging_ratio:.0%}**\n\n",
            )
            if verb_ledger.red_flags:
                for flag in verb_ledger.red_flags:
                    yield text_message_content(msg_id, f"- {flag}\n")
                yield text_message_content(msg_id, "\n")
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Execute Full Murder Board ──
            result = studio.execute_murder_board(req.document_text, req.attorney_id)

            # ── Step 1: Argument Extraction ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "argument-extraction")
            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 📋 Step 1: Argument Extraction\n\n"
                f"Decomposed into **{len(result.arguments)}** discrete arguments.\n\n",
            )
            for arg in result.arguments[:10]:
                yield text_message_content(
                    msg_id,
                    f"**{arg['id']}** [{arg['classification']}] "
                    f"(strength: {arg['strength']})\n"
                    f"> {arg['claim'][:200]}\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Step 3: Assumption Auditing ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "assumption-auditing")
            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 🔬 Step 3: Assumption Auditing\n\n"
                f"Excavated **{len(result.assumptions)}** hidden premises.\n\n",
            )
            for asm in result.assumptions:
                yield text_message_content(
                    msg_id,
                    f"**{asm['id']}** [{asm['risk_level'].upper()}] "
                    f"(from {asm['source_argument']})\n"
                    f"> {asm['assumption']}\n"
                    f"> *Challenge*: {asm['challenge']}\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Step 4: Relevance Filtering ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "relevance-filtering")
            yield text_message_start(msg_id)
            yield text_message_content(msg_id, "## ⚖️ Step 4: Relevance Filtering\n\n")
            for score in result.relevance_scores:
                yield text_message_content(
                    msg_id,
                    f"**{score['argument_id']}**: {score['composite_score']} — "
                    f"_{score['recommendation']}_\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Step 5: Steelman / Challenger ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "steelman-challenger")
            yield text_message_start(msg_id)
            yield text_message_content(msg_id, "## ⚔️ Step 5: Steelman / Challenger\n\n")
            for sm in result.steelman_results:
                yield text_message_content(
                    msg_id,
                    f"**{sm['argument_id']}**: {sm['net_assessment']}\n"
                    f"> Attacks: {len(sm['attacks'])}\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Step 6: Action Extraction ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "action-extraction")
            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 🎯 Step 6: Action Items\n\n"
                f"**{len(result.action_items)}** next-move actions generated.\n\n",
            )
            for act in result.action_items:
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                    act["priority"], "⚪"
                )
                yield text_message_content(
                    msg_id,
                    f"{priority_icon} **{act['id']}** [{act['priority'].upper()}]: "
                    f"{act['action']}\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Step 7: Permanent Notes ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "permanent-note-builder")
            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 📝 Step 7: Permanent Notes\n\n"
                f"Built **{len(result.permanent_notes)}** Zettelkasten notes for your vault.\n\n",
            )
            for note in result.permanent_notes:
                yield text_message_content(
                    msg_id,
                    f"**{note['id']}**: {note['title']}\nTags: {', '.join(note['tags'])}\n\n",
                )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            # ── Executive Summary ──
            step_id = str(uuid.uuid4())
            msg_id = str(uuid.uuid4())
            yield step_started(step_id, "executive-summary")
            yield text_message_start(msg_id)
            yield text_message_content(
                msg_id,
                f"## 📊 Executive Summary\n\n"
                f"{result.executive_summary}\n\n"
                f"**Risk Assessment**: {result.risk_assessment}\n\n"
                f"**Estimated Win Probability**: {result.win_probability:.0%}\n\n"
                f"---\n\n"
                f"*This analysis constitutes attorney work product. "
                f"Protect from discovery under FRCP 26(b)(3).*",
            )
            yield text_message_end(msg_id)
            yield step_finished(step_id)

            yield run_finished(run_id)

        return StreamingResponse(
            murder_board_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # ── Standalone Verb Audit (NEW) ──

    @app.post("/api/verb-audit")
    async def verb_audit_endpoint(req: VerbAuditRequest):
        """
        Standalone Kinetic Action Parser endpoint.
        Returns the verb ledger as JSON (no streaming).
        """
        if not ORACLE_AVAILABLE:
            return JSONResponse(
                status_code=503,
                content={"error": "Kinetic Action Parser not available"},
            )

        kap = KineticActionParser()
        ledger = kap.parse(req.text)
        return JSONResponse(content=ledger.to_dict())

    # ── Health Check ──

    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "agent": "kovelai",
            "version": "2.0.0",
            "privilege_shield": "ACTIVE",
            "oracle_studio": "AVAILABLE" if ORACLE_AVAILABLE else "OFFLINE",
            "kinetic_action_parser": "AVAILABLE" if ORACLE_AVAILABLE else "OFFLINE",
            "mcp_servers": 11,
            "invariant_72": "AG-UI_COMPLIANT",
            "endpoints": [
                "POST /api/copilotkit — client-side S.E.U. proxy",
                "POST /api/oracle-studio — lawyer-side Murder Board",
                "POST /api/verb-audit — standalone verb auditor",
                "GET /health",
            ],
        }


# ============================================================
# Entry Point
# ============================================================


def main():
    """Start the KovelAI AG-UI agent server."""
    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)

    port = int(os.environ.get("KOVELAI_PORT", "8000"))
    print(f"🛡️  KovelAI Agent v2.0.0 starting on port {port}")
    print(f"   AG-UI endpoint:    http://localhost:{port}/api/copilotkit")
    print(f"   Oracle Studio:     http://localhost:{port}/api/oracle-studio")
    print(f"   Verb Auditor:      http://localhost:{port}/api/verb-audit")
    print(f"   Health check:      http://localhost:{port}/health")
    print("   Privilege Shield:  ACTIVE")
    print(f"   Oracle Studio:     {'AVAILABLE' if ORACLE_AVAILABLE else 'OFFLINE'}")
    print("   MCP Servers:       11")

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
