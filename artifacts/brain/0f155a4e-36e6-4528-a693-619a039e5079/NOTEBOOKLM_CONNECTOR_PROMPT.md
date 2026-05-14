# NotebookLM Connector Activation Prompt

**CONTEXT**:
We need to bridge Antigravity (Execution Engine) with NotebookLM (Grounded Intelligence). The goal is a "closed-loop system" where NotebookLM verifies plans before Antigravity executes.

**OBJECTIVE**:
Build the "Missing Connector" (Server + Config + Auth + Verification) via MCP (Model Context Protocol).

**INSTRUCTIONS**:

1.  **Scaffold the MCP Server**:
    *   Create `libs/aiyou/tools/notebooklm_mcp.py`.
    *   Implement capabilities to:
        *   `upload_source(content, verification_level)`
        *   `generate_briefing(source_ids, focus)`
        *   `query_notebook(question, context_ids)`

2.  **Configuration**:
    *   Update `config/toolbox/tools.yaml` to include the `notebooklm` toolset.
    *   Ensure strict "Pilot Mode" checks (Pre-Agent Verification).

3.  **Authentication**:
    *   Use `scripts/gcloud_auth_solver.py` pattern to authenticate against NotebookLM API (or simulate via Vertex AI Grounding if Native API is closed).

4.  **Verification**:
    *   Add a pre-execution hook in `src/agents/antigravity.py` that consults NotebookLM for "Hallucination Checks" before major destructive actions.

**EXECUTION**:
Run the setup script now.
