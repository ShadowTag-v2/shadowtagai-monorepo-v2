import os
import sys

sys.path.append(os.getcwd())

from mcp.server.fastmcp import FastMCP
from src.governance.voting.cav_mtoe import CavMTOE

from src.governance.judge_six.core import JudgeSixEngine

mcp = FastMCP("minion Governance")
ARMY = CavMTOE(num_soldiers=650)
JUDGE = JudgeSixEngine()


@mcp.tool()
def assess_risk_consensus(intent: str, risk_level: str = "L") -> str:
    result = ARMY.bottom_up_vote(intent=intent, risk_level=risk_level)
    return f"✅ VOTE: {result['final_action']} ({result['approval_rate']:.1%})"


@mcp.tool()
def judge_six_evaluate(context: str, prob: int, sev: int) -> str:
    return JUDGE.evaluate_transaction(context, prob, sev)


if __name__ == "__main__":
    # Cloud Run compatibility: Bind to 0.0.0.0 and PORT
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Judge 6 Omega MCP on port {port}...")
    # Assuming FastMCP supports 'sse' transport via run() or run_sse()
    # If the library is standard, run() handles stdio.
    # For web/Cloud Run, we often need to expose the underlying FastAPI app or use a specific transport.
    # We will try a common pattern for MCP servers over HTTP.
    try:
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    except TypeError:
        # Fallback if transport arg isn't supported directly in run()
        # This implies we might need to use the fastapi app directly
        import uvicorn

        uvicorn.run(mcp._app, host="0.0.0.0", port=port)
