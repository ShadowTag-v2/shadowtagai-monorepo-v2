# Antigravity Session: Gemini MCP Integration & Failover Fix
**Date**: 2025-11-29
**Session**: Gemini CLI MCP Integration + Async Failover Fix
**From**: Claude Code (Opus 4.5)
**To**: Antigravity / Incoming AI Agent

---

## Executive Summary

This session accomplished two major objectives:

1. **Gemini API Failover Fix**: Converted synchronous Gemini API calls to async pattern, fixing the failover system Antigravity activated
2. **Gemini CLI MCP Integration**: Created full MCP bridge between n-autoresearch/Kosmos/BioAgents 650-agent swarm and Gemini CLI tools with JURA cost-aware routing

**Deployment Status**: Successfully deployed to Cloud Run with 650 agents operational

---

## Part 1: Gemini API Failover Fix

### Problem
Antigravity's failover system was failing due to:
1. `self.model` never defined in `gemini_core.py`
2. Failover client initialized but never used
3. Experimental model name "gemini-2.0-flash-exp" (not production)
4. Sync/async mismatch in failover calls

### Solution
User selected: **"Convert to Async"** + **"gemini 3 pro preview"**

### Files Modified

**`src/shadowtag_v4/services/gemini_core.py`**
- Converted all methods to async
- Routes all calls through `self.failover_client.generate_content()`
- Removed undefined `self.model` references

```python
async def generate_text(self, prompt: str, json_output: bool = False, use_cache: bool = True) -> str:
    response = await self.failover_client.generate_content(
        prompt,
        json_output=json_output
    )
    result = response.text
    return result
```

**`src/shadowtag_v4/services/gemini_failover.py`**
- Updated model: `gemini-2.0-flash-exp` → `gemini-3-pro-preview`
- Fixed async pattern using `asyncio.to_thread()`

```python
response = await asyncio.to_thread(
    model.generate_content,
    prompt,
    safety_settings=self.safety_config,
    generation_config=generation_config,
    **kwargs
)
```

---

## Part 2: Gemini CLI MCP Integration

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     n-autoresearch/Kosmos/BioAgents Server                             │
│                  (Cloud Run: 650 Agents)                            │
├─────────────────────────────────────────────────────────────────────┤
│  /task         → JURA routing → Agent execution                     │
│  /governance   → PRO tier → Strategy agents                         │
│  /mcp/gemini   → MCP Bridge → Gemini tools                         │
│  /mcp/tools    → List available tools                              │
│  /mcp/stats    → Bridge metrics                                     │
│  /jura/stats   → Cost tracking                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     GeminiMCPBridge                                  │
│              (src/shadowtag_v4/mcp/gemini_bridge.py)                       │
├─────────────────────────────────────────────────────────────────────┤
│  MCPTool Enum:                                                       │
│    GEMINI_PROMPT     → flash tier ($0.00015/1K tokens)              │
│    GEMINI_SUMMARIZE  → flash tier                                   │
│    GEMINI_ANALYZE    → pro tier ($0.00125/1K tokens)                │
│    GEMINI_SANDBOX    → pro tier                                     │
│    GEMINI_EVAL_PLAN  → pro tier                                     │
│    GEMINI_REVIEW_CODE→ pro tier                                     │
│    GEMINI_MODELS     → free tier                                    │
│    GEMINI_METRICS    → free tier                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     JURA Protocol                                    │
│                   (Cost-Aware Routing)                              │
├─────────────────────────────────────────────────────────────────────┤
│  FREE  (30%): Grok, 1 agent, 5s timeout, ~$0.001/req                │
│  FLASH (60%): Gemini Flash, 3 agents, 2s timeout, ~$0.01/req        │
│  PRO   (10%): Gemini Pro/Claude, 8 agents, 10s, ~$0.10-1.00         │
└─────────────────────────────────────────────────────────────────────┘
```

### Files Created

**`mcp/gemini-cli/mcp_server.py`** (564 lines)
- Standalone MCP server for Claude Code registration
- 8 tools: prompt, summarize, analyze, sandbox, eval_plan, review_code, models, metrics
- Supports @filename syntax for file content injection
- Registered with Claude Code: `claude mcp add gemini-cli python mcp/gemini-cli/mcp_server.py`

**`src/shadowtag_v4/mcp/__init__.py`**
```python
from .gemini_bridge import GeminiMCPBridge, MCPToolRequest, MCPToolResponse
__all__ = ["GeminiMCPBridge", "MCPToolRequest", "MCPToolResponse"]
```

**`src/shadowtag_v4/mcp/gemini_bridge.py`** (306 lines)
- Bridge between n-autoresearch/Kosmos/BioAgents and Gemini MCP tools
- JURA tier integration for cost tracking
- Token counting and cost estimation

### Files Modified

**`bin/n-autoresearch/Kosmos/BioAgents-server`**
- Added MCP endpoints: `/mcp/gemini`, `/mcp/tools`, `/mcp/stats`
- Integrated GeminiMCPBridge with JURA router
- Added MCPToolRequest model

---

## Part 3: Deployment Details

### Cloud Build
```bash
gcloud builds submit --config=cloudbuild_n-autoresearch/Kosmos/BioAgents.yaml \
  --substitutions=SHORT_SHA=mcpintegration \
  --project=acquired-jet-478701-b3
