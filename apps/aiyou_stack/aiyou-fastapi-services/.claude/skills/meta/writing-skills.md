# Writing Skills

## When to Use

When you want to create a new skill for the Superpowers Skills System. Use this guide to write high-quality, reusable skills.

## Skill Anatomy

Every skill should have these sections:

```markdown
# Skill Name

## When to Use
[Clear criteria for when this skill should be activated]

## [Main Content Sections]
[The actual skill content]

## [Examples]
[Concrete examples of the skill in action]

## [Anti-Patterns]
[What NOT to do]

## Remember
[Key takeaways]
```

## Writing Process

### Step 1: Identify the Pattern

```
Ask yourself:
- What recurring workflow am I documenting?
- When should this skill activate?
- What problem does it solve?
- Who will use this skill?

Example:
- Workflow: Writing tests before implementation
- Activates: When implementing features
- Solves: Code without tests, poor design
- Users: All developers
```

### Step 2: Define Clear Triggers

**"When to Use" section must be crystal clear.**

```markdown
❌ BAD:
## When to Use
Use this when writing code.

✅ GOOD:
## When to Use
**ALWAYS** when implementing new features, fixing bugs, or refactoring code. TDD is mandatory, not optional.

Use when:
- Starting a new feature (3+ steps)
- Fixing a bug that needs a reproduction test
- Refactoring code with existing tests
```

### Step 3: Structure the Content

```markdown
# Skill Name

## When to Use
[Clear activation criteria]

## Core Principles
[3-5 fundamental rules]

## Process / Workflow
[Step-by-step guide]

## Examples
[Concrete, realistic examples]

## Common Patterns
[Reusable patterns]

## Anti-Patterns
[What NOT to do, with examples]

## Checklist
[Quick reference checklist]

## Remember
[3-5 key takeaways]
```

### Step 4: Add Concrete Examples

**Examples make skills actionable.**

```markdown
❌ BAD:
Write tests for your code.

✅ GOOD:
```python
# Example: Testing user creation
def test_user_creation():
    """User should be created with email and password"""
    user = create_user(email="redacted@shadowtag-v4.local", password="pass123")
    assert user.id is not None
    assert user.email == "redacted@shadowtag-v4.local"
    assert user.is_active is True
```
```

### Step 5: Document Anti-Patterns

**Show what NOT to do and why.**

```markdown
## Anti-Patterns

### ❌ Writing Implementation First
```python
# WRONG: Writing the function first
def create_user(email, password):
    # ... implementation

# Then writing test after
def test_create_user():
    # ...
```

**Why this is bad:**
- Misses design feedback from writing test first
- May not be testable
- No RED phase to verify test can fail

**Fix:**
Write the test first, watch it fail, then implement.
```

### Step 6: Create Actionable Checklists

```markdown
## Quick Checklist

Before saying "Done":
- [ ] Reproduction case now passes
- [ ] All tests pass
- [ ] No regressions
- [ ] Tested in staging/production-like environment
- [ ] Edge cases tested
- [ ] Documentation updated
- [ ] Code is clean and reviewed
```

## Content Guidelines

### 1. Be Specific

```markdown
❌ VAGUE:
Make your code better.

✅ SPECIFIC:
Refactor functions longer than 50 lines into smaller, focused functions.
Each function should do one thing.
```

### 2. Show, Don't Just Tell

```markdown
❌ TELLING:
Use descriptive variable names.

✅ SHOWING:
```python
# ❌ BAD
def f(x, y):
    z = x * y
    return z

# ✅ GOOD
def calculate_total_price(quantity, unit_price):
    total_price = quantity * unit_price
    return total_price
```
```

### 3. Explain the "Why"

```markdown
❌ NO WHY:
Always write tests.

✅ WITH WHY:
Always write tests because:
1. Tests prove your code works
2. Tests prevent regressions
3. Tests document expected behavior
4. Tests enable confident refactoring
```

### 4. Provide Context

```markdown
❌ NO CONTEXT:
Use the factory pattern.

✅ WITH CONTEXT:
Use the factory pattern when:
- You have multiple related classes to instantiate
- Creation logic is complex
- You need to decouple creation from usage

Don't use factory pattern when:
- You only have 1-2 simple classes
- Creation is trivial
- YAGNI applies
```

## Skill Categories

### Testing Skills
Focus on: Test writing, test patterns, test quality
Example: TDD, testing anti-patterns, async testing

### Debugging Skills
Focus on: Finding bugs, fixing bugs, preventing bugs
Example: Systematic debugging, root cause analysis

