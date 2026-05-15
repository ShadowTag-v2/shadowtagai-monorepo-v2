# CounselConduit — Vent Mode SSE Diagnostics

## Item #11: SSE Stream Debug Toolkit

### Problem Space

Vent Mode uses Server-Sent Events (SSE) for real-time token streaming.
Common failure modes:
- Connection drops mid-stream (client-side timeout or proxy kill)
- Backpressure buildup from slow consumers
- Memory leak from unclosed SSE connections
- Cloud Run request timeout (default 300s max)

### Diagnostic Endpoints

#### GET /admin/vent-mode/diagnostics

```python
# Add to dispatch_router.py or vent_mode_router.py
@router.get("/admin/vent-mode/diagnostics")
async def vent_mode_diagnostics(
    _caller: str = Depends(_verify_admin_caller),
) -> dict:
    """SSE stream health diagnostics."""
    return {
        "active_streams": len(_active_sse_connections),
        "total_streams_lifetime": _sse_stream_counter,
        "avg_stream_duration_ms": _avg_stream_duration,
        "dropped_connections": _sse_drops,
        "backpressure_events": _sse_backpressure_count,
        "max_concurrent_streams": _sse_max_concurrent,
    }
```

### Cloud Run SSE Configuration

```bash
# Increase request timeout for long SSE sessions (max 3600s for HTTP/2)
gcloud run services update counselconduit \
  --timeout=600 \
  --region=us-central1 \
  --project=shadowtag-omega-v4

# Verify HTTP/2 is enabled (required for SSE multiplexing)
gcloud run services describe counselconduit \
  --region=us-central1 \
  --format="value(spec.template.metadata.annotations)" \
  --project=shadowtag-omega-v4
```

### Client-Side SSE Debug

```javascript
// Browser console diagnostic
const es = new EventSource('/api/v1/vent-mode/stream?session_id=debug');
es.onopen = () => console.log('SSE opened');
es.onerror = (e) => console.error('SSE error:', e);
es.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(`Token: ${data.token} | Latency: ${data.latency_ms}ms`);
};

// Heartbeat check
setTimeout(() => {
  if (es.readyState === EventSource.CLOSED) {
    console.error('SSE connection closed prematurely');
  }
}, 5000);
```

### Structured Logging for SSE

```python
def emit_sse_event_log(
    session_id: str,
    event_type: str,  # "open", "token", "close", "error", "heartbeat"
    latency_ms: float = 0,
    tokens_sent: int = 0,
    error: str = "",
):
    """Structured log for SSE event tracking."""
    log_entry = {
        "log_type": "sse_event",
        "severity": "ERROR" if event_type == "error" else "INFO",
        "session_id": session_id,
        "event_type": event_type,
        "latency_ms": round(latency_ms, 2),
        "tokens_sent": tokens_sent,
        "error": error,
        "timestamp": time.time(),
    }
    import json
    print(json.dumps(log_entry), flush=True)
```

### Load Shedding for SSE

If concurrent SSE streams exceed threshold, reject new connections:

```python
_MAX_CONCURRENT_SSE = 50
_active_sse_count = 0

@asynccontextmanager
async def sse_connection_guard():
    global _active_sse_count
    if _active_sse_count >= _MAX_CONCURRENT_SSE:
        raise HTTPException(
            status_code=503,
            detail="SSE connections at capacity. Retry later."
        )
    _active_sse_count += 1
    try:
        yield
    finally:
        _active_sse_count -= 1
```

### Monitoring

Add to `main.tf`:
```hcl
resource "google_logging_metric" "sse_errors" {
  name   = "counselconduit_sse_errors"
  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.log_type=\"sse_event\" AND jsonPayload.event_type=\"error\""
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}
```

### Common Issues + Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Client receives partial response | Cloud Run timeout | Increase `--timeout=600` |
| Connection drops after 60s | ALB idle timeout | Add SSE heartbeat every 30s |
| 503 during high load | Too many concurrent streams | Enable load shedding guard |
| Memory growth over time | Unclosed SSE connections | Add connection timeout + cleanup |
| Token order scrambled | Race condition | Use sequence numbers in SSE data |
