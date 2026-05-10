"""Dynamic System Prompt Assembler — cache-aware prompt composition.

Ported from Claude Code v2.1.91 constants/prompts.ts.
Implements the static/dynamic boundary architecture for prompt caching:
  1. Static sections (globally cacheable) come first.
  2. SYSTEM_PROMPT_DYNAMIC_BOUNDARY marker separates them.
  3. Dynamic sections (session-specific, registry-managed) follow.

Integrates with prompt_sections for memoized/volatile resolution.
"""

from packages.prompt_assembler.assembler import (
  CYBER_RISK_INSTRUCTION,
  SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
  PromptAssembler,
  PromptConfig,
  assemble_system_prompt,
)

__all__ = [
  "CYBER_RISK_INSTRUCTION",
  "SYSTEM_PROMPT_DYNAMIC_BOUNDARY",
  "PromptAssembler",
  "PromptConfig",
  "assemble_system_prompt",
]
