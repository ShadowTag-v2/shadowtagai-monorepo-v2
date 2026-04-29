# Rule 14: Terminal Rendering & Internal Architecture

## Terminal Rendering Engine
ink/screen.ts and ink/optimizer.ts borrow game-engine techniques:
- Int32Array-backed ASCII char pool
- Bitmask-encoded style metadata
- Patch optimizer that merges cursor moves and cancels hide/show pairs
- Self-evicting line-width cache (~50x reduction in stringWidth calls during token streaming)

Seems like overkill until you remember these things stream tokens one at a time.

## Core Architecture
Claude Code is a monolithic TypeScript CLI:
- Runtime: Bun (not Node.js) — Anthropic acquired Bun end of 2025
- UI: React + Ink (terminal rendering)
- Core files: QueryEngine.ts (46K lines), Tool.ts (29K lines), commands.ts (25K lines)
- Tools: ~40 built-in
- Commands: ~85 slash commands
- Model access: Anthropic only (Claude models)

The core loop: User message → API call → Parse response → Execute tools → Feed results back → Repeat

## The Rough Spots
- print.ts is 5,594 lines with a single function spanning 3,167 lines and 12 levels of nesting
- They use Axios for HTTP (compromised on npm with malicious RAT versions)
- A Bun bug (oven-sh/bun#28001) reports source maps served in production mode even though Bun docs say disabled — filed March 11, still open — this likely caused the leak

## The Source Map Leak Itself
The leak is a configuration oversight: shipping source map files alongside the production code on npm. These .map files let anyone translate the scrambled, efficient code back into the original, human-readable version. Not a hack — a build pipeline failure.

The cause: nobody set sourceMap: false in the build config. One-line tsconfig fix. The Bun bug (oven-sh/bun#28001) may have contributed — source maps served in production mode despite docs saying they should be disabled.

This is Anthropic's second accidental exposure in a week (model spec leak days prior). The package was pulled but not before widely mirrored.

## What Makes This Different From Open Source
Google's Gemini CLI and OpenAI's Codex are open source — but they open-sourced their agent SDK (a toolkit), not the full internal wiring of their flagship product.

The real damage isn't the code — it's the feature flags. COR.KAIROS, anti-distillation mechanisms — these are product roadmap details competitors can see and react to. The code can be refactored. The strategic surprise can't be un-leaked.

## The Meta-Lesson
"Accidentally shipping your source map to npm is the kind of mistake that sounds impossible until you remember that a significant portion of the codebase was probably written by the AI you are shipping."
