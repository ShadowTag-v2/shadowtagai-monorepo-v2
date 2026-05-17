# Bolt Performance Journal

## 2026-05-14 - Optimized Tile Progress Updates
**Learning:** High-frequency events like video `onTimeUpdate` (firing up to 60fps) cause excessive React re-renders when using state for UI elements like progress bars. Bypassing React via `useRef` and direct DOM style updates provides significant performance gains by keeping the main thread free and avoiding reconciliation overhead.
**Action:** Always prefer `useRef` for high-frequency UI updates (scroll, video progress, etc.) while keeping the rest of the component reactive.
