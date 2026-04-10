# Brainstorming: Socratic Design Refinement

## When to Use

Use when:
- Starting a new feature or project
- Facing a complex design decision
- Multiple approaches are possible
- Requirements are unclear or ambiguous
- Need to explore trade-offs

## The Socratic Method

Instead of jumping to solutions, use questions to refine understanding and explore options.

## Process

### Phase 1: Understand the Problem Domain

**Ask clarifying questions about the actual problem, not solutions.**

#### Questions to Ask:
```
- What problem are we actually solving?
- Who is the user/customer?
- What are they trying to accomplish?
- What are the constraints? (time, resources, technology)
- What are the success criteria?
- What does "done" look like?
```

#### Example:
```
Task: "Add export functionality"

DON'T immediately propose: "Let's add a CSV export button"

DO ask first:
- What data needs to be exported?
- Who will use the exports?
- How will they use the exported data?
- How often will they export?
- How much data might be exported?
- Are there regulatory requirements (GDPR, etc.)?
- What formats do they need? (CSV, JSON, Excel, PDF?)
```

### Phase 2: Explore Multiple Approaches

**Generate at least 3 different approaches before choosing.**

#### Template:
```
Approach 1: [Name]
- How it works: ...
- Pros: ...
- Cons: ...
- Complexity: Low/Medium/High
- Best for: ...

Approach 2: [Name]
- How it works: ...
- Pros: ...
- Cons: ...
- Complexity: Low/Medium/High
- Best for: ...

Approach 3: [Name]
- How it works: ...
- Pros: ...
- Cons: ...
- Complexity: Low/Medium/High
- Best for: ...
```

#### Example:
```
Problem: Export user data

Approach 1: Synchronous Direct Export
- How: Generate file immediately on request, return download
- Pros: Simple, immediate feedback
- Cons: Times out on large datasets, blocks server
- Complexity: Low
- Best for: Small datasets (<1000 records)

Approach 2: Async with Background Job
- How: Queue export job, email link when done
- Pros: Handles large datasets, doesn't block
- Cons: Delayed feedback, requires job queue
- Complexity: Medium
- Best for: Large datasets, infrequent exports

Approach 3: Streaming Export
- How: Stream data incrementally as generated
- Pros: Handles large datasets, immediate start
- Cons: Complex implementation, connection issues
- Complexity: High
- Best for: Very large datasets, real-time needs
```

### Phase 3: Challenge Assumptions

**Question everything, especially "obvious" choices.**

#### Questions to Ask:
```
- Why do we need this feature?
- What if we did nothing?
- What's the simplest thing that could work?
- Are we solving the right problem?
- Is there existing functionality we can reuse?
- Can we solve this without code?
- What would happen if we waited?
```

#### Example:
```
Assumption: "We need to export data"

Challenge:
- Why do users want to export?
  → "To analyze data in Excel"

Could we instead:
- Add better analytics in the app?
- Integrate with BI tools?
- Provide a read-only API?

Maybe export is a workaround for missing analytics features!
```

### Phase 4: Consider Trade-offs

**Every decision has trade-offs. Make them explicit.**

#### Trade-off Dimensions:
```
- Simplicity vs. Flexibility
- Performance vs. Maintainability
- Time to ship vs. Technical debt
- User experience vs. Implementation cost
- Generality vs. Specific needs
```

#### Example:
```
Trade-off: Simple sync export vs. Complex async export

If we choose simple sync:
+ Ship faster
+ Easier to maintain
+ Fewer moving parts
- Times out on large datasets
- Poor user experience for big exports
- Might need to rebuild later

If we choose complex async:
+ Handles all dataset sizes
+ Better user experience
+ Scales better
- Takes longer to build
- More infrastructure (queue, workers)
- More to maintain

Decision: Start with sync, add async if needed
Reason: 90% of exports are <500 records (verified with data)
```

### Phase 5: Define the MVP

**What's the smallest thing we can ship that delivers value?**

#### Questions:
```
- What's the core value?
- What can we cut and still be useful?
- What can we add later?
- What's the 80/20 split?
```

#### Example:
```
MVP for Export Feature:

Include:
✓ Export current page as CSV
✓ Include visible columns only
✓ Basic filename (export-YYYY-MM-DD.csv)

Defer to v2:
- Custom column selection
- Multiple formats (Excel, JSON)
- Scheduled exports
- Export all pages (not just current)

Rationale: 80% of users just want to copy current view to Excel
```

### Phase 6: Document the Decision

**Record why you chose this approach.**

#### Template:
```markdown
## Decision: [Title]

### Context
[What problem we're solving]

### Options Considered
1. [Approach 1] - [Why not chosen]
2. [Approach 2] - [Why not chosen]
3. [Approach 3] - [CHOSEN]

### Decision
We chose [Approach X] because:
- [Reason 1]
- [Reason 2]
- [Reason 3]

### Trade-offs Accepted
- [Trade-off 1]: We accept [downside] to get [upside]
- [Trade-off 2]: ...

### Success Metrics
- [How we'll measure success]

### Review Date
- [When we'll revisit this decision]
```

