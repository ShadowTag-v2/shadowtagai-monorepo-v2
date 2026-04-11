---
description: Improve code quality, extract functions, reduce duplication
---

# Refactor

I will help you refactor code to improve quality while preserving functionality.

## Guardrails
- Never change behavior, only structure
- Make small, incremental changes
- Ensure tests pass after each change
- Preserve public APIs unless explicitly asked
- For changes >300 LOC: run `compiler-guillotine` skill FIRST (Rule 39/40)
- Use `ast-grep` patterns for structural transforms over regex (Rule 40)

## Steps

### 1. Understand Scope
Ask clarifying questions:
- Which files or functions to refactor?
- What problems are you seeing? (duplication, complexity, etc.)
- Are there tests covering this code?
- Any constraints to be aware of?

### 2. Analyze Code
// turbo
Identify issues:
- Code duplication (search for similar patterns with grep/ast-grep)
- Long functions/methods (>50 lines)
- Deep nesting (>3 levels)
- Unclear naming
- Mixed responsibilities
- Dead code (use `vulture` for Python, `ts-prune` for TypeScript)

### 3. Plan Refactoring
Common patterns:
- **Extract Function**: Pull out reusable logic
- **Rename**: Improve clarity of names
- **Inline**: Remove unnecessary abstractions
- **Move**: Relocate to better location
- **Simplify Conditionals**: Reduce complexity
- **Replace Conditional with Polymorphism**: For type-switching code

### 4. Execute Refactoring
Make changes incrementally:
- One refactoring at a time
- Run tests after each change
- Commit frequently with `refactor(scope): description`

### 5. Verify
// turbo
- All tests still pass
- Code is more readable
- No behavior changes
- Run linter to catch style regressions

## Principles
- Refactor in small steps
- Make the change easy, then make the easy change
- If it hurts, do it more often
- Never refactor and add features in the same commit
