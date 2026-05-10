# Subagent-Driven Development

## When to Use

Use subagents for fast iteration on well-defined tasks with quality gates:
- Implementing features with clear requirements
- Refactoring with comprehensive tests
- Generating boilerplate code
- Exploring multiple approaches
- Parallel independent work

## The Pattern

**Fast execution + Quality gates = Speed with safety**

```
Main Agent (You):
├─ Define task clearly
├─ Set quality criteria
├─ Launch subagent(s)
├─ Verify results
└─ Integrate or iterate
```

## Core Principles

### 1. Clear Task Definition

**Subagents need crystal-clear instructions.**

```markdown
❌ BAD: "Add user feature"

✅ GOOD:
"Implement user registration endpoint:
- POST /api/users
- Accept: email, password
- Validate: email format, password length
- Return: user object or error
- Tests: valid input, invalid email, weak password
- Files: app/api/routes/users.py, tests/api/test_users.py"
```

### 2. Quality Gates

**Define what "done" means before starting.**

```markdown
Quality Gates for Subagent Work:
[ ] All specified tests pass
[ ] Code follows project style
[ ] No linter errors
[ ] Documentation present
[ ] Edge cases handled
[ ] No security issues
```

### 3. Verify, Don't Trust

**Always verify subagent output.**

```
Verification Checklist:
[ ] Run the tests yourself
[ ] Review the code
[ ] Check for edge cases
[ ] Verify matches requirements
[ ] Test manually
[ ] Check for security issues
```

## Workflow

### Step 1: Break Down the Work

```markdown
Feature: User Management System

Break down into subagent tasks:

Task 1: User Model
- Create User model
- Database migration
- Model tests
- DONE WHEN: Tests pass, migration works

Task 2: Registration API
- POST /api/users endpoint
- Input validation
- Password hashing
- API tests
- DONE WHEN: Tests pass, validation works

Task 3: Login API
- POST /api/login endpoint
- Authentication logic
- JWT token generation
- API tests
- DONE WHEN: Tests pass, auth works

Task 4: Integration
- Integration tests
- Error handling
- Documentation
- DONE WHEN: Full flow works end-to-end
```

### Step 2: Create Detailed Instructions

```markdown
# Subagent Task: User Registration API

## Objective
Implement user registration endpoint with validation and security.

## Requirements

### Endpoint
- Route: POST /api/users
- Input: JSON with email, password
- Output: User object (without password) or error

### Validation
- Email: Must be valid format, unique
- Password: Min 8 chars, must contain number and special char

### Security
- Hash password with bcrypt
- Never return password hash
- Rate limit: 5 requests per minute per IP

### Files to Create/Modify
- Create: app/api/routes/users.py
- Create: tests/api/test_users.py
- Modify: app/api/__init__.py (register routes)

## Success Criteria
- [ ] Endpoint exists and responds
- [ ] Valid input creates user successfully
- [ ] Invalid email returns 400 with clear message
- [ ] Weak password returns 400 with clear message
- [ ] Duplicate email returns 409
- [ ] Password is hashed (never stored plain)
- [ ] Response doesn't include password hash
- [ ] All tests pass (at least 5 test cases)
- [ ] No linter errors

## Expected Time
30-45 minutes

## Dependencies
- User model (already exists)
- bcrypt library (already installed)

## Notes
- Follow existing API patterns in app/api/routes/
- Use existing error handling patterns
- See tests/api/test_auth.py for test examples
```

### Step 3: Launch Subagent

```
Dispatch subagent with detailed instructions
→ Subagent works autonomously
→ Returns results when complete
```

### Step 4: Verify Results

```markdown
## Verification Report

Task: User Registration API
Subagent: Completed ✓

### Automated Checks
- [x] Tests pass (6/6)
- [x] No linter errors
- [x] Type checking passes

### Code Review
- [x] Code quality: Good
- [x] Follows project patterns: Yes
- [x] Security: Password hashing ✓
- [x] Validation: All cases covered ✓
- [x] Error handling: Proper messages ✓

### Manual Testing
- [x] Valid registration works
- [x] Invalid email rejected
- [x] Weak password rejected
- [x] Duplicate email rejected
- [x] Response excludes password hash

### Issues Found
None

Status: APPROVED for integration
```

### Step 5: Integrate or Iterate

```
If verification passes:
  → Integrate the work
  → Move to next task

If issues found:
  → Create refined task for subagent
  → Re-run with corrections
  → Verify again
```

## Iteration Pattern

### Fast Iteration Loop

```
Attempt 1:
Main: "Create user registration endpoint"
Sub: [implements]
Main: "Tests fail - password validation too weak"

Attempt 2:
Main: "Fix password validation: require number and special char"
Sub: [fixes]
Main: "Good! Tests pass. But missing rate limiting"

Attempt 3:
Main: "Add rate limiting: 5 requests/min per IP"
Sub: [adds]
Main: "Perfect! All quality gates passed"
```

### When to Iterate vs. Fix Yourself

```
Iterate (use subagent again) when:
✅ Issue is clear and discrete
✅ You have time for another iteration
✅ Good learning opportunity for patterns

Fix yourself when:
✅ Tiny change (< 5 lines)
✅ You know exact fix
✅ Faster to do it yourself
```

## Parallel Subagents

### Independent Tasks

```markdown
Launch 3 subagents in parallel:

Subagent A: User Registration API
Subagent B: User Login API
Subagent C: Password Reset API

All independent - no dependencies
→ Complete in parallel
→ Verify each independently
→ Integrate all together
```

