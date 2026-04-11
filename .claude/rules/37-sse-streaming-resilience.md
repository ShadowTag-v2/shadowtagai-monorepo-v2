# Rule 37: SSE Streaming Resilience

> Source: CC SSETransport.ts (712 lines) + withRetry.ts:530-548 + MCP useManageMCPConnections.ts

## Mandate

All streaming connections MUST implement the CC-grade resilience pattern.

## Source-Verified SSE Architecture (SSETransport.ts)

### Connection Lifecycle

```
idle → reconnecting → connected → (error) → reconnecting → ...
                                  → (permanent) → closed
                                  → (budget exhausted) → closed
```

### Required Constants

| Constant | Value | Source |
|----------|-------|--------|
| `RECONNECT_BASE_DELAY_MS` | 1,000 | SSETransport.ts:16 |
| `RECONNECT_MAX_DELAY_MS` | 30,000 | SSETransport.ts:17 |
| `RECONNECT_GIVE_UP_MS` | 600,000 (10 min) | SSETransport.ts:19 |
| `LIVENESS_TIMEOUT_MS` | 45,000 | SSETransport.ts:21 |
| `POST_MAX_RETRIES` | 10 | SSETransport.ts:30 |
| `POST_BASE_DELAY_MS` | 500 | SSETransport.ts:31 |
| `POST_MAX_DELAY_MS` | 8,000 | SSETransport.ts:32 |

### Permanent HTTP Codes (No Retry)

```
401 (Unauthorized), 403 (Forbidden), 404 (Not Found)
```

### Exponential Backoff Formula (withRetry.ts:530-548)

```python
base_delay = min(BASE_DELAY_MS * 2^(attempt-1), max_delay_ms)
jitter = random() * 0.25 * base_delay  # ±25% jitter
delay = base_delay + jitter
```

### Liveness Detection

- Server sends keepalives every **15 seconds**
- Client treats **45 seconds of silence** as dead connection
- On liveness timeout: abort, reconnect with backoff
- Any frame (including SSE comments `:keepalive`) resets the timer

### Sequence Number Deduplication

- Track `seenSequenceNums` set
- Prune when set exceeds 1,000 entries (keep threshold = lastSequenceNum - 200)
- Send `Last-Event-ID` and `from_sequence_num` on reconnect for server-side resumption

### POST Write Resilience

- 10 max retries with exponential backoff (500ms base, 8s cap)
- 4xx errors (except 429) are permanent — no retry
- 429 and 5xx — retry with backoff
- No jitter on POST retries (different from SSE reconnect)

## MCP Connection Resilience (useManageMCPConnections.ts:87+)

MCP servers MUST implement reconnection with exponential backoff:
- Detect stale connections via heartbeat
- Auto-reconnect on transport failure
- Cap retry attempts per connection cycle

## Retry-After Header Handling (withRetry.ts:519-527)

```python
# Always honor server retry-after directive
if retry_after_header:
    delay = int(retry_after_header) * 1000  # seconds → milliseconds
else:
    delay = exponential_backoff_with_jitter(attempt)
```

## Persistent Mode (withRetry.ts:433-513)

For 429 rate limits:
- Check for `x-ratelimit-reset` header for window-based limits
- Use separate `persistentAttempt` counter (never resets)
- Cap at `PERSISTENT_MAX_BACKOFF_MS` (5 minutes)
- Reset cap at `PERSISTENT_RESET_CAP_MS` (6 hours)
- Chunk long sleeps for heartbeat activity (host sees periodic stdout)