### Collaboration Skills
Focus on: Team workflows, communication, planning
Example: Code reviews, git workflows, planning

### Meta Skills
Focus on: Skills about skills, skill usage, skill creation
Example: This skill (writing-skills), sharing-skills

## Testing Your Skill

### Checklist for a Good Skill

```markdown
- [ ] Clear "When to Use" section
- [ ] Concrete examples (at least 2-3)
- [ ] Anti-patterns documented
- [ ] Actionable steps/checklist
- [ ] Real-world scenarios
- [ ] Code examples (if applicable)
- [ ] Proper markdown formatting
- [ ] Concise but comprehensive
- [ ] Follows naming conventions
- [ ] No typos or grammar errors
```

### Get Feedback

```markdown
1. Read the skill aloud - does it make sense?
2. Would a beginner understand it?
3. Can someone follow it step-by-step?
4. Are examples realistic?
5. Is anything unclear or ambiguous?
```

## Naming Conventions

### Skill File Names

```
# Use kebab-case
test-driven-development.md  ✓
systematic-debugging.md     ✓
writing-plans.md           ✓

# NOT
TestDrivenDevelopment.md   ✗
test_driven_development.md ✗
tdd.md                     ✗ (not descriptive)
```

### Skill Titles

```markdown
# Use Title Case, be descriptive
# Test-Driven Development     ✓
# Systematic Debugging         ✓
# Writing Plans                ✓

# NOT
# TDD                          ✗ (abbreviation)
# how to write tests           ✗ (not title case)
```

## Example Skill Outline

```markdown
# [Skill Name]

## When to Use

[When should this skill activate? Be specific.]

- Use when [scenario 1]
- Use when [scenario 2]
- Use when [scenario 3]

## Core Principles

1. **Principle 1** - [Explanation]
2. **Principle 2** - [Explanation]
3. **Principle 3** - [Explanation]

## Process

### Step 1: [Step Name]

[Description of step]

```[language]
[Code example if applicable]
```

### Step 2: [Step Name]

[Description of step]

### Step 3: [Step Name]

[Description of step]

## Examples

### Example 1: [Scenario]

```[language]
[Complete, realistic example]
```

**Explanation:**
[Why this example works]

### Example 2: [Scenario]

```[language]
[Another example]
```

## Common Patterns

### Pattern 1: [Pattern Name]

[Description and example]

### Pattern 2: [Pattern Name]

[Description and example]

## Anti-Patterns

### ❌ Anti-Pattern 1: [Name]

```[language]
[Example of what NOT to do]
```

**Why this is bad:**
[Explanation]

**Fix:**
[How to do it correctly]

### ❌ Anti-Pattern 2: [Name]

[Same structure]

## Checklist

Quick reference for applying this skill:

- [ ] [Checkable item 1]
- [ ] [Checkable item 2]
- [ ] [Checkable item 3]
- [ ] [Checkable item 4]

## Remember

- **Key point 1** - [Brief explanation]
- **Key point 2** - [Brief explanation]
- **Key point 3** - [Brief explanation]

[Memorable closing statement]
```

## Formatting Guidelines

### Code Blocks

```markdown
# Always specify language
```python
def example():
    pass
```

```bash
git commit -m "message"
```

```javascript
const example = () => {};
```
```

### Emphasis

```markdown
**Bold** for important terms
*Italic* for emphasis
`code` for inline code
```

### Lists

```markdown
# Use consistent list formatting
- Unordered list item
- Another item

1. Ordered list item
2. Another item

# Use checkboxes for checklists
- [ ] Todo item
- [x] Done item
```

### Headers

```markdown
# Skill Title (H1 - only once)
## Major Section (H2)
### Subsection (H3)
#### Minor Point (H4 - sparingly)
```

## File Organization

```
.claude/skills/
├── testing/
│   ├── test-driven-development.md
│   ├── condition-based-waiting.md
│   └── testing-anti-patterns.md
├── debugging/
│   ├── systematic-debugging.md
│   └── root-cause-tracing.md
├── collaboration/
│   ├── brainstorming.md
│   └── writing-plans.md
└── meta/
    ├── writing-skills.md          ← This file
    └── using-superpowers.md
```

## Remember

- **Clear triggers** - When should this skill activate?
- **Concrete examples** - Show, don't just tell
- **Anti-patterns** - Document what NOT to do
- **Actionable** - Provide checklists and steps
- **Tested** - Get feedback before publishing

**Good skills are: clear, actionable, well-documented, and battle-tested.**
