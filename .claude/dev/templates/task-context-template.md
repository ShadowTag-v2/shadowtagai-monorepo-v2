# [Task Name] - Context

**Last Updated**: [Date/Time]
**Current Phase**: [Phase name from plan]
**Status**: [Active/Blocked/Paused/Completed]

---

## Quick Reference

### Current Working Directory
```
/path/to/working/directory
```

### Active Branch
```
git-branch-name
```

### Key Commands
```bash
# Development
uv run uvicorn main:app --reload

# Testing
uv run pytest --cov --cov-fail-under=98

# Build
uv run build-command
```

---

## State Machine Context

```yaml
workflow: [task-workflow-name]
current_agent: [current-agent-name or "developer"]
phase: [phase-1/phase-2/phase-3]
state: [started/in-progress/testing/review/completed]
```

### State History
- [Timestamp]: [state] → [new-state] | [Agent/Developer] | [Brief reason]
- [Timestamp]: [state] → [new-state] | [Agent/Developer] | [Brief reason]

---

## Current Focus

### What We're Building Right Now
[1-2 sentence description of current immediate work]

### Next Immediate Steps
1. [Very next action]
2. [Action after that]
3. [Action after that]

---

## Key Files

### Modified This Session
- `path/to/file1.py` - [What changed, why]
- `path/to/file2.py` - [What changed, why]
- `path/to/test_file.py` - [Tests added/modified]

### Critical Dependencies
- `path/to/dependency1.py` - [Why it matters]
- `path/to/dependency2.py` - [Why it matters]

### Configuration Files
- `pyproject.toml` - [Dependencies, uv config]
- `pytest.ini` - [Test configuration]
- `.env.example` - [Environment variables]

---

## Important Decisions Made

### Decision 1: [Date]
**What**: [Decision title]
**Why**: [Rationale]
**Impact**: [How this affects implementation]

### Decision 2: [Date]
**What**: [Decision title]
**Why**: [Rationale]
**Impact**: [How this affects implementation]

---

## Technical Context

### Architecture Overview
```
[ASCII diagram or description of current architecture]

Example:
┌─────────────┐      ┌──────────────┐      ┌────────────┐
│   FastAPI   │─────→│   Service    │─────→│  BigQuery  │
│   Routes    │      │   Layer      │      │            │
└─────────────┘      └──────────────┘      └────────────┘
```

### Data Models
```python
# Key data structures
class ModelName(BaseModel):
    field1: str
    field2: int
```

### Database Schema
```sql
-- Relevant tables/changes
CREATE TABLE ...
```

---

## Dependencies & Environment

### UV Lock Hash
```
[First 12 chars of uv.lock hash for reproducibility]
```

### Key Dependencies
```toml
[tool.uv.dependencies]
fastapi = "^0.104.0"
google-cloud-aiplatform = "^1.38.0"
pytest = "^7.4.0"
```

### Environment Variables Required
- `GOOGLE_CLOUD_PROJECT`: [Purpose]
- `VERTEX_AI_LOCATION`: [Purpose]
- `DATABASE_URL`: [Purpose]

---

## Known Issues & Blockers

### Active Blockers
1. **[Blocker 1 Title]**
   - Description: [What's blocking]
   - Impact: [What can't proceed]
   - Resolution: [How to unblock]
   - Status: [Open/In Progress/Resolved]

### Known Bugs
1. **[Bug 1 Title]**
   - Symptom: [What happens]
   - Root Cause: [If known]
   - Workaround: [If available]
   - Priority: [H/M/L]

---

## Testing Status

### Coverage Metrics
- **Current**: [X%]
- **Target**: 98%
- **Delta**: [+/-X%]

### Test Files
- `tests/test_feature1.py` - [Status: ✅/🚧/❌]
- `tests/test_feature2.py` - [Status: ✅/🚧/❌]

### Manual Testing Checklist
- [ ] [Manual test scenario 1]
- [ ] [Manual test scenario 2]
- [ ] [Manual test scenario 3]

---

## Integration Points

### External APIs
- **Vertex AI**: [How we use it, endpoints]
- **BigQuery**: [Datasets, tables accessed]

### Internal Services
- **Service 1**: [How we integrate]
- **Service 2**: [How we integrate]

---

## Performance Notes

### Benchmarks
- [Operation 1]: [X ms/s]
- [Operation 2]: [X ms/s]

### Optimization Opportunities
- [Area 1]: [Potential improvement]
- [Area 2]: [Potential improvement]

---

## Agent Handoff Protocol

### Current Agent Output
[When an agent completes work, it updates this section]

**Agent**: [agent-name]
**Completed**: [Date/Time]
**Work Done**: [Summary of agent's work]
**Files Modified**: [List]
**Tests Added**: [List]
**Status**: [Success/Partial/Failed]

### Next Agent
**Agent**: [next-agent-name]
**Inputs Required**:
- [Input 1]
- [Input 2]

**Task**: [What the next agent should do]

**Context**: [Specific context the next agent needs]

---

## Context Reset Preparation

### Before Compaction, Capture:
- [Important info 1 that would otherwise be lost]
- [Important info 2 that would otherwise be lost]

### To Resume After Reset:
1. Read this context file
2. Read [task-name]-plan.md for strategy
3. Read [task-name]-tasks.md for completion status
4. Continue from "Next Immediate Steps" section above

---

## Notes & Observations

### What's Working Well
- [Observation 1]
- [Observation 2]

### What's Challenging
- [Challenge 1]
- [Challenge 2]

### Lessons Learned
- [Lesson 1]
- [Lesson 2]

---

## Quick Links

- Plan: [task-name]-plan.md
- Tasks: [task-name]-tasks.md
- Results: [task-name]-results.md (if applicable)
- Related PRs: [Links]
- Related Issues: [Links]
