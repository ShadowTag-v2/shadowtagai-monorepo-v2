# [Feature Name] - Context Log

**Feature:** [Feature Name]
**Started:** [Date]
**Last Updated:** [Date]

## Purpose

This document serves as a running log of important decisions, discoveries, and contextual information gathered during the implementation of [Feature Name]. It acts as a "transaction log" for the development session, capturing the reasoning behind changes.

---

## Architectural Decisions

### Decision 1: [Title]

**Date:** [Date]
**Made By:** [AI/Human/Pair]

**Context:**
[What prompted this decision? What problem were we solving?]

**Decision:**
[What was decided?]

**Rationale:**
[Why was this approach chosen over alternatives?]

**Alternatives Considered:**

1. [Alternative 1] - Rejected because [reason]
2. [Alternative 2] - Rejected because [reason]

**Impact:**

- Files affected: `[file1.py]`, `[file2.py]`
- Other components impacted: [List]
- Technical debt introduced: [None/Description]

**References:**

- Code: `[file.py:123]`
- Documentation: [Link]

---

### Decision 2: [Title]

**Date:** [Date]
**Made By:** [AI/Human/Pair]

**Context:**
[Description]

**Decision:**
[Description]

**Rationale:**
[Description]

**Impact:**
[Description]

---

## Key Discoveries

### Discovery 1: [Title]

**Date:** [Date]

**What We Found:**
[Description of what was discovered during implementation]

**Why It Matters:**
[Impact on the current feature or future work]

**Action Taken:**
[How we adapted the plan or implementation]

**Source:**

- File: `[path/to/file.py:line]`
- Documentation: [Link if applicable]

**Example:**

```python
# Code snippet if relevant
```

---

### Discovery 2: [Title]

**Date:** [Date]

**What We Found:**
[Description]

**Why It Matters:**
[Impact]

**Action Taken:**
[Response]

---

## Implementation Notes

### Phase 1 Notes

**Date Range:** [Start] - [End]

**Completed Tasks:**

- [Task 1] - Completed [date]
- [Task 2] - Completed [date]

**Key Implementation Details:**

- [Detail 1]: Implemented in `[file.py]` using [approach]

**Challenges Encountered:**

1. **[Challenge 1]**
   - Problem: [Description]
   - Solution: [How it was resolved]
   - Time spent: [Estimate]

2. **[Challenge 2]**
   - Problem: [Description]
   - Solution: [Resolution]

**Code Patterns Established:**

```python
# Pattern 1: [Description]
# Example from [file.py]

def example_pattern():
    """This pattern is used for [purpose]."""
    pass
```

---

### Phase 2 Notes

**Date Range:** [Start] - [End]

**Completed Tasks:**
[List]

**Key Implementation Details:**
[Details]

**Challenges Encountered:**
[List]

---

## File Change Log

### New Files Created

| File              | Purpose   | Phase   | Date   |
| ----------------- | --------- | ------- | ------ |
| `[path/file.py]`  | [Purpose] | Phase 1 | [Date] |
| `[path/other.py]` | [Purpose] | Phase 2 | [Date] |

### Existing Files Modified

| File              | Changes Made  | Reason   | Date   |
| ----------------- | ------------- | -------- | ------ |
| `[path/file.py]`  | [Description] | [Reason] | [Date] |
| `[path/other.py]` | [Description] | [Reason] | [Date] |

### Important Code Locations

| Description           | Location         | Notes     |
| --------------------- | ---------------- | --------- |
| [Feature entry point] | `[file.py:line]` | [Context] |
| [Core logic]          | `[file.py:line]` | [Context] |
| [Validation function] | `[file.py:line]` | [Context] |
| [Error handling]      | `[file.py:line]` | [Context] |

---

## Dependencies and Integrations

### External Libraries Added

| Library        | Version | Purpose   | Installation            |
| -------------- | ------- | --------- | ----------------------- |
| [package-name] | [x.y.z] | [Purpose] | `pip install [package]` |

**Configuration Required:**

```python
# Example configuration in [file]
CONFIG = {
    "key": "value"
}
```

### API Integrations

#### Integration 1: [Service Name]

