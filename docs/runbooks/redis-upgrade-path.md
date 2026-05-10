# Redis Upgrade Path for Multi-Instance Rate Limiting

## Item #14: Redis Upgrade — Migration Plan

### Current State

Token-level rate limiting and session pin tracking use **in-memory dictionaries** in `dispatch_router.py`. This works for:
- Single Cloud Run instance (min-instances=1 covers this now)
- Low to moderate traffic (< 100 RPS)

### Problem at Scale

With `max-instances > 1`, each instance maintains its own rate limit state.
A firm could bypass token limits by having requests routed to different instances.

### Migration Path

#### Phase 1: Memorystore (Recommended)

```bash
# Create Redis instance (Basic tier, 1GB)
gcloud redis instances create counselconduit-cache \
  --region=us-central1 \
  --tier=basic \
  --size=1 \
  --redis-version=redis_7_2 \
  --project=shadowtag-omega-v4

# Connect Cloud Run to VPC for Redis access
gcloud run services update counselconduit \
  --add-vpc-connector=counselconduit-vpc \
  --region=us-central1 \
  --project=shadowtag-omega-v4
```

#### Phase 2: Code Changes

```python
# Replace in dispatch_router.py

import redis

_redis = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=6379,
    decode_responses=True,
)

def check_token_budget(firm_id: str, tier: str, estimated_tokens: int) -> dict:
    """Redis-backed token budget with sliding window."""
    key = f"token_budget:{firm_id}"
    budget = _TIER_TOKEN_BUDGETS.get(tier, _DEFAULT_TOKEN_BUDGET)

    pipe = _redis.pipeline()
    pipe.get(key)
    pipe.ttl(key)
    current, ttl = pipe.execute()

    used = int(current or 0)
    remaining = budget - used

    if remaining >= estimated_tokens:
        if used == 0:
            _redis.setex(key, _TOKEN_BUDGET_WINDOW, estimated_tokens)
        else:
            _redis.incrby(key, estimated_tokens)
        used += estimated_tokens

    return {
        "allowed": remaining >= estimated_tokens,
        "remaining": max(0, remaining - estimated_tokens),
        "budget": budget,
        "used": used,
    }
```

#### Phase 3: Session Pin Migration

```python
def _persist_session_pin_redis(session_id: str, model_key: str, ttl: int = 1800):
    """Redis-backed session pin with automatic expiry."""
    _redis.setex(f"session_pin:{session_id}", ttl, model_key)
```

### Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| Memorystore Basic 1GB | ~$35/mo |
| VPC Connector | ~$7/mo |
| **Total** | **~$42/mo** |

### Trigger Criteria

Migrate to Redis when:
- `max-instances` exceeds 3
- Rate limit bypass reports appear in logs
- Dispatch latency p95 exceeds 500ms (in-memory contention)
- Monthly revenue exceeds $2,000 (can justify $42/mo)
