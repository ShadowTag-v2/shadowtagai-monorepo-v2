# Writing Plans: Detailed Implementation Plans

## When to Use

Use when:
- Starting a complex feature (3+ steps)
- Multiple files/components involved
- Need to coordinate changes
- Want to track progress systematically
- Working on unfamiliar codebase

## Plan Structure

A good plan has these sections:

### 1. Context

**What** are we building and **why**?

```markdown
## Context

Feature: Export user data to CSV
Why: Users need to analyze data in external tools
Current state: No export functionality exists
Goal: Allow users to download current page view as CSV
```

### 2. Requirements

**What** must the solution do?

```markdown
## Requirements

Functional:
- [ ] Export button in user list page
- [ ] Downloads CSV file with current page data
- [ ] Includes all visible columns
- [ ] Filename format: users-export-YYYY-MM-DD.csv
- [ ] Works for up to 1000 records

Non-functional:
- [ ] Response time < 2 seconds for 500 records
- [ ] Handles special characters in data (quotes, commas)
- [ ] Works in Chrome, Firefox, Safari

Out of scope:
- ❌ Export all pages (future feature)
- ❌ Custom column selection
- ❌ Excel format support
```

### 3. Technical Approach

**How** will we build it?

```markdown
## Technical Approach

### Architecture
- Backend: Add new endpoint `/api/users/export`
- Frontend: Add export button to UserList component
- Data flow: Frontend → API → CSV generation → File download

### Key Decisions
- Use Python's `csv` module for generation
- Stream response for better memory usage
- Generate on-demand (no background jobs for MVP)

### Dependencies
- Backend: csv module (stdlib)
- Frontend: No new dependencies
```

### 4. Implementation Steps

**What** to do, in **what order**?

```markdown
## Implementation Steps

### Backend

1. [ ] Create CSV service class
   - File: `app/services/csv_export.py`
   - Method: `generate_user_csv(users: List[User]) -> str`
   - Handles: Escaping, headers, data formatting

2. [ ] Add export endpoint
   - File: `app/api/routes/users.py`
   - Route: `GET /api/users/export`
   - Query params: Same as user list (filters, pagination)
   - Returns: CSV file with correct headers

3. [ ] Add tests
   - File: `tests/test_csv_export.py`
   - Test CSV generation with sample data
   - Test special characters handling
   - Test empty results

### Frontend

4. [ ] Add export button
   - File: `src/components/UserList.tsx`
   - Add button to toolbar
   - Icon: Download icon
   - Position: Next to search/filter controls

5. [ ] Implement download logic
   - File: `src/services/userService.ts`
   - Method: `exportUsers(filters)`
   - Triggers download with correct filename

6. [ ] Add loading state
   - Show spinner while generating
   - Disable button during export
   - Show error if export fails

### Testing

7. [ ] Manual testing checklist
   - [ ] Export with no filters
   - [ ] Export with filters applied
   - [ ] Export with sorting
   - [ ] Special characters in names
   - [ ] Large dataset (500+ records)
   - [ ] Empty result set

8. [ ] Integration test
   - File: `tests/integration/test_user_export.py`
   - Full flow: Request → CSV → Download
```

### 5. Dependencies and Risks

**What** could go wrong or block us?

```markdown
## Dependencies

- User list API must be working (already exists ✓)
- Need access to production-like data for testing
- CSV filename needs timestamp - ensure timezone handling

## Risks

Risk: Large datasets might timeout
Mitigation: Start with 1000 record limit, add pagination later

Risk: Special characters breaking CSV format
Mitigation: Use csv.writer with proper escaping

Risk: Different browsers handle downloads differently
Mitigation: Test in Chrome, Firefox, Safari before release
```

### 6. Testing Strategy

**How** will we verify it works?

```markdown
## Testing Strategy

### Unit Tests
- CSV generation with various data types
- Special character handling
- Empty data handling
- Header generation

### Integration Tests
- Full API endpoint test
- Download trigger from frontend

### Manual Tests
- UI/UX testing in different browsers
- Large dataset testing (500+ records)
- Edge cases (empty, special chars, long names)
```

### 7. Rollout Plan

**How** will we deploy and monitor?

```markdown
## Rollout Plan

### Phase 1: Development
- Implement on feature branch
- Test locally with sample data

### Phase 2: Staging
- Deploy to staging environment
- Test with production-like data
- QA review

### Phase 3: Production
- Deploy to production
- Monitor error rates
- Gather user feedback

### Monitoring
- Track export request count
- Monitor response times
- Alert on error rate > 5%
- Watch for timeouts

### Rollback Plan
- Feature flag: Can disable export button
- No database changes, safe to rollback
```

## Complete Example

```markdown
# Plan: User Data Export Feature

## Context
Users need to export their user list data to analyze in Excel or other tools.
Currently, they screenshot or manually copy-paste data, which is error-prone.

## Requirements

### Functional
- [ ] Export button visible on user list page
- [ ] Exports currently visible users (respects filters/search)
- [ ] CSV format with all visible columns
- [ ] Filename: users-export-YYYY-MM-DD-HHMMSS.csv
- [ ] Up to 1000 records per export

### Non-Functional
- [ ] Response time < 2 seconds for 500 records
- [ ] Properly escapes special characters
- [ ] Works in Chrome, Firefox, Safari

### Out of Scope
- Custom column selection (v2)
- Export all pages (v2)
- Scheduled exports (v2)
- Excel format (v2)

## Technical Approach

### Architecture
```
[User List Page] → [Export Button] → [API Request]
                                            ↓
                                    [Export Endpoint]
                                            ↓
                                    [CSV Service]
                                            ↓
                                    [File Download]