**Purpose:** [Why we're integrating]

**Endpoint Used:** `[URL/pattern]`

**Authentication:** [Method]

**Implementation:** `[file.py:line]`

**Notes:**

- [Important detail 1]
- [Important detail 2]

---

## Testing Insights

### Test Coverage

**Current Coverage:** [XX%]

**Areas Well Tested:**

- [Component 1] - [Coverage %]
- [Component 2] - [Coverage %]

**Areas Needing More Tests:**

- [ ] [Component/scenario needing tests]
- [ ] [Another area]

### Test Failures and Resolutions

#### Failure 1: [Test Name]

**Date:** [Date]

**Symptom:**
[What was failing]

**Root Cause:**
[Why it was failing]

**Resolution:**
[How it was fixed]

**Commit:** [commit hash if relevant]

---

## Performance Observations

### Benchmarks

| Operation     | Time (ms) | Target (ms) | Status   |
| ------------- | --------- | ----------- | -------- |
| [Operation 1] | [actual]  | [target]    | ✅/⚠️/❌ |
| [Operation 2] | [actual]  | [target]    | ✅/⚠️/❌ |

**Bottlenecks Identified:**

- [Bottleneck 1]: [Description] - [Mitigation strategy]

**Optimizations Applied:**

1. [Optimization 1] - [Impact]
2. [Optimization 2] - [Impact]

---

## Security Considerations

### Security Measures Implemented

- [ ] Input validation on [endpoints/functions]
- [ ] Authentication required for [operations]
- [ ] Authorization checks in [locations]
- [ ] Rate limiting on [endpoints]
- [ ] Data sanitization in [locations]

### Security Reviews

**Date:** [Date]
**Reviewer:** [AI/Human]
**Findings:**

- [Finding 1] - [Status: Addressed/Pending]
- [Finding 2] - [Status]

---

## Technical Debt Tracking

### Debt Introduced

1. **[Debt Item 1]**
   - **Location:** `[file.py:line]`
   - **Reason:** [Why this debt was taken on]
   - **Repayment Plan:** [When/how to address]
   - **Priority:** [High/Medium/Low]

2. **[Debt Item 2]**
   - **Location:** [Where]
   - **Reason:** [Why]
   - **Repayment Plan:** [Plan]

### Debt Repaid

1. **[Resolved Debt Item]**
   - **Was:** [Description of debt]
   - **Resolved:** [Date]
   - **How:** [What was done]

---

## Questions and Answers

### Resolved Questions

**Q1:** [Question that came up during development]
**A1:** [Answer/Resolution]
**Date Resolved:** [Date]
**Impact:** [How this affected implementation]

---

**Q2:** [Question]
**A2:** [Answer]
**Date Resolved:** [Date]

---

### Open Questions

**Q1:** [Question that needs resolution]
**Context:** [Why this matters]
**Blocking:** [Yes/No - is this blocking progress?]
**Assigned To:** [Who should answer this]

---

## Session Checkpoints

### Checkpoint 1: [Date/Time]

**Work Completed:**

- [Summary of work done]

**Current State:**

- Files modified: [count]
- Tests passing: [count/total]
- Phase progress: [X of Y tasks complete]

**Next Steps:**

- [ ] [Next immediate task]
- [ ] [Following task]

**Context for Resume:**
[Notes to help resume work after a break - what to remember, where you left off]

---

### Checkpoint 2: [Date/Time]

**Work Completed:**
[Summary]

**Current State:**
[Status]

**Next Steps:**
[Tasks]

---

## Lessons Learned

### What Worked Well

1. [Practice/approach that was effective]
   - Why: [Reason]
   - Reuse: [How to apply in future]

2. [Another success]

### What Could Be Improved

1. [Area for improvement]
   - Issue: [What happened]
   - Better approach: [What to do next time]

2. [Another improvement area]

### Patterns to Reuse

```python
# Pattern 1: [Name]
# Use case: [When to use this]
# Benefits: [Why it's good]

def reusable_pattern():
    """Example of pattern worth repeating."""
    pass
```

---

## References and Resources

### Documentation Consulted

- [Doc 1]: [Link] - [What we learned]
- [Doc 2]: [Link] - [Relevance]

### Similar Implementations

- [Reference implementation]: [Link] - [How it helped]

### Stack Overflow / Forums

- [Question/Answer]: [Link] - [What it solved]

---

## Integration Points

### Upstream Dependencies

[What this feature depends on from other components]

- **[Component A]:** [How we use it]
  - Contact: [file/module]
  - Assumptions: [What we assume about it]

### Downstream Dependents

[What other components will depend on this feature]

- **[Component B]:** [How it will use this feature]
  - Contract: [API/interface we're providing]
  - Stability: [How stable is our interface]

---

## Environment and Configuration

### Environment Variables Added/Modified

```bash
# .env changes
NEW_CONFIG_VAR=value  # Purpose: [description]
UPDATED_VAR=new_value  # Changed from [old_value], reason: [why]
```

### Configuration Files Modified

- `[config_file.json]`:

  ```json
  {
    "new_setting": "value"
  }
  ```

  Purpose: [Why this was added]

---

## Deployment Notes

### Pre-Deployment Checklist

- [ ] Database migrations created
- [ ] Environment variables documented
- [ ] Dependencies added to requirements.txt
- [ ] Tests passing
- [ ] Documentation updated

### Deployment Steps

1. [Step 1]
2. [Step 2]

### Post-Deployment Verification

- [ ] [Check 1]
- [ ] [Check 2]

### Rollback Procedure

1. [Rollback step 1]
2. [Rollback step 2]

---

## Collaboration Notes

### Pair Programming Sessions

**Session 1:** [Date]

- **Participants:** [AI + Human]
- **Focus:** [What was worked on]
- **Outcomes:** [What was accomplished]
- **Decisions Made:** [Key decisions]

### Code Review Feedback

**Reviewer:** [Name/AI]
**Date:** [Date]

**Feedback:**

1. [Feedback item 1] - [Status: Addressed/Pending]
2. [Feedback item 2] - [Status]

**Changes Made:**

- [Change based on review]

---

## Raw Notes and Observations

[This section is for quick, unstructured notes during development]

- [Timestamp]: [Quick note about something observed]
- [Timestamp]: [Idea for future improvement]
- [Timestamp]: [Reminder about edge case]

---

**Last Updated:** [Date and Time]
**Updated By:** [AI/Human]
**Next Update Scheduled:** [Before next context compaction / end of session]