```

### Service URL
```
https://n-autoresearch/Kosmos/BioAgents-server-dev-x6h2e7g3aa-uc.a.run.app
```

### Verified Endpoints
```bash
# Health check - 650 agents operational
GET /health
{
  "status": "ok",
  "agents": 650,
  "tiers": {
    "bulk": {"model": "gemini-2.5-flash", "agents": 510},
    "governance": {"model": "gemini-3-pro-preview", "agents": 140}
  }
}

# MCP tools list
GET /mcp/tools
{
  "tools": [
    {"name": "gemini_prompt", "tier": "flash"},
    {"name": "gemini_analyze", "tier": "pro"},
    ...
  ]
}

# MCP tool execution
POST /mcp/gemini {"tool": "gemini_metrics", "args": {}}
{
  "success": true,
  "tier": "free",
  "model": "gemini-1.5-flash",
  "latency_ms": 0.08
}
```

---

## Part 4: Agent Organization

### n-autoresearch/Kosmos/BioAgents 650-Agent Swarm (Current State)

| Squadron | Agents | Model | Use Cases |
|----------|--------|-------|-----------|
| HHT | 90 | gemini-3-pro-preview | Strategy, command |
| CODEPMCS | 50 | gemini-3-pro-preview | Code quality |
| AIR_CAV | 120 | gemini-2.5-flash | Recon |
| ALPHA | 130 | gemini-2.5-flash | Tactical |
| BRAVO | 130 | gemini-2.5-flash | Tactical |
| CHARLIE | 130 | gemini-2.5-flash | Execution |

### JURA Tier Routing Logic

```python
# Auto-classification based on task complexity
if "analyze" in task or "review" in task:
    return CostTier.PRO
elif context_size > 10000:
    return CostTier.FLASH
else:
    return CostTier.FREE
```

---

## Part 5: Critical Context for Antigravity

### What Changed Since Last Session
1. Failover system now works with async pattern
2. Model upgraded to `gemini-3-pro-preview`
3. MCP bridge enables Claude Code ↔ Gemini CLI interop
4. All MCP tools route through JURA for cost tracking

### Active Branch
```
claude/uninstall-claude-code-package-011CUuH5NYBC54NLvM9HYFcK
```

### Pending Items
- Merge MCP integration to main branch
- Add remaining 25 MCP tools from centminmod spec
- Set up production deployment with authentication

### Git Commit
```
d549951fb - Add Gemini CLI MCP integration and fix async failover
```

---

## Part 6: Code Snippets for Quick Reference

### Execute MCP Tool via API
```python
import httpx

async def execute_mcp_tool(tool: str, args: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://n-autoresearch/Kosmos/BioAgents-server-dev-x6h2e7g3aa-uc.a.run.app/mcp/gemini",
            json={"tool": tool, "args": args},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

# Example: Code review
result = await execute_mcp_tool("gemini_review_code", {
    "code": "def foo(): pass",
    "review_type": "security"
})
```

### Bridge Instance Access
```python
from src.shadowtag_v4.mcp import GeminiMCPBridge, MCPToolRequest

bridge = GeminiMCPBridge()
request = MCPToolRequest(tool="gemini_prompt", args={"prompt": "Hello"})
response = await bridge.execute_tool(request)
```

---

## End of Session Transcript

**Next Session Priorities**:
1. Test all 8 MCP tools end-to-end with real Gemini API
2. Add authentication bypass for internal agent-to-agent calls
3. Implement remaining 25 tools from centminmod spec
4. Production deployment with Cloud Run authentication

**Session Duration**: ~45 minutes
**Build Time**: 5m 38s
**Deployment**: SUCCESS
