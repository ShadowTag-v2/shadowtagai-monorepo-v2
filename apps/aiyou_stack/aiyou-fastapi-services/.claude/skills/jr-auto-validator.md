# SKILL: JR Auto-Validator

## RUN ON EVERY RESPONSE

### SILENT CHECKS (run but don't mention unless violated):
```python
def validate_jr():
    if roi < 3.0:
        return "⚠️ JR VIOLATION: ROI {roi} < 3×"
    if ltv_cac < 4.0:
        return "⚠️ JR VIOLATION: LTV:CAC {ltv_cac} < 4:1"
    if p99_latency > 90:
        return "⚠️ JR VIOLATION: p99 {p99_latency}ms > 90ms"
    if not has_kill_switch:
        return "⚠️ JR VIOLATION: No kill switch defined"
```

### WHEN VIOLATIONS FOUND:
Put at TOP of response:
```
⚠️ JR VIOLATION DETECTED
[specific violation]
Alternative: [compliant approach]

[then continue with answer]
```
