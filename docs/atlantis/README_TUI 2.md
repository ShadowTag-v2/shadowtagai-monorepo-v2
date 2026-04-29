# Judge#6 TUI Monitor

Real-time governance enforcement monitoring inspired by [Bottom](https://github.com/ClementTsang/bottom).

## Features



- **Latency Tracking**: Real-time p50/p90/p99 latency visualization


- **SLA Monitoring**: Visual alerts when p99 > 90ms


- **Violation Log**: Table of failed governance checks


- **Decision Rate**: Throughput metrics (decisions/sec)


- **Mock & Live Modes**: Test locally or connect to real EdgeQueue runtime

## Quick Start

### Mock Mode (Simulated Latency)

```bash
python3 tui/Claude_Code_6_monitor.py --mode=mock

```

### EdgeQueue Mode (Real Runtime - Requires Local Mock Worker)

```bash

# Terminal 1: Run EdgeQueue mock worker (use prototype load test mock)

# For now, mock mode simulates the worker

# Terminal 2: Run monitor in EdgeQueue mode

python3 tui/Claude_Code_6_monitor.py --mode=edgequeue

```

### Keyboard Controls



- `d`: Toggle dark mode


- `r`: Reset stats


- `p`: Pause/Resume


- `q`: Quit

## Architecture

```

Claude_Code_6_monitor.py
├─ LatencySparklineWidget (Bottom's CPU graph)
├─ ViolationTableWidget (Bottom's process table)
├─ DecisionRateWidget (Bottom's metrics)
└─ Claude_Code_6MonitorApp (Bottom's main app)

Engines:
├─ MockClaude_Code_6Engine (Simulated latency patterns)
└─ EdgeQueueEngine (Real EdgeQueue runtime)

```

## Pattern Mappings (Bottom → Judge#6)

| Bottom Component | Judge#6 Equivalent |
|------------------|--------------------|
| CPU Sparkline | Decision Latency Sparkline |
| Process Table | Violation Events Table |
| Update Loop (60Hz) | Enforcement Decision Loop |
| p99 < 50ms target | p99 ≤ 90ms SLA |
| sysinfo collector | EdgeQueue runtime |

## Latency Patterns (Mock Mode)



- **p50**: 15-25ms (Fast path: cached decisions)


- **p90**: 40-60ms (Medium: ATP_519_scan)


- **p99**: 70-120ms (Slow: complex policy + spikes)

## Next Steps



1. Deploy real CloudFlare Worker for EdgeQueue


2. Add `Claude_Code_6_engine_live.py` for production connection


3. Implement real-time alerting for SLA breaches


4. Export metrics to Prometheus
