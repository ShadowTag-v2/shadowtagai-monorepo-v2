/**
 * Layer 4: Dynamic Token Budget Allocation
 *
 * Mirrors autoCompact.ts:getEffectiveContextWindowSize() and the real
 * tokenBudget strategy: reserve output tokens, apply env overrides,
 * and split remaining context between history and tool output limits.
 *
 * Budget breakdown:
 *   20% reserved for model output (max_tokens)
 *   48% to history retention (60% of remaining 80%)
 *   32% to context/tools (40% of remaining 80%)
 *   maxToolOutputLength capped per COMPACTABLE_TOOLS spec
 */

export interface CompactionBudget {
  /** Max tokens for retained conversation history */
  historyLimit: number;
  /** Max total tokens for all context (history + attachments + system) */
  totalLimit: number;
  /** Max character length for individual tool result outputs */
  maxToolOutputLength: number;
  /** Tokens reserved for model output generation */
  reservedOutput: number;
  /** The effective context window used for this budget */
  effectiveWindow: number;
}

// p99.99 of compact summary output = 17,387 tokens (from autoCompact.ts)
const MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000;

// Default model context windows
// Sources: https://ai.google.dev/gemini-api/docs/models (verified 2026-05-02)
const MODEL_CONTEXT_WINDOWS: Record<string, number> = {
  // Claude family (200K)
  'claude-sonnet-4-20250514': 200_000,
  'claude-3-5-sonnet-20241022': 200_000,
  'claude-3-opus-20240229': 200_000,
  'claude-3-haiku-20240307': 200_000,
  'claude-opus-4-20250514': 200_000,

  // Gemini 3.x family (1M input tokens, 65K output)
  'gemini-3.1-pro-preview': 1_048_576,
  'gemini-3-flash-preview': 1_048_576,
  'gemini-3.1-flash-lite-preview': 1_048_576,

  // Gemini 2.5 family (1M input tokens, 65K output)
  'gemini-2.5-pro': 1_048_576,
  'gemini-2.5-flash': 1_048_576,
  'gemini-2.5-flash-lite': 1_048_576,

  // Gemini 2.0 family (deprecated, 1M)
  'gemini-2.0-flash': 1_048_576,
  'gemini-2.0-flash-lite': 1_048_576,

  // Gemini 1.5 family (legacy, 1M/2M)
  'gemini-1.5-pro': 2_097_152,
  'gemini-1.5-flash': 1_048_576,

  default: 200_000,
};

function getContextWindowForModel(model?: string): number {
  if (!model) return MODEL_CONTEXT_WINDOWS.default;
  return MODEL_CONTEXT_WINDOWS[model] ?? MODEL_CONTEXT_WINDOWS.default;
}

export function allocateTokenBudget(
  context: unknown,
  totalWindow?: number,
  model?: string,
): CompactionBudget {
  // Resolve effective context window
  let effectiveWindow = totalWindow ?? getContextWindowForModel(model);

  // Env override (from autoCompact.ts pattern)
  const autoCompactWindow = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW;
  if (autoCompactWindow) {
    const parsed = parseInt(autoCompactWindow, 10);
    if (!isNaN(parsed) && parsed > 0) {
      effectiveWindow = Math.min(effectiveWindow, parsed);
    }
  }

  // Reserve output tokens (min of model max_tokens and our summary cap)
  const reservedOutput = Math.min(Math.floor(effectiveWindow * 0.2), MAX_OUTPUT_TOKENS_FOR_SUMMARY);
  const availableContext = effectiveWindow - reservedOutput;

  // History gets 60% of available, remainder for system prompt + attachments
  const historyLimit = Math.floor(availableContext * 0.6);

  // Tool output length scales with context window, capped at 16K
  // Smaller windows get tighter tool output limits
  const maxToolOutputLength = Math.min(
    16_000,
    Math.max(4_000, Math.floor(availableContext * 0.05)),
  );

  return {
    historyLimit,
    totalLimit: availableContext,
    maxToolOutputLength,
    reservedOutput,
    effectiveWindow,
  };
}
