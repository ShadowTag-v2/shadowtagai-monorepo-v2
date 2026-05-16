# Antigravity Quick Reference

**Fast lookup for day-to-day operations**

---

## 🚀 Quick Start

```bash
# Set API keys
export GEMINI_API_KEY="..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Test MCP Bridge (98% compression)
python3 app/mcp_bridge.py

# Test Antigravity Router (cross-model)
python3 app/antigravity_handoff.py

# Start https://github.com/karpathy/autoresearchs Orchestrator (200 agents)
python3 shadowtagai/agents/https://github.com/karpathy/autoresearchs_orchestrator.py
```

---

## 📊 Routing Matrix

| Task | Model | SLA | Cost/1K |
|------|-------|-----|---------|
| Production Inference | Gemini | p99≤100ms | $0.002 |
| Deep Analysis | Claude | p95≤2s | $0.015 |
| Code Refactoring | Claude | p95≤3s | $0.015 |
| Judge#6 Binary | Gemini+MCP | p99≤90ms | $0.0003 |
| Artifact Creation | Claude | p95≤4s | $0.015 |
| Specialized | GPT-5 | p99≤500ms | $0.010 |

---

## 🔧 MCP Compression

```python
from app.mcp_bridge import MCPBridge

# Initialize
mcp = MCPBridge()

# Compress 50KB → 487 bytes (98% reduction)
kernel = await mcp.atp_519_scan(large_context)

# Binary decision (<35ms)
decision = await mcp.judge_six_binary(kernel)
```

**Results**: 98% compression (20KB→412 bytes) in testing

---

## 🎯 Cross-Model Routing

```python
from app.antigravity_handoff import AntigravityRouter, TaskType

# Initialize
router = AntigravityRouter()

# Decide routing
routing = router.decide_routing(
    task_type=TaskType.PRODUCTION_INFERENCE,
    context_size_bytes=5000,
    sla_ms=100
)

# Execute handoff
result = await router.execute_handoff(prompt, context, routing)
```

**Distribution**: 40% Gemini, 35% Claude, 15% GPT-5, 10% Other

---

## 💰 Economics

| Metric | Month 1-2 | Month 12+ |
|--------|-----------|-----------|
| **Usage** | 10M decisions/year | 1B decisions/year |
| **Cost** | $2.5K/mo | $60K/mo |
| **Revenue** | $3K MRR | $300K MRR |
| **Profit** | -$500/mo | +$240K/mo |

**Bootstrap Gates**: ROI ≥3×, LTV:CAC ≥4:1, p99≤90ms

---

## ⚙️ Bootstrap Gates

```
✓ ROI ≥ 3.0× in 18 months
✓ LTV:CAC ≥ 4.0:1 in 12 months
✓ p99 ≤ 90ms (Judge#6)
✓ Daily cost limit: $2,500 (hard stop)
```

---

## 🐒 https://github.com/karpathy/autoresearchs Integration

```
USER REQUEST
 ↓
https://github.com/karpathy/autoresearchs Orchestrator (200 agents)
 ├─ Task decomposition (California Bar Protocol)
 ├─ Jury deliberation (3-phase anonymous voting)
 └─ Shift management (8-hour rotation)
 ↓
ANTIGRAVITY HANDOFF
 ├─ Route to Gemini (40%) - fast decisions
 ├─ Route to Claude (35%) - deep analysis
 ├─ MCP compression (98% reduction)
 └─ Judge#6 binary (<35ms governance)
 ↓
Legal Whiteboard (GitHub persistence)
```

---

## 📝 ATP 5-19 Risk Scoring

```
SEVERITY × PROBABILITY = RISK SCORE

0-25:   Low → Auto-approve
26-50:  Medium → Approve + monitor
51-75:  High → Human review required
76-100: Critical → Auto-deny + escalate
```

---

## 🔒 Security Checklist

- [ ] PII redaction enabled
- [ ] Audit trail configured
- [ ] TLS 1.3 in-transit
- [ ] AES-256 at-rest
- [ ] RBAC enforced
- [ ] API keys in GCP Secret Manager

---

## 🚨 Circuit Breakers

```python
# Gemini failures
if router.gemini_failures >= 3:
    # Fallback to Claude

# Claude failures
if router.claude_failures >= 3:
    # Fallback to Gemini
```

Max failures: 3 consecutive

---

## 📈 Monitoring

```bash
# Get router stats
router.get_stats()
# {
#   "total_handoffs": 100,
#   "model_distribution": {"gemini": 40, "claude": 35, ...},
#   "avg_latency_ms": "87.3",
#   "compression_rate": "98%"
# }

# Get MCP stats
mcp.get_stats()
# {
#   "total_scans": 50,
#   "avg_compression": "98%",
#   "p99_latency_ms": "14.2"
# }
```

