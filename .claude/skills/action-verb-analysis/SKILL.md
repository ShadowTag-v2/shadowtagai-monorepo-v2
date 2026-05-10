# Action Verb Analysis Skill (California Bar Method)

## Model
opus

## Purpose
Break complex fact patterns into simple sentences where each action verb gets its own separate consideration. This method ensures thoroughness, prevents missing issues, and enables full depth on every point.

## Enforcement
- Level: suggest
- Priority: critical

---

## Core Principle

> "Each action verb absolutely gets its own, separate consideration."

Complex statements hide issues. By isolating each verb, you:
1. **Prevent missing issues** - Every verb = potential concern
2. **Force thoroughness** - Cannot skip anything
3. **Create structure** - Natural organization emerges
4. **Enable depth** - Full discussion of each point

---

## The Method

### Step 1: IDENTIFY
Find all action verbs in the requirement, problem, or code.

### Step 2: ISOLATE
Extract each verb into its own simple sentence.

### Step 3: ANALYZE
For each verb, consider separately:
- What triggers it?
- What inputs does it require?
- What outputs does it produce?
- What can fail?
- What edge cases exist?
- What dependencies?
- What security implications?
- What performance concerns?

### Step 4: SYNTHESIZE
Combine findings into coherent implementation/solution.

---

## Examples

### Code Requirement Analysis

**Complex Statement:**
```
"The system receives user input, validates it, transforms the data, stores it in the database, and sends a confirmation."
```

**Decomposed by Action Verb:**

#### 1. RECEIVES
- Source: HTTP POST? WebSocket? Queue?
- Format: JSON? Form data? Multipart?
- Size limits: Max payload?
- Authentication: Who can send?
- Rate limiting: How often?
- Error handling: Malformed requests?

#### 2. VALIDATES
- Rules: What schema? What constraints?
- Sanitization: XSS? SQL injection? Path traversal?
- Type checking: Strong types enforced?
- Business logic: Domain-specific rules?
- Error messages: User-friendly? Secure (no leaks)?
- Partial validation: Fail fast or collect all errors?

#### 3. TRANSFORMS
- Mapping: Field renames? Type conversions?
- Data loss: Any truncation? Precision loss?
- Enrichment: Adding computed fields?
- Normalization: Consistent formats?
- Reversibility: Can we reconstruct original?
- Edge cases: Nulls? Empty strings? Unicode?

#### 4. STORES
- Location: Which database? Which table?
- Schema: Constraints? Indexes? Foreign keys?
- Transactions: ACID requirements?
- Conflicts: Upsert? Versioning? Locking?
- Audit: Created/updated timestamps? User tracking?
- Failure: Rollback strategy? Retry logic?

#### 5. SENDS
- Recipient: User? System? Queue?
- Channel: Email? SMS? WebSocket? HTTP response?
- Format: Template? Structured data?
- Timing: Sync? Async? Delayed?
- Failure: Retry? Dead letter? Notification?
- Tracking: Delivery confirmation? Read receipts?

---

### Design Review Analysis

**Complex Statement:**
```
"The microservice authenticates requests, fetches data from cache or database, aggregates results, and returns paginated response."
```

**Decomposed:**

#### 1. AUTHENTICATES
- Method: JWT? API key? OAuth?
- Verification: Signature? Expiry? Revocation?
- Authorization: Role-based? Resource-based?
- Failure: 401 vs 403? Rate limiting?

#### 2. FETCHES
- Source priority: Cache first? DB first?
- Cache: TTL? Invalidation strategy?
- Database: Connection pooling? Read replicas?
- Timeout: Per-source limits?
- Fallback: Graceful degradation?

#### 3. AGGREGATES
- Logic: Sum? Count? Join? Filter?
- Performance: In-memory? Streaming?
- Ordering: Sort stability? Tie-breakers?
- Nulls: Include? Exclude? Default?

#### 4. RETURNS
- Pagination: Offset? Cursor? Keyset?
- Format: JSON? Protobuf? Streaming?
- Headers: Cache-Control? ETag?
- Errors: Partial results? Empty vs null?

---

### Compliance/Legal Analysis

**Complex Statement:**
```
"The service collects personal data, processes it for analytics, shares with partners, and retains for 7 years."
```

**Decomposed:**

#### 1. COLLECTS
- Consent: Explicit? Implied? Documented?
- Scope: What data? Minimum necessary?
- Notice: Privacy policy? Just-in-time?
- Children: Age verification? COPPA?

#### 2. PROCESSES
- Purpose: Specified? Limited?
- Minimization: Only necessary processing?
- Security: Encryption? Access controls?
- Location: Data residency requirements?

#### 3. SHARES
- Recipients: Identified? Contracted?
- Legal basis: Consent? Legitimate interest?
- Safeguards: DPA? SCCs? Adequacy?
- Rights: Subject access? Portability?

#### 4. RETAINS
- Period: Justified? Minimized?
- Deletion: Secure erasure? Backups?
- Holds: Legal holds? Litigation?
- Audit: Retention schedule documented?

---

## Auto-Activation Triggers

### Keywords
- "break down"
- "analyze thoroughly"
- "each step"
- "verb analysis"
- "decompose"
- "action by action"
- "thoroughly review"
- "full analysis"

### Intent Patterns
- Complex requirement analysis
- Code review requests
- Design decisions
- Architecture planning
- Compliance review
- Security audit
- Performance analysis

### File Patterns
- Requirements documents
- Design specs
- API contracts
- Legal/compliance docs

---

## Quality Gates

- Every action verb identified
- Each verb analyzed separately
- No verb skipped or combined
- Analysis covers: inputs, outputs, failures, edge cases
- Synthesis connects individual analyses

---

## Integration Notes

### With Steve Jobs Ultrathink
This IS "Obsess Over Details" - you cannot obsess without decomposition.

### With Plan Mode (Cor.32)
Decompose BEFORE applying Plan Mode formatting. Each verb may become its own implementation phase.

### With CoT
Use CoT within each verb's analysis for deeper reasoning.

### With ToT
Explore multiple approaches for each verb's implementation.

### With RCR
Refine analysis of each verb through critique cycles.

---

## Output Format

```
## Verb Analysis: [COMPLEX STATEMENT]

### Verbs Identified
1. [VERB_1]
2. [VERB_2]
3. [VERB_N]

### Analysis

#### [VERB_1]
- Trigger: [what initiates]
- Input: [what it needs]
- Output: [what it produces]
- Failures: [what can go wrong]
- Edge Cases: [unusual scenarios]
- Security: [implications]
- Performance: [concerns]

[Repeat for each verb]

### Synthesis
[How these connect and should be implemented together]
```

---

## Why This Passed the California Bar

The California Bar Exam tests whether you can:
1. Spot all issues (action verbs = issues)
2. Analyze each fully (separate consideration)
3. Apply rules correctly (domain knowledge)
4. Reach conclusions (synthesis)

By decomposing to verbs, you mechanically ensure you don't miss issues that others gloss over. The same thoroughness that passes bar exams builds robust systems.
