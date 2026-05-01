# Category B Hooks Porting Plan (STATE B - CLUTCH)

## Objective
Extract core business logic from Claude's Ink-based React hooks (Category B) and port them into Antigravity's headless, asynchronous Python/TypeScript daemons, stripping all UI/PTY dependencies.

## Targets (from /Users/pikeymickey/Downloads/Claude_Source_Code/hooks/)
1. `useCommandQueue.ts`
2. `useMainLoopModel.ts`
3. `useScheduledTasks.ts`
4. `useInboxPoller.ts`
5. `useReplBridge.tsx`

## Guidelines
- **Headless CLI Doctrine**: No `ink`, `react`, `useState`, `useEffect`. No interactive terminal manipulation.
- **Python / Asyncio preference**: Where applicable, convert stateful loops into Python asyncio daemons (e.g. for `scripts/kairos_daemon.py`).
- **BLAST Pipeline Security**: Ensure no external telemetry or hardcoded API endpoints are ported.

## Execution
- Dispatching `generalist` agent to read the source files, extract the pure logic, and draft the initial ported files in `scripts/ported_claude_controllers/` (or similar namespace) for review.