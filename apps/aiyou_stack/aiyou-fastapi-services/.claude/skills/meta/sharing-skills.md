# Sharing Skills

## When to Use

When you've created a useful skill and want to share it back with the community via a branch and pull request.

## Why Share Skills?

**Your skills can help others:**
- Codify your expertise
- Help others avoid mistakes you made
- Improve software quality across projects
- Build collective knowledge
- Get feedback to improve the skill

## Sharing Process

### Step 1: Ensure Quality

**Before sharing, verify the skill meets quality standards.**

```markdown
Quality Checklist:
- [ ] Clear "When to Use" section
- [ ] Concrete, realistic examples
- [ ] Anti-patterns documented
- [ ] Actionable steps/checklist
- [ ] Tested with at least one real use case
- [ ] No typos or grammar errors
- [ ] Properly formatted markdown
- [ ] Follows naming conventions
```

### Step 2: Test the Skill

**Test the skill yourself or with a subagent.**

```markdown
Testing Checklist:
- [ ] Read it aloud - does it make sense?
- [ ] Would a beginner understand it?
- [ ] Can someone follow it step-by-step?
- [ ] Are examples realistic and complete?
- [ ] Have you used this skill successfully?
- [ ] Did it help solve the problem?
```

### Step 3: Create a Descriptive Branch

```bash
# Branch naming: skill/<category>/<skill-name>
git checkout -b skill/testing/integration-testing
git checkout -b skill/debugging/performance-profiling
git checkout -b skill/collaboration/pair-programming

# Or if improving existing skill:
git checkout -b improve/testing/tdd-examples
```

### Step 4: Write a Clear Commit Message

```bash
git add .claude/skills/testing/integration-testing.md

git commit -m "Add integration testing skill

This skill provides guidance on writing integration tests:
- When to write integration vs unit tests
- Setting up test environments
- Common integration testing patterns
- Anti-patterns to avoid

Use case: Tested while building API integration tests for user service.
Helped reduce test brittleness and improve coverage."
```

### Step 5: Create a Pull Request

```markdown
# PR Title
Add [Category]/[Skill Name] skill

# PR Description
## Summary
This skill provides guidance on [what the skill covers].

## Why This Skill?
I created this skill because [problem it solves].

## What's Included
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Testing
- [x] Used this skill successfully in [project/scenario]
- [x] Examples are realistic and tested
- [x] Follows skill writing guidelines
- [x] No typos or formatting issues

## Use Cases
This skill helped me:
1. [Use case 1]
2. [Use case 2]

## Feedback Welcome
Particularly interested in feedback on:
- [Area 1]
- [Area 2]
```

### Step 6: Respond to Feedback

```markdown
When reviewers provide feedback:

✓ Thank them for taking time to review
✓ Address all comments
✓ Make requested changes
✓ Ask questions if unclear
✓ Update the PR when ready

See: receiving-code-review skill
```

## What Makes a Shareable Skill?

### Must Have

```markdown
✓ Clear activation criteria (When to Use)
✓ Step-by-step process
✓ Real, tested examples
✓ Anti-patterns section
✓ Proper markdown formatting
✓ No sensitive/proprietary information
```

### Nice to Have

```markdown
✓ Multiple examples
✓ Checklists
✓ Diagrams (if helpful)
✓ Links to additional resources
✓ Your experience using the skill
✓ Common variations/alternatives
```

### Should NOT Have

```markdown
✗ Company-specific details
✗ Proprietary code
✗ Sensitive information
✗ Personal opinions as fact
✗ Untested advice
✗ Unclear or vague guidance
```

## Skill Categories Worth Sharing

### High Value

```
Testing Skills:
- Novel testing patterns
- Domain-specific testing strategies
- Testing anti-patterns you discovered

Debugging Skills:
- Systematic debugging approaches
- Tool usage guides
- Problem-solving frameworks

Collaboration Skills:
- Team workflows
- Communication patterns
- Planning techniques

Performance Skills:
- Optimization strategies
- Profiling techniques
- Scaling patterns

Security Skills:
- Security checklists
- Vulnerability patterns
- Secure coding practices
```

### Lower Priority (But Still Useful)

```
- Language-specific idioms
- Framework-specific patterns
- Tool configurations
- Environment setups
```

## Example: Skill Sharing Workflow

```bash
# 1. Create the skill
cd .claude/skills/testing
# Write integration-testing.md

# 2. Test it
# Use the skill while working on a feature
# Refine based on actual usage

# 3. Create branch
git checkout -b skill/testing/integration-testing

# 4. Commit
git add .claude/skills/testing/integration-testing.md
git commit -m "Add integration testing skill

Provides systematic approach to integration testing:
- When to use integration vs unit tests
- Test environment setup
- Common patterns
- Anti-patterns

Tested on: User API integration tests project"

# 5. Push
git push origin skill/testing/integration-testing

# 6. Create PR
gh pr create --title "Add testing/integration-testing skill" \
  --body "$(cat <<EOF
## Summary
Adds guidance on writing effective integration tests.

## Why
I found myself repeatedly explaining integration testing best practices
to team members. This skill codifies that knowledge.

## What's Included
- Clear definition of integration vs unit tests
- When to write each type
- Setup patterns for test environments
- Common pitfalls and how to avoid them

## Testing
Used successfully on 3 projects:
1. User API integration tests
2. Payment service integration tests
3. Notification system tests

## Examples
All examples are from real projects (anonymized).

## Feedback
Particularly interested in feedback on the test environment setup section.
EOF
)"

# 7. Respond to reviews
# Address feedback, update as needed

# 8. After merge
git checkout main
git pull origin main
git branch -d skill/testing/integration-testing
```

## Maintaining Skills

### When to Update

```markdown
Update a skill when:
- You find a better approach
- You discover new anti-patterns
- Examples become outdated
- Feedback suggests improvements
- New tools/techniques emerge
```

### Update Process

```bash
# Create improvement branch
git checkout -b improve/testing/tdd-async-examples

# Make improvements
# Edit .claude/skills/testing/test-driven-development.md

# Commit
git commit -m "Improve TDD skill: add async/await examples

Added section on testing async code:
- Async test patterns
- Common pitfalls with async tests
- Real examples from recent project"

# Create PR
gh pr create --title "Improve TDD skill with async examples"
```

## Community Guidelines

### Be Collaborative

```markdown
✓ Welcome feedback and suggestions
✓ Give credit to others' ideas
✓ Build on existing skills
✓ Help improve others' skills through review
```

### Be Professional

```markdown
✓ Use respectful language
✓ Focus on code and patterns, not people
✓ Provide constructive criticism
✓ Be open to different approaches
```

### Be Honest

```markdown
✓ Share what actually works
✓ Admit when you're not sure
✓ Acknowledge limitations
✓ Don't oversell or exaggerate
```

## Skill Licensing

```markdown
When sharing skills:
- Skills should be freely usable
- Give credit where due
- Don't include proprietary information
- Acknowledge sources/inspirations
```

## Recognition

```markdown
Contributing skills:
- Helps the community
- Demonstrates expertise
- Builds your reputation
- Creates learning opportunities
- Improves software quality

Your contributions matter!
```

## Getting Started

```markdown
Start small:
1. Share one skill you use regularly
2. Get feedback
3. Iterate based on feedback
4. Share another skill
5. Help review others' skills

Every skill shared is valuable!
```

## Remember

- **Test first** - Use the skill yourself before sharing
- **Clear examples** - Real, tested, concrete examples
- **Welcome feedback** - Be open to improvements
- **Iterate** - Skills get better over time
- **Give back** - Share what you've learned

**Shared knowledge makes everyone better.**
