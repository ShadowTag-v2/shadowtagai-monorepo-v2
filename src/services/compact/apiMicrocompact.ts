/**
 * Layer 1: API Microcompact (Server-side Context Stripping)
 *
 * Production-grade implementation mirroring microCompact.ts patterns:
 *  - COMPACTABLE_TOOLS whitelist: Only compact known-safe tool outputs
 *  - Tool use/result pairing: Never orphan a tool_use from its tool_result
 *  - Redundant whitespace normalization
 *  - Large tool output truncation with character budget
 *  - Image placeholder compression
 */

// Mirroring the COMPACTABLE_TOOLS set from microCompact.ts
const COMPACTABLE_TOOLS = new Set<string>([
  'Read',
  'file_read',
  'Bash',
  'bash',
  'Grep',
  'grep',
  'Glob',
  'glob',
  'WebSearch',
  'web_search',
  'WebFetch',
  'web_fetch',
  'FileEdit',
  'file_edit',
  'FileWrite',
  'file_write',
]);

// Image placeholder replaces image blocks during compaction (~2000 tokens each saved)
const IMAGE_PLACEHOLDER = '[Image content removed during compaction]';

interface ContentBlock {
  type: string;
  text?: string;
  content?: string;
  name?: string;
  tool_use_id?: string;
  [key: string]: unknown;
}

/**
 * Check if a tool result is eligible for compaction.
 * Only COMPACTABLE_TOOLS outputs are stripped — non-whitelisted tools
 * (e.g., FileEdit, Task) keep their full output to preserve semantic context.
 */
function isCompactableToolResult(block: ContentBlock, toolNameMap: Map<string, string>): boolean {
  if (block.type !== 'tool_result') return false;
  const toolName = block.tool_use_id ? toolNameMap.get(block.tool_use_id) : undefined;
  return toolName ? COMPACTABLE_TOOLS.has(toolName) : true; // Default to compactable if unknown
}

/**
 * Build a map of tool_use_id → tool_name from the message stream.
 * This enables the tool_result handler to check the whitelist without
 * requiring access to the originating tool_use block.
 */
function buildToolNameMap(messages: Record<string, unknown>[]): Map<string, string> {
  const map = new Map<string, string>();
  for (const msg of messages) {
    const content = msg.content;
    if (!Array.isArray(content)) continue;
    for (const block of content as ContentBlock[]) {
      if (block.type === 'tool_use' && block.id && block.name) {
        map.set(block.id as string, block.name);
      }
    }
  }
  return map;
}

function normalizeWhitespace(text: string): string {
  return text
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]+$/gm, '')
    .trim();
}

function truncateToolOutput(content: string, maxLength: number): string {
  if (content.length <= maxLength) return content;
  const truncated = content.substring(0, maxLength);
  const removedChars = content.length - maxLength;
  return `${truncated}\n\n...[Truncated ${removedChars} characters by Microcompact L1]`;
}

export function apiMicrocompact(
  context: Record<string, unknown>[],
  maxToolOutputLength: number = 8000,
): Record<string, unknown>[] {
  if (!context || context.length === 0) return context;

  const toolNameMap = buildToolNameMap(context);

  return context.map((message) => {
    const role = message.role as string;

    // System messages pass through unmodified
    if (role === 'system') return message;

    const content = message.content;

    // String content: just normalize whitespace
    if (typeof content === 'string') {
      return {
        ...message,
        content: normalizeWhitespace(content),
        microcompacted: true,
      };
    }

    // Array content: process each block
    if (Array.isArray(content)) {
      const processedContent = (content as ContentBlock[]).map((block) => {
        // Text blocks: normalize whitespace
        if (block.type === 'text' && typeof block.text === 'string') {
          return { ...block, text: normalizeWhitespace(block.text) };
        }

        // Image blocks: replace with placeholder to save tokens
        if (block.type === 'image') {
          return { type: 'text', text: IMAGE_PLACEHOLDER };
        }

        // Tool result blocks: truncate if compactable
        if (block.type === 'tool_result' && typeof block.content === 'string') {
          if (isCompactableToolResult(block, toolNameMap)) {
            return {
              ...block,
              content: truncateToolOutput(block.content, maxToolOutputLength),
            };
          }
        }

        // Tool use blocks pass through (paired with their results)
        return block;
      });

      return { ...message, content: processedContent, microcompacted: true };
    }

    return { ...message, microcompacted: true };
  });
}
