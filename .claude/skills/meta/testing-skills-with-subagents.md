# Testing Skills with Subagents

## When to Use

Before sharing a skill or after creating a new skill, test it with subagents to verify it's clear, actionable, and effective.

## Why Test Skills?

**Skills should work, not just look good.**

```
Untested skill:
- Might have unclear instructions
- Examples might not work
- Steps might be missing
- Anti-patterns might be wrong

Tested skill:
- Proven to work
- Clear and actionable
- Examples are realistic
- Catches edge cases
```

## Testing Methods

### Method 1: Task-Based Testing

**Give a subagent a task and see if the skill helps.**

```markdown
# Setup
Skill: test-driven-development.md
Task: Implement user registration with TDD

# Test Process
1. Give subagent the task
2. Provide the TDD skill
3. Observe if subagent follows the skill
4. Check if result matches skill expectations

# Success Criteria
- Subagent writes test first (RED)
- Subagent implements minimal code (GREEN)
- Subagent refactors (REFACTOR)
- Final code has tests
- Tests actually test behavior
```

### Method 2: Skill Application Testing

**Ask a subagent to apply the skill to a scenario.**

```markdown
# Setup
Skill: systematic-debugging.md
Scenario: Bug report with failing test

# Test Process
1. Provide bug scenario
2. Provide systematic debugging skill
3. Ask subagent to debug using the skill
4. Verify subagent follows the process

# Success Criteria
- Subagent follows 4-phase process
- Reproduces the problem (REPRODUCE)
- Isolates root cause (ISOLATE)
- Verifies understanding (VERIFY)
- Applies correct fix (FIX)
```

### Method 3: Comprehension Testing

**Ask a subagent to explain the skill back to you.**

```markdown
# Setup
Skill: condition-based-waiting.md

# Test Process
1. Provide the skill to subagent
2. Ask: "Explain when and how to use this skill"
3. Ask: "What are the key anti-patterns?"
4. Ask: "Give me an example from the skill"

# Success Criteria
- Subagent correctly explains purpose
- Subagent identifies key principles
- Subagent recognizes anti-patterns
- Subagent can provide examples
```

## Testing Workflow

### Step 1: Prepare Test Scenario

```markdown
## Test Scenario Template

Skill Being Tested: [skill-name]

Scenario: [Realistic task that requires the skill]

Setup:
- [What's already in place]
- [What's the starting state]

Task:
- [What the subagent should do]

Expected Outcome:
- [What should result from following the skill]

Success Metrics:
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]
```

### Step 2: Run the Test

```markdown
# Subagent Instructions

You are testing a skill: [skill-name]

Here is the skill:
[Include full skill content]

Here is your task:
[Task description]

Follow the skill step-by-step.
Report back:
1. What steps you took
2. What worked well
3. What was unclear
4. What you would improve
```

### Step 3: Evaluate Results

```markdown
## Evaluation Checklist

Clarity:
- [ ] Instructions were clear
- [ ] Examples were helpful
- [ ] No ambiguous steps
- [ ] Process was logical

Effectiveness:
- [ ] Skill helped complete task
- [ ] Result matches expectations
- [ ] No major gaps in guidance
- [ ] Anti-patterns were useful

Completeness:
- [ ] All necessary steps included
- [ ] Edge cases covered
- [ ] Checklist was sufficient
- [ ] Examples were realistic
```

### Step 4: Iterate on Feedback

```markdown
Based on subagent feedback:

Issues Found:
1. [Issue description]
   - Fix: [How you'll improve]

2. [Issue description]
   - Fix: [How you'll improve]

Unclear Sections:
1. [Section name]
   - Improve: [How you'll clarify]

Missing Information:
1. [What was missing]
   - Add: [What you'll add]
```

## Example Test Sessions

### Example 1: Testing TDD Skill

```markdown
## Test Setup

Skill: test-driven-development.md
Task: Implement a function that validates email addresses

## Instructions to Subagent

"You need to implement an email validation function.
Follow the test-driven-development skill attached.

Task: Create is_valid_email(email: str) -> bool

Requirements:
- Returns True for valid emails
- Returns False for invalid emails
- Valid: Contains @ and domain
- Invalid: Missing @, spaces, invalid chars

Use TDD as described in the skill."

## Subagent Response

"Following TDD skill:

### RED Phase
```python
def test_valid_email():
    assert is_valid_email('test@example.com') is True

def test_invalid_email_no_at():
    assert is_valid_email('testexample.com') is False
```

Running tests: FAIL (is_valid_email not defined) ✓

### GREEN Phase
```python
def is_valid_email(email: str) -> bool:
    return '@' in email and '.' in email
```

Running tests: PASS ✓

### REFACTOR Phase
```python
import re

def is_valid_email(email: str) -> bool:
    \"\"\"Validate email format\"\"\"
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

Running tests: PASS ✓"

## Evaluation

✅ Followed RED-GREEN-REFACTOR cycle
✅ Wrote test first
✅ Made test fail correctly
✅ Implemented minimal code
✅ Refactored for quality

