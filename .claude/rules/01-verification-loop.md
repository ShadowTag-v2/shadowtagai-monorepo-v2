# Rule 01: Employee-Grade Verification Loop

The employee-only verification gate: In services/tools/toolExecution.ts, the agent's success metric for a file write is exactly one thing: did the write operation complete? Not "does the code compile." Not "did I introduce type errors." Just: did bytes hit disk?

The source contains explicit instructions telling the agent to verify its work before reporting success. Those instructions are gated behind `process.env.USER_TYPE === 'ant'`. What that means is that Anthropic employees get post-edit verification, and you don't. Their own internal comments document a 29-30% false-claims rate on the current model. They know it, and they built the fix — then kept it for themselves.

## The Override
You are FORBIDDEN from reporting a task as complete until you have:
1. Run `npx tsc --noEmit` (or the project's equivalent type-check)
2. Run `npx eslint . --quiet` (if configured)
3. Fixed ALL resulting errors
4. If no type-checker is configured, state that explicitly instead of claiming success

This is non-negotiable. Every file modification triggers the verification loop.
