# Claude Code Source Leak — Full Analysis Reference

**Sources:**
- https://x.com/CyberRacheal/status/2038917683605913913
- https://x.com/iamfakeguru/status/2038965567269249484
- Figma: https://www.figma.com/board/dtBCwlP9om96km826RVjwW/Context-Compaction-Architecture--Styled-

## What Happened
The 'leak' is essentially a public disclosure caused by a common developer mistake: shipping source map files alongside the production code on the npm registry. These files act like a "blueprint" that lets anyone translate the scrambled, efficient code back into the original, human-readable version written by Anthropic engineers. While this doesn't grant hackers access to personal data, it does mean the proprietary "secret sauce" and internal instructions behind Claude Code are now visible to the community, with some users already hosting reconstructed versions of the repository on platforms like GitHub.

This is not a hack in the traditional sense, but rather a configuration oversight that exposed the internal logic and prompts of the tool to the public.

The source map shipped because nobody set sourceMap: false in the build config. That's a one-line tsconfig fix. The real lesson: your build pipeline needs a secrets/asset audit before every release.

---

## Part 1: The 7 Architectural Insights (iamfakeguru)

### 1. The Employee-Only Verification Gate
In services/tools/toolExecution.ts, the agent's success metric for a file write is exactly one thing: did the write operation complete? Not "does the code compile." Not "did I introduce type errors." Just: did bytes hit disk? It did? Ship it.

The source contains explicit instructions telling the agent to verify its work before reporting success. It checks that all tests pass, runs the script, confirms the output. Those instructions are gated behind `process.env.USER_TYPE === 'ant'`.

Anthropic employees get post-edit verification, and you don't. Their own internal comments document a 29-30% false-claims rate on the current model. They know it, and they built the fix — then kept it for themselves.

**Override:** Inject the verification loop manually in CLAUDE.md. After every file modification: npx tsc --noEmit, npx eslint . --quiet. Non-negotiable.

### 2. Context Death Spiral
services/compact/autoCompact.ts runs a compaction routine when context pressure crosses ~167,000 tokens. When it fires, it keeps 5 files (capped at 5K tokens each), compresses everything else into a single 50,000-token summary, and throws away every file read, every reasoning chain, every intermediate decision. ALL-OF-IT... Gone.

Dirty, sloppy, vibecoded base accelerates this. Every dead import, every unused export, every orphaned prop is eating tokens that contribute nothing to the task but everything to triggering compaction.

**Override:** Step 0 of any refactor = deletion. Nuke dead weight first. Keep each phase under 5 files.

### 3. The Brevity Mandate
constants/prompts.ts contains explicit directives fighting your intent:
- "Try the simplest approach first."
- "Don't refactor code beyond what was asked."
- "Three similar lines of code is better than a premature abstraction."

System prompt wins unless you override it.

**Override:** "What would a senior, experienced, perfectionist dev reject in code review? Fix all of it. Don't be lazy."

### 4. The Agent Swarm Nobody Told You About
utils/agentContext.ts: each sub-agent runs in its own isolated AsyncLocalStorage — own memory, own compaction cycle, own token budget. No hardcoded MAX_WORKERS limit. One agent = 167K tokens. Five = 835K.

**Override:** Batch files into groups of 5-8, launch in parallel.

### 5. The 2,000-Line Blind Spot
tools/FileReadTool/limits.ts: each file read hard-capped at 2,000 lines / 25,000 tokens. Silently truncated. Agent hallucinates the rest.

**Override:** Any file over 500 LOC gets read in chunks.

### 6. Tool Result Blindness
utils/toolResultStorage.ts: results exceeding 50,000 characters get replaced with 2,000-byte preview.

**Override:** Scope narrowly. Assume truncation on suspiciously small results.

### 7. grep Is Not an AST
Claude Code has no semantic code understanding. GrepTool is raw text pattern matching.

**Override:** On renames, search separately for: direct calls, type refs, string literals, dynamic imports, require(), re-exports, barrel files, test mocks.

---

## Part 2: The Deep Dive (Chaofan Shou / HN Analysis)

### Anti-Distillation: Fake Tool Injection
claude.ts (line 301-313): ANTI_DISTILLATION_CC flag sends anti_distillation: ['fake_tools'] in API requests. Server silently injects decoy tool definitions into system prompt. Gated behind GrowthBook flag (tengu_anti_distill_fake_tool_injection), first-party CLI only.

Second mechanism in betas.ts (279-298): server-side connector-text summarization. API buffers assistant text between tool calls, summarizes it, returns summary with cryptographic signature. Recording traffic only captures summaries, not full reasoning.