Result: Skill worked as intended ✓
```

### Example 2: Testing Debugging Skill

```markdown
## Test Setup

Skill: systematic-debugging.md
Bug: Login fails with uppercase emails

## Instructions to Subagent

"There's a bug: users can't login if they use uppercase letters in their email.

Code:
```python
def create_user(email, password):
    user = User(email=email.lower())
    db.save(user)

def login(email, password):
    user = db.get_user(email=email)  # Not lowercased!
    return verify_password(user, password)
```

Follow systematic-debugging skill to find and fix this bug."

## Subagent Response

"Following systematic-debugging skill:

### Phase 1: REPRODUCE
Test case:
```python
def test_login_bug():
    create_user('Test@Example.com', 'pass')
    result = login('Test@Example.com', 'pass')
    assert result is True  # FAILS ✓
```

Bug reproduced ✓

### Phase 2: ISOLATE
Checking create_user:
- email.lower() → stored as 'test@example.com' ✓

Checking login:
- db.get_user(email=email) → searches for 'Test@Example.com'
- Database has 'test@example.com'
- No match!

ROOT CAUSE: Login doesn't normalize email ✓

### Phase 3: VERIFY
Hypothesis: login needs email.lower()

Test:
```python
# Stored: 'test@example.com'
db.get_user('test@example.com')  → Found ✓
db.get_user('Test@Example.com')  → Not found ✓
```

Hypothesis confirmed ✓

### Phase 4: FIX
```python
def login(email, password):
    email = email.lower()  # Normalize like create_user
    user = db.get_user(email=email)
    return verify_password(user, password)
```

Test now passes ✓"

## Evaluation

✅ Followed 4-phase process
✅ Reproduced the problem
✅ Isolated root cause
✅ Verified understanding
✅ Applied correct fix

Result: Skill worked perfectly ✓
```

## Common Test Scenarios

### For Testing Skills

```markdown
Scenario 1: TDD Skill
- Implement new feature from scratch
- Must write tests first

Scenario 2: Testing Anti-Patterns Skill
- Review existing tests
- Identify anti-patterns
- Suggest improvements

Scenario 3: Condition-Based Waiting Skill
- Write tests for async operation
- Must use waiting, not sleep
```

### For Debugging Skills

```markdown
Scenario 1: Systematic Debugging
- Provide bug report
- Subagent debugs using skill

Scenario 2: Root Cause Tracing
- Provide symptom
- Subagent traces to root cause

Scenario 3: Verification Before Completion
- Subagent claims bug fixed
- Must verify per checklist
```

### For Collaboration Skills

```markdown
Scenario 1: Writing Plans
- Give complex feature requirement
- Subagent creates plan using skill

Scenario 2: Brainstorming
- Give design problem
- Subagent brainstorms using skill

Scenario 3: Code Review
- Provide PR to review
- Subagent reviews using skill
```

## Measuring Skill Quality

### Quantitative Metrics

```markdown
Success Rate:
- X/Y subagents successfully applied skill
- Target: >80%

Clarity Score:
- Questions asked / skill length
- Lower is better

Completion Rate:
- Tasks completed correctly
- Target: 100%

Time to Complete:
- Average time to apply skill
- Compared to without skill
```

### Qualitative Feedback

```markdown
Ask subagents:
- What was clear?
- What was confusing?
- What was missing?
- What would you improve?
- Would you use this skill again?
```

## Iteration Based on Testing

```markdown
Testing Cycle:

1. Write skill v1
   ↓
2. Test with subagent
   ↓
3. Collect feedback
   ↓
4. Identify issues
   ↓
5. Improve skill → v2
   ↓
6. Test again
   ↓
7. Repeat until quality threshold met
```

## Quality Thresholds

```markdown
Before sharing, skill should achieve:

- [ ] 80%+ success rate in tests
- [ ] 0 major confusion points
- [ ] 100% task completion rate
- [ ] Positive feedback from subagents
- [ ] All examples work as shown
- [ ] Anti-patterns are accurate
- [ ] Checklist is complete
```

## Test Documentation

```markdown
## Test Report Template

Skill: [skill-name]
Version: [version]
Date: [date]

### Test Scenarios
1. [Scenario 1]: [Result]
2. [Scenario 2]: [Result]
3. [Scenario 3]: [Result]

### Success Metrics
- Completion Rate: X/Y (Z%)
- Average Time: N minutes
- Clarity Score: N questions

### Feedback Summary
**What Worked:**
- [Point 1]
- [Point 2]

**What Needs Improvement:**
- [Point 1]
- [Point 2]

### Changes Made
- [Change 1]
- [Change 2]

### Ready to Share?
- [ ] Yes
- [ ] No - needs more iteration
```

## Remember

- **Test before sharing** - Don't share untested skills
- **Use real scenarios** - Test with realistic tasks
- **Iterate based on feedback** - Improve continuously
- **Multiple tests better** - Test different scenarios
- **Document results** - Track what works and what doesn't

**Tested skills are trusted skills.**
