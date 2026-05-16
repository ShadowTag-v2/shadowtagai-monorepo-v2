# TDD-GUARD DOCTRINE

## Purpose
Quality gate between Red→Green phases. Inspect-only, no modification.

## Compliance Rules

### Test Structure Rules
1. **MUST** have descriptive test names following pattern: `test_<action>_<expected_outcome>`
2. **MUST** include docstring explaining test purpose
3. **MUST** follow Arrange-Act-Assert pattern
4. **MUST** have single assertion per test (or logically grouped assertions)
5. **MUST NOT** contain implementation logic

### Integration-First Rules (80/20)
6. **SHOULD** prioritize integration tests over unit tests (80% integration, 20% unit)
7. **MUST** test actual behavior, not mocks
8. **SHOULD** cover happy path + primary edge cases

### Coverage Rules
9. **MUST** achieve 95%+ compliance score
10. **MUST** have explicit assertions (no empty tests)

## Validation Thresholds

```python
COMPLIANCE_THRESHOLD = 0.95  # 95% minimum
MAX_ITERATIONS = 3           # Retry limit before escalation
TIMEOUT_SECONDS = 90         # p99 ≤90s
FAIL_FAST_THRESHOLD = 10     # Max violations before early exit
```

## Violation Severities

- **CRITICAL**: Blocks progression (empty tests, no assertions)
- **MAJOR**: Must fix (bad naming, no docstring)
- **MINOR**: Should fix (style issues)

## Escalation Path

```
iterations > MAX_ITERATIONS → manual_review
violations > FAIL_FAST_THRESHOLD → early_exit
timeout > 90s → fail_fast
```
