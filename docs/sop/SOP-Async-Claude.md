# SOP: Async Claude Code Usage

**Version:** 1.0
**Status:** ACTIVE (Option 1 Trial)
**Effective:** 2025-11-25
**Review Date:** 7 days from activation

---

## Purpose

Enable non-blocking, long-running Claude Code tasks to increase JR Engine + Judge 6 development throughput while maintaining p99 governance standards.

---

## Scope

### ALLOWED Uses

| Task Type           | Examples                                    | Max Duration |
| ------------------- | ------------------------------------------- | ------------ |
| ShadowTag Analysis  | DCT watermark prototypes, provenance checks | 2 hours      |
| JR Engine Analytics | Performance profiling on scrubbed logs      | 1 hour       |
| Code Review         | Large refactor simulations, security audits | 30 min       |
| Documentation       | API docs generation, architecture diagrams  | 1 hour       |

### FORBIDDEN Uses

| Category                 | Reason                |
| ------------------------ | --------------------- |
| Schema migrations        | Production impact     |
| Infrastructure changes   | Irreversible          |
| Secrets/credentials      | Security exposure     |
| Live customer data       | Compliance violation  |
| Production deployments   | Governance bypass     |
| Final Judge 6 decisions | Audit trail integrity |

---

## Procedure

### 1. Pre-Flight Check

```bash
# Verify kill-switch is not active
cat /var/log/pnkln/claude-async/.kill_switch 2>/dev/null && echo "BLOCKED" || echo "CLEAR"
```

### 2. Run Async Task

```bash
# From prompt file
./scripts/async/claude_async.sh run <task_name> ./prompts/<file>.txt

# From inline prompt
./scripts/async/claude_async.sh run <task_name> - "Your prompt here"
```

### 3. Monitor Progress

```bash
# Check status
./scripts/async/claude_async.sh status <job_id>

# Watch live output
tail -f /var/log/pnkln/claude-async/<job_id>.log
```

### 4. Capture Teleport URL

When Claude outputs a teleport URL (format: `https://claude.ai/...`):

1. Copy URL immediately
2. Record in job manifest (auto-captured if present in output)
3. Use URL to continue conversation on web if needed

### 5. Validate Results

```bash
./scripts/async/claude_async.sh validate <job_id>
```

---

## Kill-Switch Protocol

### Trigger Conditions

Activate kill-switch if ANY occur:

1. **Message Display Bug** - Critical conversation parts hidden/dropped
2. **Missing Teleport URL** - URL not presented or not capturable
3. **Log Corruption** - Local logs missing, truncated, or unreadable
4. **CLI/Web Mismatch** - Inconsistency affecting conclusions

### Activation

```bash
./scripts/async/claude_async.sh kill-switch "Reason: <description>"
```

### Recovery

1. Investigate root cause
2. Document in incident log
3. Wait for Anthropic fix OR build GCP-native alternative
4. Remove kill-switch file only after verification:

```bash
rm /var/log/pnkln/claude-async/.kill_switch
```

---

## Trial Metrics (7-Day Window)

Track these metrics during trial period:

| Metric                                  | Baseline   | Target                     |
| --------------------------------------- | ---------- | -------------------------- |
| Time to complete long analysis          | T_baseline | T_async < 0.7 × T_baseline |
| Concurrent tasks per dev                | C_baseline | C_async > 2 × C_baseline   |
| Hard failure rate                       | N/A        | < 5%                       |
| Soft failure rate                       | N/A        | < 15%                      |
| Token reduction (repeated explanations) | N/A        | 40-60% savings             |

### Failure Definitions

- **Hard Failure**: Missing messages/logs/URL, job cannot be interpreted
- **Soft Failure**: Confusing UI, context glitches requiring restart

---

## Escalation Path

| Issue                   | Action                                                  | Contact             |
| ----------------------- | ------------------------------------------------------- | ------------------- |
| Suspected data exposure | Immediate kill-switch + incident report                 | Security Lead       |
| Repeated soft failures  | Document pattern, consider narrowing scope              | Engineering Lead    |
| Kill-switch triggered   | Evaluate Option 2 (hold) or Option 3 (build GCP-native) | Architecture Review |

---

## Related Documents

- `scripts/async/claude_async.sh` - Wrapper implementation
- `pnkln/safety/training_data_indexer.py` - Safety indexing module
- `pnkln/governance/judge_six.py` - Judge 6 governance engine

---

## Revision History

| Version | Date       | Change                                        | Author |
| ------- | ---------- | --------------------------------------------- | ------ |
| 1.0     | 2025-11-25 | Initial SOP based on JR Engine tuned decision | Claude |
