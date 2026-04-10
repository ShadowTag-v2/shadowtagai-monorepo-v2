---
applyTo: "**/*.{test,spec}.{ts,tsx,py}"
---
- Prefer deterministic tests. No `sleep()` unless unavoidable.
- Mock network boundaries, not domain logic.
- Assert observable behavior, not implementation details.
