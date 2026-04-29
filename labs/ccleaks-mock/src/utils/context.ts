// src/utils/context.ts

export function getMaxContextTokens(): number {
  if (process.env.CLAUDE_CODE_MAX_CONTEXT_TOKENS) {
    return parseInt(process.env.CLAUDE_CODE_MAX_CONTEXT_TOKENS, 10);
  }

  // force-disabled with CLAUDE_CODE_DISABLE_1M_CONTEXT for healthcare compliance
  if (process.env.CLAUDE_CODE_DISABLE_1M_CONTEXT === '1') {
    return 200000;
  }

  return 1000000; // 1M context window
}
