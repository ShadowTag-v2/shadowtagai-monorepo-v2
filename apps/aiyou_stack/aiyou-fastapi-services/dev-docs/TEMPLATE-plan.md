# [Feature Name] - Implementation Plan

**Created:** [Date]
**Status:** Planning
**Estimated Effort:** [Hours/Days]

## Executive Summary

[2-3 paragraph overview of what this feature does, why it's needed, and the high-level approach]

## Goals and Success Criteria

### Primary Goals

- [ ] [Measurable goal 1]
- [ ] [Measurable goal 2]
- [ ] [Measurable goal 3]

### Success Metrics

- [ ] [Specific success criterion with measurement]
- [ ] [Example: "All API endpoints return responses in <200ms"]
- [ ] [Example: "Test coverage ≥80%"]

## Architecture Overview

### System Components Affected

- **[Component 1]:** [How it's affected]
- **[Component 2]:** [How it's affected]

### New Components to Create

- **[New Component]:** [Purpose and responsibility]

### Data Flow

```
[User/Client] → [API Gateway] → [Service] → [Database]
                     ↓
              [Other Services]
```

### Technology Decisions

| Technology | Purpose    | Justification |
| ---------- | ---------- | ------------- |
| [Tech 1]   | [Use case] | [Why chosen]  |
| [Tech 2]   | [Use case] | [Why chosen]  |

## Implementation Phases

### Phase 1: [Phase Name] (Estimated: [Time])

**Objective:** [Clear, measurable objective for this phase]

**Tasks:**

1. [Specific task with file references]
   - Files to create: `[path/to/file.py]`
   - Files to modify: `[path/to/existing.py]`

2. [Another specific task]
   - Dependencies: [What must be done first]
   - Expected output: [What deliverable looks like]

**Validation:**

- [ ] [How to verify this phase is complete]
- [ ] [Tests that should pass]

### Phase 2: [Phase Name] (Estimated: [Time])

**Objective:** [Clear, measurable objective for this phase]

**Tasks:**

1. [Specific task]
2. [Another task]

**Validation:**

- [ ] [Validation criterion]

### Phase 3: [Phase Name] (Estimated: [Time])

**Objective:** [Clear, measurable objective for this phase]

**Tasks:**

1. [Specific task]

**Validation:**

- [ ] [Validation criterion]

## Detailed Design

### API Endpoints (if applicable)

#### Endpoint 1: [Method] /api/v1/[path]

**Request:**

```json
{
  "field1": "string",
  "field2": 123
}
```

**Response (200 OK):**

```json
{
  "id": "uuid",
  "status": "success",
  "data": {}
}
```

**Error Responses:**

- `400 Bad Request` - [When this occurs]
- `401 Unauthorized` - [When this occurs]
- `404 Not Found` - [When this occurs]

### Data Models

#### Model 1: [Name]

```python
class [ModelName](BaseModel):
    """[Description]"""
    field1: str = Field(..., description="[Purpose]")
    field2: int = Field(default=0, ge=0, description="[Purpose]")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
```

**Validation Rules:**

- [Rule 1]
- [Rule 2]

### Database Schema (if applicable)

#### Table: [table_name]

| Column     | Type      | Constraints   | Description           |
| ---------- | --------- | ------------- | --------------------- |
| id         | UUID      | PRIMARY KEY   | Unique identifier     |
| [column]   | [type]    | [constraints] | [description]         |
| created_at | TIMESTAMP | NOT NULL      | Creation timestamp    |
| updated_at | TIMESTAMP | NOT NULL      | Last update timestamp |

**Indexes:**

- `idx_[table]_[column]` on `[column]` (for [query type])

**Relationships:**

- Foreign key to `[other_table].[column]`

### Business Logic

**Key Algorithms:**

1. **[Algorithm Name]:**

   ```
   Input: [Description]
   Output: [Description]

   Steps:
   1. [Step 1]
   2. [Step 2]
   3. [Step 3]
   ```

**Validation Rules:**

- [Rule 1 with rationale]
- [Rule 2 with rationale]

**Edge Cases to Handle:**

- [Edge case 1] → [How to handle]
- [Edge case 2] → [How to handle]

## Dependencies and Prerequisites

### External Dependencies

- [ ] [Library/Package name] - [Version] - [Purpose]
- [ ] [Another dependency]

### Internal Dependencies

- [ ] [Feature/Component that must exist first]
- [ ] [Another internal dependency]

### Environment Requirements

- [ ] [Environment variable needed]
- [ ] [Database migration]
- [ ] [Configuration change]

## Testing Strategy

### Unit Tests

- [ ] Test [component] with [scenario]
- [ ] Test [error handling] for [edge case]
- [ ] Test [validation] for [invalid input]

**Location:** `tests/unit/test_[feature].py`

### Integration Tests

- [ ] Test full workflow: [description]
- [ ] Test interaction between [component A] and [component B]

**Location:** `tests/integration/test_[feature]_integration.py`

### End-to-End Tests

- [ ] Test complete user journey: [description]

**Location:** `tests/e2e/test_[feature]_e2e.py`

### Manual Testing Checklist

- [ ] [Manual test scenario 1]
- [ ] [Manual test scenario 2]
- [ ] Test with [specific data condition]

## Risk Analysis

### High Risk Items

#### Risk 1: [Description]

- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [Strategy to reduce risk]
- **Contingency:** [What to do if risk occurs]

#### Risk 2: [Description]

- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [Strategy]
- **Contingency:** [Backup plan]

### Technical Debt Considerations

- [Debt item 1] - [When to address]
- [Debt item 2] - [Tradeoff being made]

### Security Considerations

- [ ] [Security consideration 1]
- [ ] Input validation and sanitization
- [ ] Authentication and authorization
- [ ] Data encryption (at rest/in transit)
- [ ] Rate limiting and abuse prevention

## Performance Considerations

### Expected Load

- **Requests per second:** [Estimate]
- **Data volume:** [Estimate]
- **Concurrent users:** [Estimate]

### Performance Targets

- [ ] API response time: [target] ms (p95)
- [ ] Database query time: [target] ms (p95)
- [ ] Memory usage: < [target] MB

### Optimization Strategies

- [Strategy 1] - [When to apply]
- [Strategy 2] - [Expected benefit]

### Monitoring and Metrics

- [ ] Track [metric 1] with [tool]
- [ ] Alert on [condition]
- [ ] Dashboard showing [key metrics]

## Documentation Requirements

- [ ] API documentation (OpenAPI/Swagger)
- [ ] Update CLAUDE.md with [relevant info]
- [ ] Code documentation (docstrings)
- [ ] README updates for [component]
- [ ] Architecture diagram updates

## Rollout Plan

### Development

1. [Step 1]
2. [Step 2]

### Testing

1. [Testing phase description]
2. [QA validation]

### Deployment

1. [Deployment step 1]
2. [Deployment step 2]

### Rollback Plan

If issues occur:

1. [Rollback step 1]
2. [Rollback step 2]

## Open Questions

- [ ] **Q:** [Question 1]
  - **A:** [Answer once resolved, or "TBD"]

- [ ] **Q:** [Question 2]
  - **A:** [Answer once resolved]

## References

- [Related documentation link]
- [Design document reference]
- [External API documentation]
- [Architecture decision record (ADR)]

## Timeline

| Phase   | Start Date | End Date | Status  |
| ------- | ---------- | -------- | ------- |
| Phase 1 | [Date]     | [Date]   | Pending |
| Phase 2 | [Date]     | [Date]   | Pending |
| Phase 3 | [Date]     | [Date]   | Pending |

**Total Estimated Duration:** [X days/weeks]

---

## Notes

[Any additional notes, assumptions, or context that doesn't fit elsewhere]

---

**Plan Approved By:** [Name/Date]
**Last Updated:** [Date]
