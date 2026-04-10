# Retrieval-of-Thought (RoT) Template: Postgres Deadlock Resolution
**ID**: `rot-db-001`
**Trigger**: `OperationalError: deadlock detected`

## 1. Immediate Diagnosis
- **Check `pg_stat_activity`**: Identify blocking PIDs.
- **Trace Transaction**: Map the lock order (Item A -> Item B vs Item B -> Item A).

## 2. Common Root Causes & Fixes
### Pattern A: Unordered Inserts (High Entropy)
*   **Symptoms**: Concurrent inserts into parent/child tables.
*   **Fix**: Enforce alphanumeric sorting of IDs before batch operations.
    ```python
    items.sort(key=lambda x: x.id)  # Enforce Order
    ```

### Pattern B: Index Gap Locking (Medium Entropy)
*   **Symptoms**: UPDATE on non-indexed columns.
*   **Fix**: Add index to foreign key columns immediately.

## 3. Resolution Protocol (SOP-B)
1.  Kill blocking PID (if user-facing impact > 500ms).
2.  Apply "Enforce Order" patch.
3.  Add retry logic with exponential backoff (`tenacity`).

## 4. CodePMCS Verification
- [ ] Test with `pg_isolation_test` (simulate concurrency).
- [ ] Verify `ORDER BY` in all batch transaction queries.
