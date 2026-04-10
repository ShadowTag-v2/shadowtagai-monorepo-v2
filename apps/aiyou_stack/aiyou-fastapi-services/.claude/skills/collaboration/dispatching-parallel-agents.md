# Dispatching Parallel Agents

## When to Use

Use when you have multiple independent tasks that can be executed concurrently:
- Testing multiple components simultaneously
- Researching different approaches in parallel
- Implementing independent features
- Gathering information from multiple sources

## The Principle

**Independent tasks should run in parallel, not sequentially.**

Instead of:
```
Task A → Task B → Task C (3 hours sequential)
```

Do:
```
Task A ↘
Task B → All complete (1 hour parallel)
Task C ↗
```

## When Tasks Are Independent

Tasks are independent when:
- ✅ Don't share state or files
- ✅ Don't depend on each other's output
- ✅ Can be verified separately
- ✅ Failures don't cascade

Tasks are NOT independent when:
- ❌ One needs output from another
- ❌ They modify the same files
- ❌ They share mutable state
- ❌ Order matters for correctness

## Dispatching Pattern

### 1. Identify Independent Tasks

```
Feature: Add user authentication

Task Analysis:
- Create User model → Independent ✓
- Create Auth service → Independent ✓
- Create Login UI → Depends on Auth service ✗
- Write tests → Depends on implementation ✗

Parallel Batch 1:
- Agent A: Create User model
- Agent B: Create Auth service

Sequential Batch 2 (after Batch 1):
- Create Login UI (uses Auth service)
- Write integration tests
```

### 2. Create Clear Agent Instructions

Each agent needs:
- **Clear goal**: What to accomplish
- **Scope**: What files to touch
- **Success criteria**: How to verify completion
- **Report format**: What to return

```markdown
# Agent A Instructions

## Goal
Create User model with authentication fields

## Scope
- Create: models/user.py
- Update: models/__init__.py
- Do NOT touch: Any auth logic (Agent B's job)

## Requirements
- Email field (unique)
- Password hash field
- Created/updated timestamps
- is_active boolean

## Success Criteria
- [ ] User model created
- [ ] Fields include: email, password_hash, is_active, created_at, updated_at
- [ ] Migration file created
- [ ] Basic model tests passing

## Report Back
Provide:
1. File paths created/modified
2. Test results
3. Any issues encountered
```

### 3. Launch Agents in Parallel

```python
# Conceptual example
agents = [
    Agent(name="User Model", instructions=user_model_instructions),
    Agent(name="Auth Service", instructions=auth_service_instructions),
    Agent(name="Password Utils", instructions=password_utils_instructions),
]

# Launch all at once
results = await asyncio.gather(*[agent.run() for agent in agents])

# Process results
for result in results:
    print(f"{result.name}: {result.status}")
```

### 4. Collect and Verify Results

After parallel execution:

```markdown
# Results Collection

## Agent A: User Model ✅
Created:
- models/user.py
- migrations/001_create_users.sql
- tests/test_user_model.py

Tests: 5/5 passing
Issues: None

## Agent B: Auth Service ✅
Created:
- services/auth_service.py
- tests/test_auth_service.py

Tests: 8/8 passing
Issues: None

## Agent C: Password Utils ✅
Created:
- utils/password.py
- tests/test_password.py

Tests: 6/6 passing
Issues: None

## Integration Verification
- [ ] All files compile together
- [ ] No import conflicts
- [ ] Combined tests pass (19/19)
- [ ] No duplicate code
```

## Real-World Examples

### Example 1: Multi-Component Testing

```markdown
# Parallel Testing Strategy

Independent test suites:

Agent 1: Backend API Tests
- Run: pytest tests/api/
- Report: Pass/fail + coverage

Agent 2: Frontend Unit Tests
- Run: npm test -- --coverage
- Report: Pass/fail + coverage

Agent 3: Database Migration Tests
- Run: pytest tests/migrations/
- Report: Pass/fail + any warnings

Agent 4: E2E Tests
- Run: playwright test
- Report: Pass/fail + screenshots if failed

Result: All 4 test suites run in parallel
Time: ~5 minutes (vs. ~20 minutes sequential)
```

### Example 2: Research Tasks

```markdown
# Research: Choose database for new project

Independent research tasks:

Agent 1: PostgreSQL Research
Investigate:
- Performance characteristics
- Scalability
- Cost
- Ecosystem

Agent 2: MongoDB Research
Investigate:
- Performance characteristics
- Scalability
- Cost
- Ecosystem

Agent 3: DynamoDB Research
Investigate:
- Performance characteristics
- Scalability
- Cost
- Ecosystem

Result: Parallel research reports in ~30 min
(vs. ~90 min sequential)
```

### Example 3: Codebase Analysis

```markdown
# Codebase Audit

Independent analysis tasks:

Agent 1: Security Audit
- Check for SQL injection vulnerabilities
- Check for XSS vulnerabilities
- Check authentication/authorization
Report: Security findings

Agent 2: Performance Analysis
- Identify N+1 queries
- Find slow algorithms
- Check caching opportunities
Report: Performance findings

Agent 3: Code Quality Review
- Check test coverage
- Find code duplication
- Check complexity metrics
Report: Quality findings

Agent 4: Dependency Audit
- Check for outdated packages
- Check for security vulnerabilities
- Check for unused dependencies
Report: Dependency findings

Result: Complete audit in parallel
```

