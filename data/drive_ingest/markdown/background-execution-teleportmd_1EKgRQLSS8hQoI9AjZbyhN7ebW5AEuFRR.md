# Background Task Execution with Teleport

## Overview

Claude Code's background execution feature (`&` suffix) enables async workflows with web-based monitoring. This document covers integration with ShadowTagAI's OPORD-based atomic chat system.

## Feature Capabilities

**FEATURE**: `&` suffix in CLI → background execution + web session URL
**PERSISTENCE**: Conversation maintained, messages displayed (w/ known bug)
**REQUIREMENT**: GitHub repos connected to Claude Code web
**STATUS**: Live, production-ready (with caveats)

## Use Cases for ShadowTagAI

### 1. Long-Running Security Audits

```bash
# Background execution for multi-hour smart contract audit
/agent blockchain-security-auditor contracts/tba/ShadowTagAccount.sol &

# Returns teleport URL: https://code.claude.com/session/abc123
# Monitor progress in browser while CLI remains available
```

### 2. Large-Scale Refactors

```bash
# Refactor 300k+ LOC codebase in background
/dev-docs "Migrate all services to async/await pattern" &

# Continue other work in CLI
# Check teleport URL for phase completion
```

### 3. Judge#6 Performance Analysis

```bash
# Analyze governance decision logs (multi-hour task)
claude code "Analyze Judge#6 p99 latency patterns in production logs" &

# Teleport to web for real-time progress
# Results logged to Context Index when complete
```

### 4. Autoresearch Swarm Coordination

```bash
# Broadcast OPORD to 200 agents (async consensus building)
/agent swarm-orchestrator-specialist "Route 50 tasks to Shift 1" &

# Monitor consensus votes via teleport
# CLI free for emergency overrides
```

## Integration with OPORD System

### Background OPORD Execution

```python
# In atomic_chat_manager.py
def create_background_opord(
    task_title: str,
    agent_id: str,
    shift_number: int,
    teleport_url: Optional[str] = None
) -> int:
    """
    Create OPORD for background task with teleport monitoring.
    """
    opord_num = self.create_opord(
        task_title=task_title,
        agent_id=agent_id,
        shift_number=shift_number,
        mission={
            "who": agent_id,
            "what": task_title,
            "when": "Async (background)",
            "where": "Background process",
            "why": "Long-running task requiring async execution"
        },
        command_signal={
            "command": "SwarmOrchestrator",
            "signal": f"Teleport URL: {teleport_url}" if teleport_url else "CLI only",
            "succession": ["Primary: Background process", "Alternate: Foreground fallback"]
        },
        tags=["background", "teleport", "async"]
    )

    logger.info(f"Created background OPORD {opord_num:05d} with teleport: {teleport_url}")
    return opord_num
```

### Teleport URL Logging

```python
# Log teleport URLs to Context Index for audit trail
context_index.create_context(
    issue_title=f"Background Task: {task_title}",
    brief=f"Teleport URL: {teleport_url}\nOPORD: {opord_num:05d}",
    tags=["teleport", "background", "async"]
)
```

## Revenue Opportunities

### 1. Async Monitoring Upsell (ShadowTag DCT)

```python
# Video watermarking inherently async
# Charge premium for monitored processing

PRICING = {
    "fire_and_forget": 0.005,  # $0.005/minute
    "monitored": 0.01,          # $0.01/minute (2× revenue)
    "priority_monitored": 0.02  # $0.02/minute (4× revenue)
}

# Teleport-style progress viewer in client SDK
# Target: +$200-500 MRR within 4 weeks
```

### 2. Judge#6 Audit Trail Monetization

```python
# Package background task logs as compliance feature
# "Governance Decision Replay" with teleport-style access

COMPLIANCE_TIER = {
    "basic": 0,              # No audit trail
    "standard": 100,         # 30-day retention
    "enterprise": 500        # Unlimited retention + teleport replay
}

# Target: Compliance teams at $500/mo
```

