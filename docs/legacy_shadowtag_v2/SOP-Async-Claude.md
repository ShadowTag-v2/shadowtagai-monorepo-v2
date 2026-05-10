# SOP: Async Claude Operations

## Purpose

Standard Operating Procedure for asynchronous Claude Code tasks with teleport handoff and guard mount rotation.

---

## Key Principles

### 1. Guard Mount Discipline

- **4-hour shifts maximum**: After 4 hours, cognitive effectiveness drops rapidly

- **Rotate in groups of 25**: Fresh agents every shift

- **No agent works past exhaustion**: Kill switch enforced

### 2. Bar Exam Isolation

- During execution: **zero interaction**

- Output only at completion

- Neighbors at "kissing distance" but cannot communicate

### 3. OPORD-Based Handoff

- Every task starts with ATOMIC thread

- Every task ends with Handoff JSON

- No orphaned work

---

## Usage

### Start Async Task

```bash
./scripts/claude_async.sh start ATOMIC-001 "Fix Redis timeout" --tier FREE

```

### Check Status

```bash
./scripts/claude_async.sh status job_20241122_143052

```

### Kill Job (Manual or Auto)

```bash
./scripts/claude_async.sh kill job_20241122_143052

```

### Rotate Shifts

```bash
./scripts/claude_async.sh rotate

```

### List All Jobs

```bash
./scripts/claude_async.sh list

```

---

## Kill Switch Conditions

Jobs are automatically terminated if:

| Condition          | Threshold       | Rationale               |
| ------------------ | --------------- | ----------------------- |
| Runtime            | > 240 min (4hr) | Guard shift exhaustion  |
| Consecutive errors | >= 3            | Failing task, escalate  |
| p99 latency        | > 5000ms        | Performance degradation |

---

## Tier Routing

| Task Type           | Tier  | Cost/1K | Use When                  |
| ------------------- | ----- | ------- | ------------------------- |
| Discovery, indexing | FREE  | $0      | Bulk scanning             |
| Code generation     | FLASH | $0.10   | Standard dev work         |
| Complex reasoning   | PRO   | $1.00   | Architecture, refactoring |

---

## Teleport Protocol

When a job completes or is killed:

1. Log file contains full output: `logs/async/job_*.log`

2. Metadata JSON has handoff info: `logs/async/job_*.json`

3. TELEPORT URL provided: `file:///path/to/log`

To resume in new session:

```bash
cat logs/async/job_20241122_143052.log | tail -100

```

---

## Integration with ATOMIC Threads

### Before Starting Async Job

1. Create thread: `python scripts/atomic_thread_manager.py create --tier FREE --mission "..."`

2. Note thread ID: `ATOMIC-001`

3. Start async: `./scripts/claude_async.sh start ATOMIC-001 "..."`

### After Job Completes

1. Review output: `./scripts/claude_async.sh status job_*`

2. Complete thread: `python scripts/atomic_thread_manager.py complete ATOMIC-001 --outcome "..."`

3. Check handoff JSON for next action

---

## Shift Rotation Schedule

For sustained operations (Flying n-autoresearch/Kosmos/BioAgents at scale):

| Shift | Time   | Action                           |
| ----- | ------ | -------------------------------- |
| 1     | 0-4hr  | Deploy batch A (agents 1-25)     |
| 2     | 4-8hr  | Rotate to batch B (agents 26-50) |
| 3     | 8-12hr | Rotate to batch C (agents 51-75) |
| ...   | ...    | Continue rotation                |

Run `./scripts/claude_async.sh rotate` at each shift change.

---

## Emergency Procedures

### BLACK (Full Abort)

```bash

# Kill all running jobs

for pid_file in logs/async/*.pid; do
    kill $(cat "$pid_file") 2>/dev/null
done

```

### RED (Escalate)

- Tag thread as BLOCKED

- Document reason in Handoff JSON

- Notify human operator

### YELLOW (Monitor)

- Continue execution

- Increase logging verbosity

- Reduce request rate

---

## Metrics to Track

- Jobs started per shift

- Jobs completed vs killed

- Average runtime

- Error rate by tier

- Handoff completion rate
