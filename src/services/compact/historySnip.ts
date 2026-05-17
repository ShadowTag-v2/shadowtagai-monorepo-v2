/**
 * Layer 2: Conversation History Snipping
 *
 * Production-grade implementation integrating grouping.ts API-round boundaries:
 *  - Groups messages by API round-trips (assistant-id boundaries)
 *  - Drops entire groups (never orphans a tool_use from its tool_result)
 *  - Preserves the most recent groups first (reverse chronological)
 *  - Inserts a system-level snip indicator at the trim boundary
 *  - Token estimation: 4 chars ≈ 1 token (same as production heuristic)
 */

interface MessageLike {
  role?: string;
  type?: string;
  content?: unknown;
  message?: { id?: string };
  historySnipped?: boolean;
  [key: string]: unknown;
}

interface SnipResult {
  messages: MessageLike[];
  snippedCount: number;
  snippedGroups: number;
}

function estimateTokens(msg: MessageLike): number {
  const serialized = JSON.stringify(msg);
  return Math.ceil(serialized.length / 4);
}

/**
 * Group messages by API round-trip boundaries.
 * A new group starts when an assistant message with a different message.id appears.
 * This mirrors grouping.ts:groupMessagesByApiRound() logic.
 */
function groupByApiRound(messages: MessageLike[]): MessageLike[][] {
  const groups: MessageLike[][] = [];
  let current: MessageLike[] = [];
  let lastAssistantId: string | undefined;

  for (const msg of messages) {
    const isAssistant = msg.role === "assistant" || msg.type === "assistant";
    const msgId = msg.message?.id;

    if (isAssistant && msgId !== lastAssistantId && current.length > 0) {
      groups.push(current);
      current = [msg];
    } else {
      current.push(msg);
    }

    if (isAssistant && msgId) {
      lastAssistantId = msgId;
    }
  }

  if (current.length > 0) {
    groups.push(current);
  }

  return groups;
}

export function historySnip(messages: MessageLike[], historyLimit: number): MessageLike[] {
  if (messages.length === 0) return messages;

  const groups = groupByApiRound(messages);

  // If only one group, keep everything (can't snip the only round)
  if (groups.length <= 1) return messages;

  // Traverse groups in reverse (keep most recent first)
  let currentTokens = 0;
  const keptGroups: MessageLike[][] = [];
  let snippedMessageCount = 0;
  let snippedGroupCount = 0;

  for (let i = groups.length - 1; i >= 0; i--) {
    const group = groups[i];
    const groupTokens = group.reduce((sum, msg) => sum + estimateTokens(msg), 0);

    if (currentTokens + groupTokens > historyLimit && i !== groups.length - 1) {
      // This group would exceed the budget — snip everything from here backwards
      snippedGroupCount = i + 1;
      for (let j = 0; j <= i; j++) {
        snippedMessageCount += groups[j].length;
      }
      break;
    }

    currentTokens += groupTokens;
    keptGroups.unshift(group);
  }

  // If nothing was snipped, return original
  if (snippedMessageCount === 0) return messages;

  // Build result with snip indicator at the boundary
  const snipIndicator: MessageLike = {
    role: "system",
    content: `[System: ${snippedMessageCount} older messages across ${snippedGroupCount} API rounds were snipped to preserve context window budget. ${currentTokens} tokens retained.]`,
    historySnipped: true,
  };

  const result = [snipIndicator];
  for (const group of keptGroups) {
    result.push(...group);
  }

  return result;
}

export { groupByApiRound, type SnipResult };
