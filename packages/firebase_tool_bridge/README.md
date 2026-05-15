# Firebase Tool Bridge

> Client-side bridge from Firebase AI Logic function calls to approved application functions.

## Contract

See [`tool_contracts/firebase.function_bridge.yaml`](../../tool_contracts/firebase.function_bridge.yaml) for the governing contract.

## Architecture

```
Firebase AI Logic (Gemini model)
  ↓ proposes function call
Firebase SDK (client library)
  ↓ routes to registered handler
firebase_tool_bridge (this package)
  ↓ validates via ToolGateway contract
  ↓ checks risk classification
  ↓ requires confirmation for consequential actions
Application function (actual execution)
  ↓ returns result
firebase_tool_bridge
  ↓ logs evidence
  ↓ returns FunctionResponse to model
Firebase SDK → next model turn
```

## Key Principles

1. **The model proposes; the app executes.** The model never directly calls APIs.
2. **All function calls are registered.** Unregistered functions are rejected.
3. **Consequential actions require confirmation.** See `function_call.consequential_action.yaml`.
4. **Evidence is logged.** Every function call records: name, args hash, risk tier, result.
5. **Temperature 0.0 default.** Deterministic argument generation for tool calls.

## Implementation Status

- [ ] TypeScript SDK bridge (web/Node.js)
- [ ] Dart SDK bridge (Flutter)
- [ ] Python SDK bridge (server-side)
- [ ] ToolGateway integration
- [ ] Evidence logging hooks

## Reference

- [Firebase AI Logic — Function Calling](https://firebase.google.com/docs/ai-logic/function-calling)
- [`tool_contracts/function_call.consequential_action.yaml`](../../tool_contracts/function_call.consequential_action.yaml)
- [`MONOREPO_OS.md`](../../MONOREPO_OS.md) — ToolGateway → Push Gates integration
