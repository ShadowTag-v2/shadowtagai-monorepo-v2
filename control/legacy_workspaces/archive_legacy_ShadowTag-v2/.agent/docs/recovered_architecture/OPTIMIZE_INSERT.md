# OPTIMIZE INSERT — "Doing Less, Better Results" Filter

Use for: Refactoring, performance optimization, scope reduction

---

## Prioritization Framework

### Core Principle

> "The right amount of complexity is the minimum needed for the current task."

---

## 1. Work Tasks Filter

### High-Value Actions (Keep)

| Task | Value Created | Time Required | Priority |
|------|---------------|---------------|----------|
| | | | 1 |
| | | | 2 |
| | | | 3 |

### Low-Value Actions (Eliminate/Delegate)

| Task | Why Low Value | Action |
|------|---------------|--------|
| | | Eliminate / Delegate |

---

## 2. Code Complexity Audit

### Current State


- **Lines of Code**: [Count]

- **Cyclomatic Complexity**: [Score]

- **Dependencies**: [Count]

### Reduction Targets


- [ ] Remove unused imports

- [ ] Delete dead code

- [ ] Inline single-use functions

- [ ] Remove premature abstractions

- [ ] Eliminate feature flags for shipped features

### Anti-Patterns to Remove


- [ ] Over-engineered factory patterns

- [ ] Unnecessary interface layers

- [ ] Redundant error handling

- [ ] Defensive copies where unnecessary

- [ ] Comments that restate code

---

## 3. Energy Protection

### High-Impact Work

[What moves the needle most?]

### Energy Drains to Eliminate

| Drain | Why It's a Drain | Resolution |
|-------|------------------|------------|
| | | |

### "No" List

Things explicitly NOT doing in this thread:

1.
2. 3. ---

## 4. Resource Optimization

### Current Spend

| Resource | Current Usage | Target | Savings |
|----------|---------------|--------|---------|
| API calls | | | |
| Compute | | | |
| Memory | | | |

### Three Cuts


1. **Cut 1**: [Unnecessary expense to eliminate]

2. **Cut 2**: [Unnecessary expense to eliminate]

3. **Cut 3**: [Unnecessary expense to eliminate]

---

## 5. Learning Focus

### One Skill to Master

**Skill**: [Single skill that aligns with goal]
**Why**: [How it helps this optimization]
**Outcome**: [Measurable result]

### Defer Until Later


- [ ] [Nice-to-have feature]

- [ ] [Future enhancement]

- [ ] [Separate concern]

---

## 6. Success Metrics

### Before State

| Metric | Value |
|--------|-------|
| Response time | |
| Memory usage | |
| Code lines | |
| Test coverage | |

### After State (Target)

| Metric | Target | Achieved |
|--------|--------|----------|
| Response time | | |
| Memory usage | | |
| Code lines | | |
| Test coverage | | |

### Validation


- [ ] Performance benchmarks pass

- [ ] All tests green

- [ ] No regressions

- [ ] Cleaner than before

---

## "Three Lines Better Than Abstraction" Checklist

Before creating a new function/class/module:

- [ ] Will this be used more than once?

- [ ] Is the abstraction obvious and intuitive?

- [ ] Does it reduce total code complexity?

If any answer is "No", write inline code instead.
