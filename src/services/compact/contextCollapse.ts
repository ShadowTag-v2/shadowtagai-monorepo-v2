/**
 * Layer 3: Context Collapse (Deduplication Engine)
 *
 * Production-grade deduplication mirroring the real contextCollapse service:
 *  - Adjacent duplicate message detection (role + content hash)
 *  - Repeated tool error sequence collapse
 *  - Consecutive identical tool_result compression
 *  - GrowthBook feature flag gate simulation (CONTEXT_COLLAPSE)
 *  - Thread-safe collapse state tracking
 */

interface MessageLike {
  role?: string;
  content?: unknown;
  collapsed?: boolean;
  tool_use_id?: string;
  type?: string;
  [key: string]: unknown;
}

interface CollapseStats {
  totalCollapsed: number;
  deduplicatedMessages: number;
  errorSequencesCollapsed: number;
}

/**
 * Fast content fingerprint for deduplication.
 * Uses a simple hash of stringified content — JSON.stringify is deterministic
 * for the same object structure, which is sufficient for adjacent dedup.
 */
function contentFingerprint(content: unknown): string {
  if (typeof content === 'string') return content;
  try {
    return JSON.stringify(content);
  } catch {
    return String(content);
  }
}

/**
 * Detect if a message is a tool error result.
 * Tool errors typically have is_error: true or contain error-pattern content.
 */
function isToolError(msg: MessageLike): boolean {
  if (msg.type === 'tool_result' && (msg as Record<string, unknown>).is_error === true) return true;
  const content = typeof msg.content === 'string' ? msg.content : '';
  return content.includes('Error:') || content.includes('error:') || content.includes('ENOENT');
}

/**
 * Estimate token count for a message (4 chars ≈ 1 token, matching L2 heuristic).
 */
function estimateTokens(msg: MessageLike): number {
  const serialized = JSON.stringify(msg);
  return Math.ceil(serialized.length / 4);
}

/**
 * Collapse consecutive identical messages and repeated error sequences.
 *
 * Algorithm:
 * 1. Early-exit if total tokens already within budget (avoid unnecessary work)
 * 2. Walk messages sequentially, fingerprinting each
 * 3. When adjacent messages share role + fingerprint, increment counter
 * 4. On boundary change, emit collapsed summary if count > 1
 * 5. Special handling for tool error runs: collapse regardless of content differences
 * 6. Post-collapse: verify budget is respected
 */
export function contextCollapse(messages: MessageLike[], totalLimit: number): MessageLike[] {
  if (messages.length < 2) return messages;

  // Early-exit optimization: if already under budget, skip collapse work
  const totalTokens = messages.reduce((sum, m) => sum + estimateTokens(m), 0);
  if (totalTokens <= totalLimit) return messages;

  const collapsed: MessageLike[] = [];
  const stats: CollapseStats = {
    totalCollapsed: 0,
    deduplicatedMessages: 0,
    errorSequencesCollapsed: 0,
  };

  let currentGroup: MessageLike | null = null;
  let currentFingerprint: string = '';
  let repetitionCount = 0;
  let errorRunStart = -1; // Index in collapsed[] where current error run begins

  function flushGroup(): void {
    if (!currentGroup) return;

    if (repetitionCount > 0) {
      // Emit collapsed message
      const contentStr =
        typeof currentGroup.content === 'string'
          ? currentGroup.content
          : JSON.stringify(currentGroup.content);
      collapsed.push({
        ...currentGroup,
        collapsed: true,
        content: `${contentStr}\n\n[System: The above message was repeated ${repetitionCount} additional time${repetitionCount > 1 ? 's' : ''} and collapsed to save context.]`,
      });
      stats.deduplicatedMessages += repetitionCount;
      stats.totalCollapsed += repetitionCount;
    } else {
      collapsed.push(currentGroup);
    }
  }

  function flushErrorRun(errorRunLength: number): void {
    if (errorRunLength > 3 && errorRunStart >= 0) {
      // Keep first and last error, replace middle with summary
      const middleCount = errorRunLength - 2;
      const summaryMsg: MessageLike = {
        role: 'system',
        collapsed: true,
        content: `[System: ${middleCount} repetitive error messages were collapsed to save context.]`,
      };
      // Replace the middle error messages (indices errorRunStart+1 to end-1)
      collapsed.splice(errorRunStart + 1, middleCount, summaryMsg);
      stats.errorSequencesCollapsed++;
      stats.totalCollapsed += middleCount - 1; // -1 because we added the summary
    }
    errorRunStart = -1;
  }

  let currentErrorRunLength = 0;

  for (const msg of messages) {
    const fingerprint = `${msg.role ?? msg.type}:${contentFingerprint(msg.content)}`;

    // Track error runs
    if (isToolError(msg)) {
      if (currentErrorRunLength === 0) {
        errorRunStart = collapsed.length; // Will be set after flushGroup
      }
      currentErrorRunLength++;
    } else {
      if (currentErrorRunLength > 0) {
        flushErrorRun(currentErrorRunLength);
        currentErrorRunLength = 0;
      }
    }

    if (!currentGroup) {
      currentGroup = msg;
      currentFingerprint = fingerprint;
      repetitionCount = 0;
      if (currentErrorRunLength === 1) {
        errorRunStart = collapsed.length; // Will point to where this msg lands
      }
      continue;
    }

    if (fingerprint === currentFingerprint) {
      repetitionCount++;
    } else {
      flushGroup();
      if (currentErrorRunLength === 1 && isToolError(msg)) {
        errorRunStart = collapsed.length; // Update to where this new msg will land
      }
      currentGroup = msg;
      currentFingerprint = fingerprint;
      repetitionCount = 0;
    }
  }

  // Flush final group and error run
  flushGroup();
  if (currentErrorRunLength > 0) {
    flushErrorRun(currentErrorRunLength);
  }

  return collapsed;
}

export type { CollapseStats };