### Sequential Dependencies

```markdown
Sequential tasks:

Task 1: User Model
  ↓ (wait for completion)
Task 2: Registration API (needs User model)
  ↓ (wait for completion)
Task 3: Login API (needs Registration)
  ↓ (wait for completion)
Task 4: Integration Tests (needs all)
```

## Quality Gates Detail

### Code Quality Gate

```python
# Check before accepting subagent work

def verify_code_quality(files):
    """Verify code meets quality standards"""

    # Run linter
    result = run_linter(files)
    assert result.errors == 0, f"Linter errors: {result.errors}"

    # Check test coverage
    coverage = get_coverage(files)
    assert coverage >= 80, f"Coverage too low: {coverage}%"

    # Run type checker
    type_result = run_type_checker(files)
    assert type_result.errors == 0, f"Type errors: {type_result.errors}"

    return True
```

### Security Gate

```
Security Checklist:
[ ] No SQL injection vulnerabilities
[ ] No XSS vulnerabilities
[ ] Passwords are hashed, never plain text
[ ] Authentication required where needed
[ ] Authorization checks present
[ ] Input validation on all endpoints
[ ] No secrets in code
[ ] HTTPS enforced for sensitive data
```

### Testing Gate

```
Testing Checklist:
[ ] Happy path tested
[ ] Error cases tested
[ ] Edge cases tested
[ ] Invalid input tested
[ ] Boundary values tested
[ ] Integration points tested
[ ] All tests pass
[ ] Tests are meaningful (not just for coverage)
```

## Examples

### Example 1: CRUD API

```markdown
Main Task: Create Books CRUD API

Break down for subagents:

Subagent 1: Book Model
- Create Book model (title, author, ISBN, year)
- Database migration
- Model tests

Subagent 2: List & Get Endpoints
- GET /api/books (list all)
- GET /api/books/:id (get one)
- Tests for both

Subagent 3: Create & Update Endpoints
- POST /api/books (create)
- PUT /api/books/:id (update)
- Tests for both

Subagent 4: Delete Endpoint
- DELETE /api/books/:id
- Soft delete vs hard delete
- Tests

Integration: Main Agent
- Review all subagent work
- Integration tests
- Manual testing
- Documentation
```

### Example 2: Refactoring

```markdown
Task: Refactor user service to use repository pattern

Subagent 1: Create Repository Interface
- Define IUserRepository interface
- Document methods
- Unit tests for interface compliance

Subagent 2: Implement Database Repository
- Implement DatabaseUserRepository
- All CRUD operations
- Tests using test database

Subagent 3: Implement Cache Repository
- Implement CacheUserRepository (decorator)
- Cache-aside pattern
- Tests with mock cache

Subagent 4: Update User Service
- Inject repository dependency
- Update all methods
- Ensure tests still pass

Integration: Main Agent
- Verify all repositories work
- Test switching repositories
- Performance testing
- Update documentation
```

## Tips for Success

### 1. Start Small

```
❌ DON'T: "Build entire user management system"
✅ DO: "Create user registration endpoint" (iterate)
```

### 2. Be Specific

```
❌ VAGUE: "Make it better"
✅ SPECIFIC: "Add validation for email format using regex pattern X"
```

### 3. Provide Examples

```markdown
"Create tests following this pattern:

def test_create_user_with_valid_data():
    response = client.post('/api/users', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!'
    })
    assert response.status_code == 201
    assert 'id' in response.json()

Create similar tests for:
- Invalid email
- Weak password
- Duplicate email"
```

### 4. Set Clear Boundaries

```markdown
"Work ONLY on these files:
- app/services/user_service.py
- tests/test_user_service.py

DO NOT modify:
- Database schema
- API endpoints
- Other services"
```

### 5. Define Done Clearly

```markdown
"Task is complete when:
✓ All 5 test cases pass
✓ Coverage > 90% for user_service.py
✓ No linter warnings
✓ Docstrings on all public methods
✓ No breaking changes to API"
```

## Common Pitfalls

### ❌ Pitfall 1: Vague Instructions

```
Bad: "Add user stuff"
Result: Subagent confused, wrong implementation

Fix: Detailed requirements with examples
```

### ❌ Pitfall 2: No Quality Gates

```
Bad: Accept subagent work without review
Result: Low quality code in codebase

Fix: Always verify against quality gates
```

### ❌ Pitfall 3: Too Much at Once

```
Bad: "Build entire authentication system"
Result: Complexity explosion, hard to verify

Fix: Break into 5-10 smaller tasks
```

### ❌ Pitfall 4: No Verification

```
Bad: Trust tests pass without running them
Result: Broken code merged

Fix: Always run tests yourself
```

## Benefits

### Speed
```
Without subagents: 8 hours for 4 features
With subagents (parallel): 3 hours for 4 features
Speedup: 2.7x
```

### Quality
```
With quality gates:
- All code reviewed
- All tests verified
- Consistent patterns
- Security checked
```

### Learning
```
Review subagent solutions:
- Learn new patterns
- See different approaches
- Identify improvements
```

## Remember

- **Clear instructions** = Better results
- **Quality gates** = Consistent quality
- **Verify always** = Catch issues early
- **Iterate fast** = Rapid improvement
- **Parallel when possible** = Maximum speed

**Subagents amplify your productivity, but you remain responsible for quality.**
