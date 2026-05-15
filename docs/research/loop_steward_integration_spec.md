# LoopSteward Integration Spec

## Overview
The `LoopSteward` is designed to be the autonomous heartbeat of the AGNT process, maintaining background continuation tasks without blocking the main event loop.

## Wiring into `__main__`

### 1. Initialization
In the primary entrypoint (e.g., `agnt_main.py` or equivalent), the `LoopSteward` must be initialized alongside the core engine.

```python
from scripts.loop_steward import LoopSteward
import threading

def init_steward():
    steward = LoopSteward(interval_minutes=5)
    # Run the steward in a background daemon thread
    t = threading.Thread(target=steward.start, daemon=True)
    t.start()
    return steward
```

### 2. Signal Handling
The main agent process must gracefully shut down the steward upon termination (`SIGINT`/`SIGTERM`). The steward checks `self.running`, so a graceful exit hook must toggle this boolean.

### 3. Task Continuation Logic
The LoopSteward reads from `.beads/tasks.jsonl` every 5 minutes. If an `IN_PROGRESS` or `DEFERRED` task is found with a scheduled continuation time matching the current window, the steward spawns a headless sub-agent to resume the work.

### 4. Tmux Isolation
The steward uses the `TmuxSocketManager` to spawn background shells. This guarantees that spawned tasks do not interfere with the active IDE or terminal state.
