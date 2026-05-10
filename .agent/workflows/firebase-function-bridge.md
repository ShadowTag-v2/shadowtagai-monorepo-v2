---
description: Implement Firebase AI Logic function calling safely as a Monorepo OS client edge.
---

# /firebase-function-bridge

## Goal

Implement Firebase AI Logic function calling as a governed client-side bridge
that obeys the same safety physics as Antigravity's repo-side ToolGateway.

## Steps

1. Define the local or API function first (the real code).
2. Create a function declaration with:
   - Descriptive name (alphanumeric + underscores)
   - Clear description of what the function does
   - Typed parameters with JSON Schema
   - Narrow scope — one responsibility per function
3. Register only task-relevant tools:
   - Default active tool bundle: **under 10**
   - Hard review threshold: **20**
   - Use scoped bundles, not global tool exposure
4. Set generation config:
   - Temperature: **0.0** for deterministic tool selection
   - Override via Firebase Remote Config if needed
5. Use chat-style interaction for function calling.
6. When model requests a function call:
   - Verify function name is registered in `ToolRegistry`
   - Parse and validate arguments against schema
   - Classify risk through `ToolGateway` contract
   - Request user confirmation for consequential actions
   - Execute function in app code (never model-direct)
   - Return `FunctionResponsePart` with same function name
   - Write evidence
7. Handle edge cases:
   - Multiple function calls in one response
   - Malformed arguments → reject with error
   - Unknown function name → reject with error
   - Consequential action without confirmation → block
8. Add tests:
   - Valid function call round-trip
   - Malformed arguments rejection
   - Unknown function rejection
   - Consequential action confirmation gate
   - Multiple function calls in one response
   - Temperature override via Remote Config

## Contracts

- `tool_contracts/firebase.function_bridge.yaml`
- `tool_contracts/function_call.consequential_action.yaml`
- `tool_contracts/firebase.ai_logic_launch.yaml`

## Package

- `packages/firebase_tool_bridge/`

## Rules

- The model proposes; the app executes
- No silent consequential actions
- No unbounded tool lists
- Evidence for every execution
- Remote Config for runtime knobs, not hardcoded values
