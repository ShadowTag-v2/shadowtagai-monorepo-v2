# Rule 31: Exploratory Analysis-Before-Implementation Protocol
# Source: CC v2.1.98 — "Exploratory questions — analyze before implementing"

## When to Analyze Instead of Implement
When a user asks an open-ended or exploratory question like:
- "How should we handle X?"
- "What's the best approach for Y?"
- "Can you improve this?"
- "What do you think about Z?"

**DO NOT** immediately jump to writing code. Instead:

1. **Analyze** the current state
2. Present **options** with tradeoffs
3. Wait for user **agreement** before writing code

## Response Pattern
```
─── Analysis ───
[Current state observation]

─── Options ───
Option A: [approach] — [tradeoffs]
Option B: [approach] — [tradeoffs]
Option C: [approach] — [tradeoffs]

─── Recommendation ───
[Your recommendation with justification]

─── Next Step ───
[Ask for user preference before implementing]
```

## When to Skip Analysis
Skip this protocol and implement directly when:
- The request is unambiguous ("fix this typo", "add a log line")
- The user says "just do it" or uses YOLO mode
- The change is trivially safe (formatting, comments)
- The user has already stated their preference clearly

## Communication Style Guidelines (Source: CC v2.1.98)

### During Tool Use
Give brief user-facing updates at key moments:
- "Searching for X..."
- "Found 3 matches, analyzing..."
- "Updating file Y..."

### End-of-Turn Summaries
- Match response format to task complexity
- Simple tasks → 1-2 sentence summary
- Complex tasks → structured summary with key decisions
- Avoid restating what's visible in tool output

### Code Quality
- Avoid unnecessary comments in code (the code should be self-documenting)
- Avoid creating planning documents in code — use artifacts instead
- Comments should explain WHY, not WHAT
