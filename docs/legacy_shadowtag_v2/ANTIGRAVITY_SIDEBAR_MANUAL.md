# Antigravity & Cloud Code 2026 Manual

## 1. Overview

As of 2026, **Google Cloud Code** is the primary interface for **Antigravity** (Agent-First Platform) and **Gemini Code Assist**. This integration brings "God Mode" capabilities directly into VS Code.

## 2. The Sidebar (Activity Bar)

- **Icon:** Look for the **Cloud Code icon** (far-left sidebar).
- **Capabilities:**
  - **Antigravity Agent:** A dedicated pane for the AI to plan, execute, and "UltraThink".
  - **Quota Tracking:** Real-time visibility into your Daily Limits for Claude/Gemini usage.
  - **Multi-Agent Toggle:** Switch between "Alpha" (CEO), "Bravo" (Hunter), or "CodePMCS" roles.
  - **Cloud Run/GKE:** Manage deployments directly.

## 3. Key Interactions

- **Launch:** Click the Sidebar Icon -> Select `Antigravity Agent` or `Gemini Code Assist`.
- **Shortcuts:**
  - `Ctrl+Shift+X` (Extensions) -> Ensure `Google Cloud Code` is active.
  - Status Bar: Check **AGQ (Antigravity Quota)** availability.

## 4. Troubleshooting

- **Missing Icon?**
  1.  `Settings > Extensions > Google Cloud Code`: Check `Enable Gemini/Duet AI`.
  2.  **Restart IDE:** 2026 updates often require a full reload.
- **Quota Lag:** Use the CLI tool `antigravity-usage` for real-time stats if the UI lags.

## 5. Security & Auth

- **Keyless:** Uses OAuth via `gcloud` or Cloud Code link. No hardcoded JSON keys.
- **Restrictions:** The AI honors `.aiexclude` to avoid leaking secrets.