## Synchronization Points

Sometimes you need to wait for all agents before proceeding:

```
Phase 1: Parallel Implementation
├─ Agent A: Feature A
├─ Agent B: Feature B
└─ Agent C: Feature C

SYNC POINT: All agents complete

Phase 2: Integration
└─ Single agent: Integrate A + B + C

SYNC POINT: Integration complete

Phase 3: Parallel Testing
├─ Agent A: Test Feature A
├─ Agent B: Test Feature B
└─ Agent C: Test Feature C

SYNC POINT: All tests pass

Phase 4: Deployment
└─ Single agent: Deploy all features
```

## Avoiding Common Pitfalls

### Pitfall 1: File Conflicts

```markdown
❌ BAD: Both agents modify same file
Agent A: Modify user_service.py (add login)
Agent B: Modify user_service.py (add registration)
Result: Merge conflict

✅ GOOD: Separate files or coordinate
Agent A: Create login_service.py
Agent B: Create registration_service.py
Result: No conflicts
```

### Pitfall 2: Shared State

```markdown
❌ BAD: Both agents use same test database
Agent A: Runs tests (creates test users)
Agent B: Runs tests (expects empty DB)
Result: Test failures

✅ GOOD: Isolated environments
Agent A: Uses test_db_1
Agent B: Uses test_db_2
Result: No interference
```

### Pitfall 3: Hidden Dependencies

```markdown
❌ BAD: Agent B secretly depends on Agent A
Agent A: Create User model
Agent B: Create Order service (needs User model)
Agent B: Fails because User not ready yet

✅ GOOD: Explicit dependencies
Batch 1:
- Agent A: Create User model

Batch 2 (after Batch 1):
- Agent B: Create Order service (uses User)
```

## Agent Communication Protocol

### Agent Report Template

```markdown
# Agent Report: [Agent Name]

## Status
- [ ] In Progress
- [x] Complete
- [ ] Blocked

## Completed Tasks
- [x] Created models/user.py
- [x] Added tests
- [x] All tests passing

## Files Created/Modified
- Created: models/user.py (150 lines)
- Modified: models/__init__.py (1 line)
- Created: tests/test_user_model.py (80 lines)

## Test Results
- Tests run: 5
- Tests passed: 5
- Coverage: 95%

## Issues Encountered
None

## Blockers
None

## Dependencies for Next Steps
User model ready for use by:
- Login service
- Registration service
- Password reset service

## Notes
Used bcrypt for password hashing (industry standard)
```

## Orchestration Strategies

### Strategy 1: Fire and Forget

```
Launch all agents → Wait for all → Verify results
```

Good for: Independent tasks with no coordination needs

### Strategy 2: Wave Pattern

```
Wave 1: Launch agents A, B, C → Wait
Wave 2: Launch agents D, E (use results from Wave 1) → Wait
Wave 3: Launch agent F (integrates all) → Wait
```

Good for: Tasks with dependency chains

### Strategy 3: Pipeline Pattern

```
Agent A → Agent B → Agent C
  ↓         ↓         ↓
Output  → Input   → Output
```

Good for: Data transformation pipelines

### Strategy 4: Map-Reduce Pattern

```
Map Phase (parallel):
Agent 1: Process chunk 1
Agent 2: Process chunk 2
Agent 3: Process chunk 3

Reduce Phase (sequential):
Agent: Combine all results
```

Good for: Large data processing

## Benefits

### Time Savings

```
Sequential:
Task A (1h) + Task B (1h) + Task C (1h) = 3 hours

Parallel:
max(Task A (1h), Task B (1h), Task C (1h)) = 1 hour

Savings: 2 hours (67% faster)
```

### Better Resource Utilization

```
Sequential: Uses 1 CPU/thread at a time
Parallel: Uses multiple CPUs/threads
Result: Better hardware utilization
```

### Faster Feedback

```
Sequential: Wait 3 hours to know if C works
Parallel: Know in 1 hour if any task fails
Result: Faster iteration
```

## When NOT to Use Parallel Agents

Don't use parallel agents when:
- ❌ Tasks have dependencies on each other
- ❌ Tasks modify the same files
- ❌ Order of execution matters
- ❌ Tasks are very quick (overhead not worth it)
- ❌ Debugging is needed (parallel makes debugging harder)

## Checklist

Before dispatching parallel agents:

- [ ] Tasks are truly independent
- [ ] Each agent has clear scope
- [ ] No file conflicts possible
- [ ] Each agent has isolated environment if needed
- [ ] Success criteria defined for each agent
- [ ] Plan for collecting and integrating results
- [ ] Synchronization points identified

## Remember

- **Parallel = faster**, but only for independent tasks
- **Clear boundaries** prevent conflicts
- **Explicit sync points** coordinate work
- **Verify integration** after parallel work completes

**Dispatch wisely, synchronize carefully, integrate thoroughly.**
