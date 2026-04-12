# Refactoring Plan Template

## SCOPE
- Files affected: [LIST]
- Services impacted: [LIST]
- Estimated SLA impact: [p50/p90/p99 changes]

## DEPENDENCY ORDER
1. [First change - why it must be first]
2. [Second change - depends on #1]
3. [etc.]

## ROLLBACK STRATEGY
- Checkpoint after step: [X]
- Rollback command: `kubectl rollout undo ...`
- SLA violation threshold: [p99 > Xms triggers rollback]

## TESTING CHECKLIST
☐ Unit tests pass
☐ Integration tests pass
☐ p99 ≤ target latency
☐ No memory leaks
☐ GPU utilization < 80%
