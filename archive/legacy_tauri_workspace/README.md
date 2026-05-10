# Legacy Tauri Agentic Workspace — ARCHIVED

**Archived**: 2026-04-24
**Reason**: Tauri retired from UphillSnowball. Replaced by browser tab + WebAuthn approvals.

## What replaced this

- **UI**: Browser tab (no Tauri desktop wrapper)
- **Biometric auth**: WebAuthn / FIDO2 passkeys (replaces local TouchID/FaceID hooks)
- **Control plane**: Cloud Run `uphillsnowball-control` service
- **Architecture**: See `docs/UPHILLSNOWBALL_ARCHITECTURE.md`

## Why

- Tauri required local desktop deployment, limiting reach
- `trigger_biometric_auth()` always returned true (Risk #83)
- WebAuthn provides equivalent biometric security in the browser
- Cloud Run sidecar pattern replaces local sidecar architecture
