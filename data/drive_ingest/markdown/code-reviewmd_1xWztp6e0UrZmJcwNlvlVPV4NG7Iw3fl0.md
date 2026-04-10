# /code-review - Automated Code Quality Check

Runs comprehensive quality checks and generates review report.

## Usage

```
/code-review [file-or-directory]
```

If no path provided, reviews all changed files in current branch.

## What It Does

1. **Static Analysis**
   - `mypy` - Type checking
   - `ruff` - Linting and style
   - `bandit` - Security vulnerabilities (Python)
   - `slither` - Smart contract security (Solidity)

2. **Test Coverage**
   - `pytest --cov` - Code coverage report
   - Identifies untested code paths

3. **Complexity Analysis**
   - Cyclomatic complexity per function
   - Flags functions >10 complexity

4. **Best Practices**
   - Checks against active skills (backend-dev-guidelines, blockchain-dev-guidelines)
   - Verifies OPORD format for dev-docs
   - Validates Army Leadership Principles in agent code

## Example

```
/code-review contracts/tba/ShadowTagAccount.sol
```

Runs Slither, checks ERC-6551 compliance, generates security report.

## Output Format

```markdown
# Code Review Report

## Summary
- **Files Reviewed**: 5
- **Issues Found**: 12 (2 critical, 3 high, 5 medium, 2 low)
- **Test Coverage**: 87%
- **Recommendation**: FIX CRITICAL BEFORE MERGE

## Critical Issues

### [CRIT-001] Type Safety Violation
**File**: `src/ShadowTag-v2/services/reputation_service.py:42`
**Issue**: Missing type hint on return value
**Skill Violated**: backend-dev-guidelines (Type Safety section)
**Fix**:
\`\`\`python
async def get_reputation(self, address: str) -> int:  # Add return type
    ...
\`\`\`

## High Issues
[Similar format]

## Medium Issues
[Similar format]

## Test Coverage Gaps
- `src/ShadowTag-v2/services/reputation_service.py` - 65% coverage
  - Missing tests for error handling paths

## Complexity Warnings
- `calculate_royalties()` - Complexity 12 (threshold: 10)
  - Consider extracting helper functions

## Skill Compliance
✅ backend-dev-guidelines - 95% compliant
⚠️  blockchain-dev-guidelines - 2 security issues found
✅ agent-orchestration - OPORD format correct

## Recommendations
1. Fix 2 critical type safety issues
2. Add tests for error paths (target: 90% coverage)
3. Refactor `calculate_royalties()` to reduce complexity
4. Run Slither on smart contracts before deployment
```

## Integration

- Logs review results to Context Index
- Tags with "code-review", file paths, severity levels
- Blocks merge if critical issues found (BarExamProtocol gate)
- Notifies SwarmOrchestrator if agent assistance needed

## Background Execution (Teleport Feature)

For large codebases, run in background:

```bash
/code-review src/ &
```

This will:
1. Start review in background process
2. Generate teleport URL for monitoring
3. Preserve conversation context
4. Display results when complete

**Kill-Switch**: If message display bug loses context, revert to foreground execution.

## Best Practices

1. **Run before every PR** - Catch issues early
2. **Fix critical first** - Don't accumulate tech debt
3. **Track coverage trends** - Aim for 90%+
4. **Use with /dev-docs** - Review plan compliance