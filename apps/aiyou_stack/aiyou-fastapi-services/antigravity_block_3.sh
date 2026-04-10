#!/bin/bash
set -e
cd ShadowTag-Omega 2>/dev/null || true

echo ">>> 🦍 BLOCK 3/5: INTELLIGENCE & AGENTS..."

# 1. DEEP RESEARCH (Interactions API)
cat <<PYTHON > libs/ShadowTag-v2/agents/deep_research.py
import logging
# Mock SDK for Beta
class Client: pass
class ResearchEngine:
    def __init__(self): self.model = "gemini-3-pro-interactions-exp"
    def report(self, topic, files=None):
        print(f"🧪 Deep Research: {topic} (Files: {len(files or [])})")
        return f"✅ REPORT GENERATED via {self.model}"
researcher = ResearchEngine()
PYTHON

# 2. RECURSIVE AGENT (The Brain)
cat <<PYTHON > libs/ShadowTag-v2/agents/recursive_rlm.py
import os, google.auth
from google import genai
class RecursiveAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-2.5-pro"
    def solve(self, prompt):
        ctx = ""
        if os.path.exists(".agent/context/GOOGLE_SCIENCE_DOCTRINE.md"):
            with open(".agent/context/GOOGLE_SCIENCE_DOCTRINE.md") as f: ctx = f"[DOCTRINE]\\n{f.read()}"
        return self.client.models.generate_content(model=self.model, contents=ctx+prompt).text
PYTHON

# 3. QUIBBLER & MCP CONFIG
mkdir -p .vscode .quibbler tools/mcp_servers

# Quibbler Rules
cat <<MD > .quibbler/rules.md
# QUIBBLER RULES
1. Governance: All code must pass Sentinel.
2. Architecture: No loose files in root.
3. Secrets: No hardcoded keys.
MD

# Deep Research MCP Server
cat <<PYTHON > tools/mcp_servers/deep_research_server.py
import sys, json
from libs.ShadowTag-v2.agents.deep_research import researcher
while True:
    line = sys.stdin.readline()
    if not line: break
    req = json.loads(line)
    if req.get("method") == "tools/call" and req["params"]["name"] == "deep_research":
        res = researcher.report(req["params"]["arguments"]["topic"])
        print(json.dumps({"jsonrpc":"2.0","id":req["id"],"result":{"content":[{"type":"text","text":res}]}})); sys.stdout.flush()
PYTHON

# VS Code MCP Config
cat <<JSON > .vscode/mcp.json
{
  "mcpServers": {
    "quibbler": { "command": "quibbler", "args": ["mcp"] },
    "deep-research": { "command": "python3", "args": ["tools/mcp_servers/deep_research_server.py"] }
  }
}
JSON

echo ">>> ✅ BLOCK 3 COMPLETE."
