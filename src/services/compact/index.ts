/**
 * 4-Layer Context Compaction Pipeline — Production Orchestrator
 *
 * Layer 1: Microcompact (apiMicrocompact.ts)
 *   → Tool output truncation, whitespace normalization, image compression
 *   → COMPACTABLE_TOOLS whitelist, tool_use/result pairing awareness
 *
 * Layer 2: Session Snip (historySnip.ts)
 *   → API-round-aware history trimming with group atomicity
 *   → Never orphans tool_use from tool_result
 *
 * Layer 3: Context Collapse (contextCollapse.ts)
 *   → Adjacent duplicate deduplication, error sequence compression
 *   → Content fingerprinting for efficient comparison
 *
 * Layer 4: Token Budget (tokenBudget.ts)
 *   → Model-aware context window allocation
 *   → Env override support, output token reservation
 *
 * Circuit breaker: MAX_CONSECUTIVE_FAILURES prevents infinite retry loops
 * when context is irrecoverably over limit (mirrors autoCompact.ts pattern).
 */

import { apiMicrocompact } from './apiMicrocompact.js';
import { contextCollapse } from './contextCollapse.js';
import { historySnip } from './historySnip.js';
import { allocateTokenBudget, type CompactionBudget } from './tokenBudget.js';

// Circuit breaker: stop retrying after N consecutive failures
const MAX_CONSECUTIVE_FAILURES = 3;
let consecutiveFailures = 0;

export interface CompactionPipelineResult {
  messages: Record<string, unknown>[];
  budget: CompactionBudget;
  layersApplied: string[];
  circuitBroken: boolean;
}

/**
 * Run the full 4-layer compaction pipeline.
 *
 * @param messages - Raw conversation messages
 * @param totalWindow - Total context window size (default: 200K)
 * @param model - Model identifier for context window lookup
 * @returns Compacted messages with budget metadata
 */
export async function runCompactionPipeline(
  messages: Record<string, unknown>[],
  totalWindow?: number,
  model?: string,
): Promise<CompactionPipelineResult> {
  const layersApplied: string[] = [];

  // Circuit breaker check
  if (consecutiveFailures >= MAX_CONSECUTIVE_FAILURES) {
    return {
      messages,
      budget: allocateTokenBudget(messages, totalWindow, model),
      layersApplied: [],
      circuitBroken: true,
    };
  }

  try {
    // Layer 4: Compute budget first (drives all other layers)
    const budget = allocateTokenBudget(messages, totalWindow, model);
    layersApplied.push('tokenBudget');

    // Layer 1: Strip and truncate tool outputs
    let compacted = apiMicrocompact(messages, budget.maxToolOutputLength);
    layersApplied.push('apiMicrocompact');

    // Layer 2: Snip old conversation history by API-round groups
    compacted = historySnip(compacted, budget.historyLimit);
    layersApplied.push('historySnip');

    // Layer 3: Collapse adjacent duplicates and error sequences
    compacted = contextCollapse(compacted, budget.totalLimit);
    layersApplied.push('contextCollapse');

    // Success — reset circuit breaker
    consecutiveFailures = 0;

    return { messages: compacted, budget, layersApplied, circuitBroken: false };
  } catch {
    consecutiveFailures++;
    return {
      messages,
      budget: allocateTokenBudget(messages, totalWindow, model),
      layersApplied,
      circuitBroken: consecutiveFailures >= MAX_CONSECUTIVE_FAILURES,
    };
  }
}

/** Reset circuit breaker (exposed for testing and post-compact cleanup) */
export function resetCompactionCircuitBreaker(): void {
  consecutiveFailures = 0;
}

export type { CompactionBudget };
export { allocateTokenBudget, apiMicrocompact, contextCollapse, historySnip };