```

### Technology Choices
- **Backend**: Python csv module (stdlib, no dependencies)
- **Frontend**: Fetch API + Blob download
- **Format**: RFC 4180 compliant CSV

### Key Decisions
1. **Sync vs Async**: Synchronous for MVP (handles 1000 records fine)
2. **All data vs Current page**: Current page only (simpler, faster)
3. **Format**: CSV only (most requested format)

## Implementation Steps

### Step 1: Create CSV Service (Backend)
**File**: `app/services/csv_export.py`

```python
class CSVExportService:
    def generate_user_csv(self, users: List[User]) -> str:
        """Generate CSV from user list"""
        # Implementation details...
```

**Tests**: `tests/test_csv_export.py`
- Test with sample data
- Test special characters (quotes, commas, newlines)
- Test empty list
- Test unicode characters

**Estimate**: 1 hour

### Step 2: Add API Endpoint (Backend)
**File**: `app/api/routes/users.py`

```python
@router.get("/users/export")
def export_users(
    filters: UserFilters = Depends(),
    db: Session = Depends(get_db)
):
    # Get filtered users
    # Generate CSV
    # Return as file
```

**Tests**: `tests/api/test_user_export.py`
- Test endpoint returns CSV
- Test with filters
- Test with pagination
- Test error cases

**Estimate**: 1.5 hours

### Step 3: Add Export Button (Frontend)
**File**: `src/components/UserList.tsx`

```typescript
<Button
  icon={<DownloadIcon />}
  onClick={handleExport}
  loading={isExporting}
>
  Export CSV
</Button>
```

**Estimate**: 0.5 hours

### Step 4: Implement Download Logic (Frontend)
**File**: `src/services/userService.ts`

```typescript
export async function exportUsers(filters: UserFilters) {
  const response = await fetch('/api/users/export?' + buildQuery(filters));
  const blob = await response.blob();
  downloadBlob(blob, generateFilename());
}
```

**Tests**: `tests/services/userService.test.ts`
**Estimate**: 1 hour

### Step 5: Integration Testing
**Manual test cases**:
- [ ] Export with no filters
- [ ] Export with name filter
- [ ] Export with date range
- [ ] Export sorted list
- [ ] Names with commas (e.g., "Doe, John")
- [ ] Names with quotes
- [ ] Email addresses
- [ ] Large dataset (500 records)
- [ ] Empty dataset

**Estimate**: 1 hour

### Step 6: Documentation
- [ ] Update user guide
- [ ] Add API documentation
- [ ] Update changelog

**Estimate**: 0.5 hours

## Timeline

| Task | Estimate | Dependencies |
|------|----------|--------------|
| CSV Service | 1h | None |
| API Endpoint | 1.5h | CSV Service |
| Export Button | 0.5h | None |
| Download Logic | 1h | API Endpoint |
| Integration Testing | 1h | All above |
| Documentation | 0.5h | All above |
| **Total** | **5.5h** | |

## Dependencies & Risks

### Dependencies
- ✅ User list API exists and working
- ✅ User model has all required fields
- ⚠️ Need production data sample for testing

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Large exports timeout | High | Medium | Limit to 1000 records, add async later if needed |
| Special chars break CSV | Medium | Low | Use stdlib csv module with proper escaping |
| Browser compatibility | Medium | Low | Test in Chrome, Firefox, Safari |
| Memory issues | Low | Low | Stream CSV generation |

## Testing Strategy

### Unit Tests (Backend)
- CSV generation logic
- Special character handling
- Data formatting

### Unit Tests (Frontend)
- Download trigger
- Filename generation
- Error handling

### Integration Tests
- Full flow: UI → API → CSV → Download
- Filters applied correctly
- File format correct

### Manual Testing
- Cross-browser testing
- Real data testing
- Performance testing (500+ records)

## Success Metrics

- [ ] Users can export current page as CSV
- [ ] Export completes in < 2 seconds for 500 records
- [ ] CSV opens correctly in Excel
- [ ] Zero data corruption issues
- [ ] Works in all supported browsers

## Rollout

### Phase 1: Dev (Day 1)
- Implement all code
- Unit tests passing
- Manual testing in dev

### Phase 2: Staging (Day 2)
- Deploy to staging
- QA testing
- Load testing
- Bug fixes

### Phase 3: Production (Day 3)
- Deploy with feature flag
- Enable for 10% of users
- Monitor for 24h
- Enable for 100%

### Monitoring
- Export request count (expect ~100/day)
- Response time (target < 2s, alert > 5s)
- Error rate (target < 1%, alert > 5%)

## Rollback Plan
- Feature flag can disable export button
- No database migrations, safe to rollback code
- Monitoring will alert to issues quickly
```

## Tips for Good Plans

### Make Steps Concrete
```
❌ "Add export functionality"
✅ "Create exportUsers() function in userService.ts that calls /api/users/export and triggers download"
```

### Include File Paths
```
❌ "Update the user service"
✅ "Update src/services/userService.ts"
```

### Specify Tests
```
❌ "Add tests"
✅ "Add tests in tests/test_csv_export.py for: sample data, special chars, empty list, unicode"
```

### Estimate Time
```
❌ No estimates
✅ Each step: 0.5h - 2h estimates
```

### Identify Dependencies
```
❌ No dependency tracking
✅ "Step 4 depends on Step 2 (API endpoint must exist)"
```

### Plan for Risks
```
❌ No risk consideration
✅ "Risk: Timeout on large datasets. Mitigation: 1000 record limit"
```

## Remember

A good plan:
- **Clear context** - Why are we building this?
- **Concrete steps** - What exactly to do
- **Correct order** - What depends on what
- **Testable outcomes** - How do we know it works?
- **Risk awareness** - What could go wrong?

Write the plan before writing code. Adjust as you learn.