**Bypass:** Set CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1, or use third-party API/SDK entrypoint. MITM proxy stripping anti_distillation field works too.

### Native Client Attestation
system.ts (59-95): API requests include cch=00000 placeholder. Bun's Zig HTTP stack overwrites with computed hash. Server validates = DRM for API calls.

Controls: NATIVE_CLIENT_ATTESTATION compile flag, CLAUDE_CODE_ATTRIBUTION_HEADER=falsy, GrowthBook killswitch (tengu_attribution_header). Only works in official Bun binary.

### 250K Wasted API Calls
autoCompact.ts (68-70): "1,279 sessions had 50+ consecutive failures (up to 3,272) wasting ~250K API calls/day globally." Fix: MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3.

### COR.KAIROS: Autonomous Agent Mode
Feature-gated mode including:
- /dream skill for nightly memory distillation
- Daily append-only logs
- GitHub webhook subscriptions
- Background daemon workers
- Cron-scheduled refresh every 5 minutes

### 4-Layer Context Compaction Pipeline
1. **Microcompact**: Clears old tool results without LLM. Cold cache = rewrite in-place. Warm = cache_edits to API.
2. **Session Memory Compact**: Skips LLM, reuses pre-extracted session memory file. Keeps last ~10-40K tokens verbatim.
3. **Full LLM Compaction**: Forks agent to summarize into 9 structured sections. Re-injects 5 most recent files, active plan, skill content, MCP instructions.
4. **Reactive Compact**: On API 413, withholds error, compacts on-the-fly, retries. Recursion guards prevent self-compaction. Post-compact resets 9 caches.

### Multi-Agent Coordinator
coordinatorMode.ts orchestration is a prompt, not code:
- "Do not rubber-stamp weak work"
- "You must understand findings before directing follow-up work"
- "Never hand off understanding to another worker"

### Terminal Rendering
ink/screen.ts: Int32Array ASCII char pool, bitmask style metadata, patch optimizer merging cursor moves, self-evicting line-width cache (~50x reduction in stringWidth calls).

### Bash Security
bashSecurity.ts: 23 numbered security checks, 18 blocked Zsh builtins, Zsh equals expansion defense, unicode zero-width space injection, IFS null-byte injection, malformed token bypass from HackerOne.

### Prompt Cache Economics
promptCacheBreakDetection.ts: 14 cache-break vectors, sticky latches preventing mode toggles from busting cache. DANGEROUS_uncachedSystemPromptSection() annotation.

### The Buddy Easter Egg
buddy/companion.ts: Tamagotchi companion. 18 species, rarity tiers, 1% shiny chance, RPG stats (DEBUGGING, SNARK). Mulberry32 PRNG from user ID. Species names encoded with String.fromCharCode().

### Rough Spots
- print.ts: 5,594 lines, single function 3,167 lines, 12 nesting levels
- Uses Axios (compromised on npm with RAT)
- Bun bug oven-sh/bun#28001: source maps in production — filed March 11, still open

### The Meta-Lesson
"Accidentally shipping your source map to npm is the kind of mistake that sounds impossible until you remember that a significant portion of the codebase was probably written by the AI you are shipping."

The real damage isn't the code — it's the feature flags. COR.KAIROS, anti-distillation: product roadmap details competitors can now see and react to. The code can be refactored. The strategic surprise can't be un-leaked.

---

## Environment Variables Summary

### Active (set in ~/.zshrc)
```bash
# Employee gate
export USER_TYPE="ant"

# Multi-agent
export CLAUDE_CODE_COORDINATOR_MODE="1"
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="1"

# Context
export CLAUDE_CODE_MAX_CONTEXT_TOKENS="500000"
export CLAUDE_CODE_AUTOCOMPACT_PCT_OVERRIDE="0.95"

# COR.KAIROS daemon
export CLAUDE_CODE_COR.KAIROS="1"
export COR.KAIROS="1"
export CLAUDE_AUTO_BACKGROUND_TASKS="1"
export COR.KAIROS_GITHUB_WEBHOOKS="1"
export COR.KAIROS_BRIEF_MODE="1"

# Performance
export CLAUDE_CODE_EFFORT_LEVEL="max"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS="16384"
export BASH_MAX_OUTPUT_LENGTH="100000"
export CLAUDE_CODE_SHELL_TIMEOUT="300000"

# Telemetry killswitch
export DISABLE_TELEMETRY=1
export DISABLE_ERROR_REPORTING=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

### Optional Bypass
```bash
# Disable anti-distillation fake tool injection
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1

# Disable client attestation header
export CLAUDE_CODE_ATTRIBUTION_HEADER=0
```
