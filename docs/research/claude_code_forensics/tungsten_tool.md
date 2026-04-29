# TungstenTool Forensics & Architecture

## Overview
`TungstenTool` is an internal ("ant-only") tool extracted from the Claude Code forensic audit (`_audit_claude_code/src/tools/TungstenTool/`). It provides background command execution capability using `tmux` for long-running shell jobs without blocking the main REPL thread.

## Components

### 1. The Tool (`src/tools/TungstenTool/TungstenTool.ts`)
- Exposed only when `process.env.USER_TYPE === 'ant'`.
- Uses `tmuxSocket.ts` to manage headless `tmux` sessions.
- Injects `args[]` into the transcript, causing it to render as a distinct UI block.

### 2. App State (`src/screens/REPL.tsx` & AppStateStore)
- `tungstenActiveSession`: Tracks the active background tmux session.
- `tungstenPanelAutoHidden`: Boolean tracking whether the expanded logs view has been minimized.

### 3. Live Monitor UI (`src/tools/TungstenTool/TungstenLiveMonitor.tsx`)
- Placed in the `REPL.tsx` view hierarchy (`{'external' === 'ant' && <TungstenLiveMonitor />}`).
- Renders a real-time view of the `tmux` buffer when expanded.
- When `tungstenPanelAutoHidden` is set to `true` (at the end of a turn), the main panel collapses, but a distinct "pill" remains in the footer (`PromptInputFooterLeftSide.tsx`), indicating that background tasks (e.g., `/hunter`) are still running.

## AGNT Porting Strategy
This behavior maps directly to the AGNT `command_status` async tracking system, where long-running commands return a `CommandId` that is monitored silently by the Loop Steward rather than blocking the active chat thread.