---

## 🛠️ VSCode Tasks

Access via `Cmd+Shift+P → Tasks: Run Task`:

1. **🐒 Start https://github.com/karpathy/autoresearchs Orchestrator**
2. **🧪 Test Gemini Antigravity API**
3. **📊 Show Agent Swarm Status**
4. **🔄 Run Shift Handoff**
5. **🚀 Deploy to GKE**
6. **🔍 Check Bootstrap Gates**

---

## 📂 File Structure

```
app/
├── mcp_bridge.py              # MCP compression (98%)
├── antigravity_handoff.py     # Cross-model router
└── gemini_antigravity_api.py  # Gemini client

shadowtagai/agents/
├── https://github.com/karpathy/autoresearchs_orchestrator.py  # 200-agent swarm
├── core/
│   ├── legal_whiteboard.py        # GitHub persistence
│   ├── california_bar_protocol.py # Fact decomposition
│   ├── agent_isolation_protocol.py # Jury deliberation
│   ├── shift_management.py        # 8-hour rotation
│   └── cofounder_enhancements.py  # Business context

docs/
├── ANTIGRAVITY_HANDOFF.md     # Complete system docs
└── VSCODE_INTEGRATION.md      # VSCode setup guide
```

---

## 🧪 Testing

```bash
# MCP Bridge
python3 app/mcp_bridge.py
# Expected: 98% compression, <1ms latency

# Antigravity Router
python3 app/antigravity_handoff.py
# Expected: Routing decisions, model distribution

# https://github.com/karpathy/autoresearchs
python3 shadowtagai/agents/https://github.com/karpathy/autoresearchs_orchestrator.py
# Expected: 200 agents initialized, swarm ready
```

---

## 🎯 SLA Targets

| Component | Target | Consequence |
|-----------|--------|-------------|
| Judge#6 | p99≤90ms | Kill-switch after 1hr breach |
| Kernel Chain | <35ms | Revert to full context |
| Gemini | p99≤100ms | Route to Claude fallback |
| Claude | p95≤2s | Route to Gemini fallback |
| ATP 5-19 | <50ms | Skip compression |

---

## 📞 Support

- **Docs**: `/docs/ANTIGRAVITY_HANDOFF.md`
- **VSCode**: `/docs/VSCODE_INTEGRATION.md`
- **GKE**: `kubectl get pods -n pnkln-core`
- **Logs**: `kubectl logs -n pnkln-core -l app=antigravity-handoff -f`

---

---

## 🔌 Gemini CLI MCP Integration (NEW 2025-11-29)

### Cloud Run Deployment
```bash
# Service URL
https://https://github.com/karpathy/autoresearchs-server-dev-x6h2e7g3aa-uc.a.run.app

# 650 agents operational (upgraded from 200)
# - HHT: 90 agents (Strategy)
# - CODEPMCS: 50 agents (Code quality)
# - AIR_CAV: 120 agents (Recon)
# - ALPHA/BRAVO/CHARLIE: 390 agents (Execution)
```

### MCP Endpoints
```bash
GET  /health       # Health check (650 agents)
GET  /mcp/tools    # List 8 MCP tools
GET  /mcp/stats    # Bridge metrics
POST /mcp/gemini   # Execute MCP tool

# Example: Execute MCP tool
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -d '{"tool":"gemini_analyze","args":{"content":"...","analysis_type":"security"}}' \
  https://https://github.com/karpathy/autoresearchs-server-dev-x6h2e7g3aa-uc.a.run.app/mcp/gemini
```

### MCP Tools Available
| Tool | Tier | Cost/1K |
|------|------|---------|
| gemini_prompt | FLASH | $0.00015 |
| gemini_summarize | FLASH | $0.00015 |
| gemini_analyze | PRO | $0.00125 |
| gemini_sandbox | PRO | $0.00125 |
| gemini_eval_plan | PRO | $0.00125 |
| gemini_review_code | PRO | $0.00125 |
| gemini_models | FREE | $0.00 |
| gemini_metrics | FREE | $0.00 |

### Python Usage
```python
from src.pnkln-stack.mcp import GeminiMCPBridge, MCPToolRequest

bridge = GeminiMCPBridge()
request = MCPToolRequest(tool="gemini_analyze", args={"content": "..."})
response = await bridge.execute_tool(request)
```

---

**Version**: 1.1
**Updated**: 2025-11-29
**Status**: Production-ready (Cloud Run)
**Agents**: 650 operational
**Bootstrap Gates**: ROI ≥3×, LTV:CAC ≥4:1, p99≤90ms
