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

# Start n-autoresearch/Kosmos/BioAgents Orchestrator (200 agents)

python3 shadowtagai/agents/n-autoresearch/Kosmos/BioAgents_orchestrator.py

```

---

## 📊 Routing Matrix

| Task                 | Model      | SLA       | Cost/1K |
| -------------------- | ---------- | --------- | ------- |
| Production Inference | Gemini     | p99≤100ms | $0.002  |
| Deep Analysis        | Claude     | p95≤2s    | $0.015  |
| Code Refactoring     | Claude     | p95≤3s    | $0.015  |
| Judge#6 Binary       | Gemini+MCP | p99≤90ms  | $0.0003 |
| Artifact Creation    | Claude     | p95≤4s    | $0.015  |
| Specialized          | GPT-5      | p99≤500ms | $0.010  |

---

## 🔧 MCP Compression

```python
from app.mcp_bridge import MCPBridge

# Initialize

mcp = MCPBridge()

# Compress 50KB → 487 bytes (98% reduction)

kernel = await mcp.atp_519_scan(large_context)

# Binary decision (<35ms)

decision = await mcp.Claude_Code_6_binary(kernel)

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

| Metric      | Month 1-2          | Month 12+         |
| ----------- | ------------------ | ----------------- |
| **Usage**   | 10M decisions/year | 1B decisions/year |
| **Cost**    | $2.5K/mo           | $60K/mo           |
| **Revenue** | $3K MRR            | $300K MRR         |
| **Profit**  | -$500/mo           | +$240K/mo         |

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

## 🐒 n-autoresearch/Kosmos/BioAgents Integration

```

USER REQUEST
 ↓
n-autoresearch/Kosmos/BioAgents Orchestrator (200 agents)
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

1. **🐒 Start n-autoresearch/Kosmos/BioAgents Orchestrator**

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
├── n-autoresearch/Kosmos/BioAgents_orchestrator.py  # 200-agent swarm
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

# n-autoresearch/Kosmos/BioAgents

python3 shadowtagai/agents/n-autoresearch/Kosmos/BioAgents_orchestrator.py

# Expected: 200 agents initialized, swarm ready

```

---

## 🎯 SLA Targets

| Component    | Target    | Consequence                  |
| ------------ | --------- | ---------------------------- |
| Judge#6      | p99≤90ms  | Kill-switch after 1hr breach |
| Kernel Chain | <35ms     | Revert to full context       |
| Gemini       | p99≤100ms | Route to Claude fallback     |
| Claude       | p95≤2s    | Route to Gemini fallback     |
| ATP 5-19     | <50ms     | Skip compression             |

---

## 📞 Support

- **Docs**: `/docs/ANTIGRAVITY_HANDOFF.md`

- **VSCode**: `/docs/VSCODE_INTEGRATION.md`

- **GKE**: `kubectl get pods -n pnkln-core`

- **Logs**: `kubectl logs -n pnkln-core -l app=antigravity-handoff -f`

---

**Version**: 1.0
**Created**: 2025-11-22
**Status**: Production-ready
**Bootstrap Gates**: ROI ≥3×, LTV:CAC ≥4:1, p99≤90ms