## Example: Complete Brainstorming Session

```
TASK: Add real-time notifications to the app

=== Phase 1: Understand ===

Q: What events need notifications?
A: New messages, mentions, system alerts

Q: Who receives notifications?
A: All logged-in users

Q: How many users?
A: ~10,000 active users, ~500 concurrent

Q: How often do events happen?
A: ~100 events/minute total

Q: What's the latency requirement?
A: "Real-time" = within a few seconds is fine

=== Phase 2: Explore Approaches ===

Approach 1: Polling
- Client checks server every 5 seconds
- Pros: Simple, works everywhere
- Cons: Wasteful, delayed, server load
- Complexity: Low

Approach 2: WebSockets
- Persistent connection per client
- Pros: True real-time, efficient
- Cons: Complex, scaling challenges
- Complexity: High

Approach 3: Server-Sent Events (SSE)
- Server pushes to client over HTTP
- Pros: Simpler than WebSockets, real-time
- Cons: One-way only, connection limits
- Complexity: Medium

=== Phase 3: Challenge Assumptions ===

Q: Do we really need real-time?
A: Users expect it for messaging

Q: Could we do messaging-specific solution?
A: Maybe! Chat vs. other notifications different

Q: What about mobile?
A: Mobile uses push notifications anyway

Decision: Different solutions for different needs
- Chat: WebSockets (real-time critical)
- Other notifications: SSE (real-time nice-to-have)
- Mobile: Push notifications (separate system)

=== Phase 4: Trade-offs ===

WebSockets for chat:
+ True bidirectional real-time
+ Best user experience
- Complex infrastructure
- Need to handle reconnections
- Scaling requires consideration

Accept trade-off: Worth complexity for core chat feature

=== Phase 5: MVP ===

MVP:
✓ WebSocket for chat messages only
✓ Fallback to polling if WebSocket fails
✓ Basic reconnection logic
✓ Works for 500 concurrent users

Defer:
- SSE for other notifications (use polling for now)
- Advanced reconnection strategies
- Horizontal scaling (single server fine for now)

=== Phase 6: Document ===

Decision: WebSockets for chat, polling for other notifications

Context: Users expect real-time chat, other notifications less critical

Chosen: Hybrid approach
- WebSockets for chat (real-time critical)
- Polling for notifications (real-time nice-to-have)

Trade-offs:
- Complexity of two systems vs. consistency
- Accept: Worth it for better UX where it matters

Success: Average message latency < 1 second

Review: After 3 months, consider SSE for notifications
```

## Brainstorming Questions Library

### Understanding the Problem
- What's the actual user need?
- What problem does this solve?
- How do users currently work around this?
- What's painful about the current solution?

### Exploring Solutions
- What are 3 completely different ways to solve this?
- What would the simplest solution look like?
- What would the most robust solution look like?
- What would the fastest-to-ship solution look like?

### Challenging Assumptions
- Why do we think we need this?
- What if we did nothing?
- What if we removed something instead of adding?
- Are we solving the root cause or a symptom?

### Understanding Trade-offs
- What are we optimizing for?
- What are we willing to sacrifice?
- What's the cost of being wrong?
- How easily can we change this later?

### Defining Scope
- What's the smallest useful version?
- What can we learn before building everything?
- What can we fake/mock initially?
- What would a beta version include?

## Anti-Patterns

### ❌ Jumping to Solutions
```
User: "We need export"
Dev: "I'll add a CSV export button!"

DON'T: Skip understanding the problem
DO: Ask why, explore options, consider alternatives
```

### ❌ Single Option Bias
```
"The solution is obviously to use Redis for this"

DON'T: Consider only one approach
DO: Generate at least 3 options, compare trade-offs
```

### ❌ Analysis Paralysis
```
Week 1: Discussing approach A vs B
Week 2: Still discussing, found approach C
Week 3: Should we reconsider approach A?

DON'T: Discuss forever
DO: Time-box brainstorming, make decision, move forward
```

### ❌ No Documentation
```
After 2-hour brainstorming session:
Team: "So what did we decide?"
Everyone: "Uh..."

DON'T: Leave decisions undocumented
DO: Write down decisions and reasoning
```

## Time-boxing

Brainstorming should be time-boxed:

- **Small feature**: 15-30 minutes
- **Medium feature**: 1-2 hours
- **Large project**: 1-2 days (with breaks)

After time-box: **Make a decision and move forward**

## Remember

- **Understand before solving**
- **Explore multiple options**
- **Challenge assumptions**
- **Make trade-offs explicit**
- **Document decisions**
- **Time-box the process**

Good brainstorming leads to better designs and fewer regrets.
