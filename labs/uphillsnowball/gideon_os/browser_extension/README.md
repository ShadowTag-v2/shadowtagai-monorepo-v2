# Browser Extension

> Gideon OS Block 9 — Secure Operator Sidebar

## Purpose

The Browser Extension provides a secure sidebar interface for operator interaction with the Gideon OS infrastructure directly from the browser. It replaces the deprecated Tauri desktop wrapper (archived 2026-04-24) with a lighter, WebAuthn-based approach.

## Architecture

```
┌─────────────────────────────────────────┐
│          Browser Tab (Chrome)           │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Sidebar UI │  │  Content Script │  │
│  │  (React)    │  │  (DOM Observer) │  │
│  └──────┬──────┘  └────────┬────────┘  │
│         │                  │            │
│  ┌──────▼──────────────────▼────────┐  │
│  │      Service Worker (MV3)        │  │
│  │  • WebAuthn gate                 │  │
│  │  • Message routing               │  │
│  │  • CSP enforcement               │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│  ┌──────────────▼───────────────────┐  │
│  │  Native Messaging Host (Python)  │  │
│  │  → Gideon OS subprocess bridge   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| WebAuthn Auth | Biometric authentication via platform authenticator |
| DOM Observer | Monitors and extracts structured data from web pages |
| Sidebar UI | React-based operator interface with real-time updates |
| Native Bridge | Python subprocess for Gideon OS command execution |
| CSP Strict | Manifest V3 with strict Content Security Policy |

## Security

- WebAuthn FIDO2 authentication (replaces Tauri biometric — Risk #83 RESOLVED)
- Manifest V3 with minimal permissions
- No `activeTab` unless explicitly granted
- Native Messaging Host restricted to allowlisted extensions
- All messages signed with session nonce

## Development

```bash
# Build the extension
cd labs/uphillsnowball/gideon_os/browser_extension
npm run build

# Load unpacked in Chrome
# chrome://extensions → Developer Mode → Load Unpacked → dist/
```

## Status

🔶 Scaffolded — MV3 manifest defined, WebAuthn flow prototyped, Native Messaging Host pending.
