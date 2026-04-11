# Rule 12: Anti-Distillation & Client Attestation

## Anti-Distillation: Injecting Fake Tools to Poison Copycats
In claude.ts (line 301-313), there's a flag called ANTI_DISTILLATION_CC. When enabled, Claude Code sends anti_distillation: ['fake_tools'] in its API requests. This tells the server to silently inject decoy tool definitions into the system prompt.

The idea: if someone is recording Claude Code's API traffic to train a competing model, the fake tools pollute that training data. It's gated behind a GrowthBook feature flag (tengu_anti_distill_fake_tool_injection) and only active for first-party CLI sessions.

### Second Anti-Distillation Mechanism
In betas.ts (lines 279-298), server-side connector-text summarization. When enabled, the API buffers the assistant's text between tool calls, summarizes it, and returns the summary with a cryptographic signature. On subsequent turns, the original text can be restored from the signature. If you're recording API traffic, you only get the summaries, not the full reasoning chain.

### Bypass
The fake tools injection requires ALL FOUR conditions:
1. The ANTI_DISTILLATION_CC compile-time flag
2. The cli entrypoint
3. A first-party API provider
4. The tengu_anti_distill_fake_tool_injection GrowthBook flag returning true

A MITM proxy stripping the anti_distillation field bypasses it entirely (injection is server-side, opt-in). Setting CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS to truthy disables the whole thing. Using a third-party API provider or SDK entrypoint means the check never fires. The connector-text summarization is Anthropic-internal-only (USER_TYPE === 'ant').

## Native Client Attestation (DRM for API Calls)
In system.ts (lines 59-95), API requests include a cch=00000 placeholder. Before the request leaves the process, Bun's native HTTP stack (written in Zig) overwrites those five zeros with a computed hash. The server validates the hash to confirm the request came from a real Claude Code binary.

They use a placeholder of the same length so the replacement doesn't change Content-Length or require buffer reallocation. The computation happens below the JavaScript runtime — invisible to JS layer.

### Attestation Controls
- Gated behind NATIVE_CLIENT_ATTESTATION compile-time flag
- cch=00000 only injected into x-anthropic-billing-header when flag is on
- Header disabled entirely by CLAUDE_CODE_ATTRIBUTION_HEADER=falsy
- Or remotely via GrowthBook killswitch (tengu_attribution_header)
- Only works inside official Bun binary — stock Bun/Node sends literal zeros
- Server-side _parse_cc_header "tolerates unknown extra fields" — validation may be forgiving

## 23 Bash Security Checks
bashSecurity.ts implements:
- 18 blocked Zsh builtins
- Defense against Zsh equals expansion (=curl bypassing permission checks)
- Unicode zero-width space injection detection
- IFS null-byte injection detection
- Malformed token bypass found during HackerOne review