### 3. Kernel Chain Async API

```python
# Position as "$0.0003/decision, <35ms, async-ready"
# Add async execution layer for batch processing

BATCH_PRICING = {
    "sync": 0.0003,          # Per decision
    "async_batch": 0.0002,   # 33% discount for batch
    "monitored_batch": 0.00025  # Premium for progress tracking
}

# Target: Customers running multi-hour compliance scans
```

## Known Issues & Kill-Switch

### Message Display Bug

**ISSUE**: Early-stage feature has known bug in message display
**IMPACT**: Could lose critical context mid-governance-decision
**MITIGATION**: Kill-switch trigger

```python
# Kill-switch logic
def validate_teleport_context(opord_num: int) -> bool:
    """
    Verify context preservation after background execution.

    Returns False if message display bug detected.
    """
    # Check if all OPORD messages present in Context Index
    messages = context_index.get_opord_messages(opord_num)

    if len(messages) < expected_message_count:
        logger.error(f"KILL-SWITCH: Context loss detected in OPORD {opord_num:05d}")
        logger.error("Reverting to foreground execution for all future tasks")
        return False

    return True

# KILL-SWITCH TRIGGER:
# If context loss occurs in first 3 test tasks, disable background execution
```

### GitHub-Only Requirement

**ISSUE**: Feature requires GitHub repos connected to Claude Code web
**CONFLICT**: GCP-native stack preference
**WORKAROUND**: Accept GitHub for dev tooling, keep production on GCP

```bash
# Connect GitHub repos for dev workflows
# Keep GCP Source Repositories for production code
# Treat GitHub as "dev environment" only
```

## Testing Protocol

### Phase 1: Low-Risk Validation

```bash
# Test with non-critical task
cd /Users/pikeymickey/ShadowTag-v2-fastapi-services

# Create test task
echo "# Judge #6 Performance Analysis - Test Run

Analyze p99 latency patterns in existing JR Engine decision logs.
Focus: Token count vs decision time correlation.
No production changes." > test_task.md

# Run in background
claude code "Analyze test_task.md and generate performance report" &

# Copy teleport URL
# Open in browser
# Validate message display
# Check Context Index for complete logs
```

### Phase 2: Production Validation

```bash
# If Phase 1 succeeds, test with real security audit
/agent blockchain-security-auditor contracts/tba/ShadowTagAccount.sol &

# Monitor for context loss
# Verify audit report completeness
# Check kill-switch trigger
```

### Phase 3: Revenue Integration

```bash
# If Phase 2 succeeds, build progress monitoring into ShadowTag SDK
# Test with pilot customer
# Measure willingness-to-pay for monitored tier
# Target: $200-500 MRR within 4 weeks
```

## Fallback Strategy

If teleport feature fails p99 survivability:

1. **Immediate**: Revert to foreground CLI execution
2. **Short-term**: Use `tmux`/`screen` for async workflows
3. **Long-term**: Build custom GCP-native solution (Option 3)

```bash
# Fallback: tmux-based background execution
tmux new-session -d -s audit "claude code 'Run security audit'"
tmux attach -t audit  # Monitor progress
```

## Recommendation

**ADOPT Option 1**: Exploit now with kill-switch monitoring

**Rationale**:
- ✅ 20-30% dev cycle time reduction on multi-hour tasks
- ✅ Aligns with MCP token reduction strategy (40-60% target)
- ✅ Enables revenue opportunities (async monitoring upsell)
- ⚠️ Kill-switch mitigates message display bug risk
- ✅ Zero cost, included in existing Claude Code access

**Next Actions**:
1. Run Phase 1 testing (1-2 hours)
2. If successful, integrate with OPORD system
3. Build progress monitoring into ShadowTag SDK
4. Launch monitored tier pricing within 4 weeks

---

**SECURITY NOTE**: Teleport URL security model unclear. Assume bearer token semantics - treat URLs as sensitive, don't log to public repos.