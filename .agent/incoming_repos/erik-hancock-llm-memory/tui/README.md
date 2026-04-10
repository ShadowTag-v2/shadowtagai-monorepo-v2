# Judge#6 TUI Monitor - Pattern Validation

## Architecture (Ported from Bottom)

### 1. **Immediate-Mode Rendering** ✓
```python
def update_display(self):  # Runs at 60Hz
    latency_widget.update_data()
    latency_widget.refresh()
    # ... redraw everything every frame
```
**Bottom equivalent:** `terminal.draw()` loop in `main.rs`

### 2. **Widget Composition** ✓
```
Judge6MonitorApp
├─ LatencySparklineWidget (Bottom's cpu_graph.rs)
├─ DecisionRateWidget (Bottom's metrics)
└─ ViolationTableWidget (Bottom's process_table.rs)
```

### 3. **Latency Tracking** ✓
```python
class LatencyStats:
    def percentile(self, p: float) -> float
```
**Bottom equivalent:** `LatencyHistogram` in runtime/profiling.py

### 4. **60Hz Update Loop** ✓
```python
self.set_interval(1/60, self.update_display)  # 16.67ms/frame
```
**Bottom equivalent:** 60 FPS target in render loop

---

## Test Plan

### Phase 1: Validate Mock Engine (NOW)
```bash
# Run the monitor
python3 tui/judge6_monitor.py --mode=mock

# Expected behavior:
# - p50: ~15-25ms (green)
# - p90: ~40-60ms (yellow)
# - p99: ~70-120ms (will violate 90ms SLA 5-10% of time)
```

**Hypothesis to test:**
> Can the TUI itself maintain 60Hz rendering while processing decisions?

### Phase 2: Add Real Judge#6 Backend
```python
# Replace MockJudge6Engine with:
from judge6.renderer.jr_engine import JREngineRenderer
from judge6.runtime.base import WASMRuntime

class RealJudge6Engine:
    async def make_decision(self) -> DecisionMetric:
        # Actual ATP_519_scan + WASM execution
        start = time.perf_counter_ns()
        result = await self.runtime.check_policy(context)
        latency_us = (time.perf_counter_ns() - start) // 1000
        return DecisionMetric(...)
```

### Phase 3: Add GitHub MCP Layer
```python
class GitHubMCPEngine:
    async def make_decision(self, pr_diff_url: str) -> DecisionMetric:
        # 1. Fetch diff via MCP
        start = time.perf_counter_ns()
        diff = await mcp_client.get_commit(repo, sha)

        # 2. Run ATP_519_scan compression
        compressed = atp_519_scan(diff)

        # 3. Judge#6 decision
        result = await judge6.check(compressed)

        latency_us = (time.perf_counter_ns() - start) // 1000
        return DecisionMetric(...)
```

---

## Metrics to Watch

| Metric | Target | Mock Expected | Real Expected | Notes |
|--------|--------|---------------|---------------|-------|
| p50    | <30ms  | 15-25ms ✓     | 20-40ms       | Fast path |
| p90    | <60ms  | 40-60ms ✓     | 50-80ms       | Medium path |
| p99    | ≤90ms  | 70-120ms ⚠️   | **TBD**       | **CRITICAL** |
| SLA %  | >99%   | ~92-95%       | **TBD**       | Must validate |

---

## Kill-Switch Triggers (from github-mcp-integration-plan_1.md)

1. **MCP latency > 50ms** → Adds to decision budget
2. **Token reduction < 30%** → Not worth integration cost
3. **p99 > 90ms consistently** → SLA violation

---

## Next Steps

1. **NOW:** Run `python3 tui/judge6_monitor.py --mode=mock` and observe baseline
2. **+10 min:** Let it run, watch if p99 stabilizes or spikes
3. **+30 min:** Add real Judge#6 backend (phase 2)
4. **+1 hour:** Add GitHub MCP layer (phase 3)
5. **+2 hours:** Make go/no-go decision on MCP integration

**The TUI is your decision support system.** If you can't hit 90ms p99 in the TUI, you won't hit it in production.
