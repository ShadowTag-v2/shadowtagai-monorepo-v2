# API Versioning Strategy — CounselConduit

## Current State
- API version: v1 (implicit, no prefix)
- All endpoints at root path (e.g., `/dispatch`, `/admin/metrics`)

## Versioning Approach: URL Path Prefix

### Phase 1: Add Version Prefix (Non-Breaking)
```
/v1/dispatch          ← New canonical path
/dispatch             ← Legacy alias (302 redirect after deprecation period)
/v1/admin/metrics     ← New canonical path
/admin/metrics        ← Legacy alias
```

### Phase 2: v2 Introduction
```python
# dispatch_router.py
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

# v1 stays frozen after deprecation notice
@v1_router.post("/dispatch")
async def dispatch_v1(body: DispatchRequest): ...

# v2 introduces breaking changes
@v2_router.post("/dispatch")
async def dispatch_v2(body: DispatchRequestV2): ...
```

## Deprecation Policy
1. **Announce**: 90 days before deprecation
2. **Warn**: Add `Deprecation` and `Sunset` headers
3. **Redirect**: 301/302 from old to new for 30 days
4. **Remove**: After sunset date

### Headers
```
Deprecation: true
Sunset: Sat, 01 Nov 2026 00:00:00 GMT
Link: </v2/dispatch>; rel="successor-version"
```

## Breaking vs Non-Breaking Changes
| Change | Breaking? | Requires New Version? |
|--------|-----------|----------------------|
| Add optional field to response | No | No |
| Add required field to request | Yes | Yes |
| Remove field from response | Yes | Yes |
| Change field type | Yes | Yes |
| Add new endpoint | No | No |
| Change auth mechanism | Yes | Yes |

## OpenAPI
- Each version gets its own OpenAPI spec
- Spec served at `/v1/openapi.json`, `/v2/openapi.json`
- Combined spec at `/openapi.json` showing all active versions
