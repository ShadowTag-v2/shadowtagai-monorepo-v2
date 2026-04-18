# SOP: Claude Code Async Execution with Teleport

**Version**: 1.0
**Status**: TRIAL PHASE - Non-Production Only
**Owner**: ShadowTagAI Engineering
**Last Updated**: 2025-11-22

## Purpose

Enable async execution of long-running tasks (>30 min) using Claude Code's background execution (`&` suffix) and teleport URL monitoring, while maintaining strict p99 survivability standards.

## Scope

### ✅ ALLOWED Use Cases (Non-Production Only)

1. **ShadowTag DCT Analysis** - Watermark optimization on synthetic/scrubbed clips
2. **Judge#6 Performance Analytics** - p99 latency analysis on scrubbed logs
3. **Code Review Simulations** - Large refactor analysis with no deploy path
4. **Security Audits** - Smart contract analysis (test contracts only)
5. **Swarm Coordination** - Autoresearch task routing simulations

### ❌ FORBIDDEN Use Cases

1. **Schema Migrations** - Any database structure changes
2. **Infrastructure Changes** - GCP resource modifications, K8s deployments
3. **Secrets Management** - API keys, credentials, tokens
4. **Live Customer Data** - Production data, PII, regulated content
5. **Final Governance Decisions** - Judge#6 production rulings
6. **Mainnet Deployments** - Smart contract deployments to production chains

## Wrapper Script Usage

All async tasks MUST use the wrapper script for logging and monitoring:

```bash
# Location: scripts/claude_async.sh
./scripts/claude_async.sh "Task description" path/to/prompt.md

# Example:
./scripts/claude_async.sh \
  "ShadowTag DCT optimization analysis" \
  tasks/shadowtag_dct_analysis.md
```

### Wrapper Behavior

1. **Logs Input** - Writes prompt + params to `/var/log/pnkln/claude-async/<timestamp>.jsonl`
2. **Captures Teleport URL** - Parses and stores URL in `async_manifest.jsonl`
3. **Streams Output** - Uses `tee` to mirror stdout/stderr to local log
4. **Validates Context** - Checks for message display bugs post-execution

## Trial Metrics (7-Day Window)

### Baseline vs Trial Comparison

Track these metrics:

| Metric | Baseline (Sync CLI) | Trial (Async `&`) | Target Improvement |
|--------|---------------------|-------------------|-------------------|
| Mean completion time (long tasks) | T_baseline | T_async | -20% to -30% |
| Concurrent tasks per dev | C_baseline | C_async | +50% to +100% |
| Async failure rate | N/A | F_async | <10% |
| Token reduction (context preservation) | 0 | ΔT_tokens | 40-60% |

### Failure Categories

**Hard Failures** (trigger kill-switch):
- Missing messages/logs required for understanding outcome
- Teleport URL not presented or not capturable
- Local logs missing or corrupted
- Conversation inconsistency affecting conclusions

**Soft Failures** (monitor but don't kill-switch):
- Confusing UI elements
- Minor context glitches requiring refresh
- Slow teleport page load

## p99 Survivability Test

**Requirement**: Run N≥5 long-running tasks (≥30 min each)

**Pass Criteria**: Zero hard failures across all test tasks

**Fail Criteria**: ≥1 hard failure → Trigger kill-switch

### Test Tasks

1. ShadowTag watermark analysis (synthetic clip)
2. Judge#6 log analysis (scrubbed data)
3. Smart contract security audit (test contract)
4. Autoresearch routing simulation (200 agents)
5. Code review (large refactor, no deploy)

## Kill-Switch Conditions

**IMMEDIATE DISABLE** if any of:

1. **Context Loss** - Message display bug hides critical conversation parts
2. **URL Failure** - Teleport URL not presented or not reproducibly capturable
3. **Log Corruption** - Local logs missing or corrupted for async run
4. **Inconsistency** - CLI output ≠ web conversation affecting conclusions

**Kill-Switch Response**:
1. Remove `&` from all SOP examples
2. Mark feature as "REFERENCE ONLY – DO NOT USE" in docs
3. Revert to standard CLI for all tasks
4. Escalate to engineering lead for Option 2/3 decision

## Security & Compliance

### GitHub Connection

- **Minimum Scope**: Connect only non-sensitive repos initially
- **No Regulated Data**: Never use async for HIPAA/SOC2/defense data
- **Teleport URL Security**: Treat URLs as bearer tokens - never log to public repos

### Local Logging Requirements

All async runs MUST:
1. Write input to `/var/log/pnkln/claude-async/`
2. Capture teleport URL in `async_manifest.jsonl`
3. Stream output via `tee` to local log file
4. Validate context completeness post-execution

## Revenue Experiments (Parallel Track)

These product experiments run independently of Claude's implementation:

### 1. ShadowTag Monitored Tier

- **Base**: $0.005/min "fire-and-forget" processing
- **Premium**: $0.01/min "monitored" with live status + logs
- **Target**: Close 1-2 customers at +$200-500 MRR within 4 weeks

### 2. Kernel Chain Async Batch

- **Sync**: $0.0003/decision, <35ms
- **Async Batch**: Same price with monitoring upsell
- **Target**: Validate 3+ serious leads needing bulk async work

### 3. Judge#6 Governance Replay

- **Feature**: Full audit trail with timeline + search
- **Pricing**: $500+/month for regulated clients
- **Target**: 2-3 discovery interviews to validate willingness-to-pay

## Next Actions

### Setup (1-2 hours)

1. Connect Pnkln GitHub repos to Claude Code web (non-sensitive only)
2. Create `scripts/claude_async.sh` wrapper
3. Initialize logging directories:
   ```bash
   mkdir -p /var/log/pnkln/claude-async
   touch /var/log/pnkln/async_manifest.jsonl
   ```

### Trial Execution (2-4 hours)

1. Run 5-10 test tasks using wrapper
2. Validate teleport URLs and context preservation
3. Measure metrics vs baseline
4. Check for kill-switch conditions

### Decision Gate (End of 7 days)

- **KEEP**: If pass criteria met, continue for non-critical tasks
- **NARROW**: If soft failures only, restrict to specific use cases
- **DISABLE**: If kill-switch triggered, revert to Option 2

## Fallback Strategies

### Option 2: Hold + Monitor

- No use of `&` for Pnkln work
- Weekly check of Anthropic release notes for bug fixes
- Standard CLI + GCP-native async only

### Option 3: Build GCP-Native Teleport

- Only if Option 1 proves conceptually valuable but fails p99
- Design: GCS job storage + Cloud Run viewer
- Timeline: 1-2 days implementation when greenlit

## Approval

**Trial Phase Approved By**: [Engineering Lead]
**Date**: 2025-11-22
**Review Date**: 2025-11-29 (7 days)

---

**CRITICAL**: This is a TRIAL. Strict adherence to allowed/forbidden use cases is mandatory. Any violation or kill-switch trigger requires immediate escalation.
