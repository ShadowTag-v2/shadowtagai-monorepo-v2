# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Compaction Prompt Templates — summary generation prompts.

Ported from: compact/prompt.ts
Reference: AGNT STATE B Spec P1.5

These prompts drive the LLM-based summarization used by L4 (full compaction).
The <analysis> block is a drafting scratchpad stripped by formatCompactSummary()
before the summary reaches context.

Two modes:
  - BASE: Scopes to "the conversation" (full compaction)
  - PARTIAL: Scopes to "recent messages" (partial compaction, recent-only)
"""

from __future__ import annotations

import re

# Aggressive no-tools preamble. On Sonnet 4.6+ adaptive-thinking models,
# the model sometimes attempts a tool call despite the weaker trailer.
# With maxTurns: 1, a denied tool call means no text output.
NO_TOOLS_PREAMBLE = """CRITICAL: Respond with TEXT ONLY. Do NOT call any tools.

- Do NOT use Read, Bash, Grep, Glob, Edit, Write, or ANY other tool.
- You already have all the context you need in the conversation above.
- Tool calls will be REJECTED and will waste your only turn — you will fail the task.
- Your entire response must be plain text: an <analysis> block followed by a <summary> block.

"""

NO_TOOLS_TRAILER = (
  "\n\nREMINDER: Do NOT call any tools. Respond with plain text only — "
  "an <analysis> block followed by a <summary> block. "
  "Tool calls will be rejected and you will fail the task."
)

DETAILED_ANALYSIS_BASE = """Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Chronologically analyze each message and section of the conversation. For each section thoroughly identify:
   - The user's explicit requests and intents
   - Your approach to addressing the user's requests
   - Key decisions, technical concepts and code patterns
   - Specific details like:
     - file names
     - full code snippets
     - function signatures
     - file edits
   - Errors that you ran into and how you fixed them
   - Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
2. Double-check for technical accuracy and completeness, addressing each required element thoroughly."""

DETAILED_ANALYSIS_PARTIAL = """Before providing your final summary, wrap your analysis in <analysis> tags to organize your thoughts and ensure you've covered all necessary points. In your analysis process:

1. Analyze the recent messages chronologically. For each section thoroughly identify:
   - The user's explicit requests and intents
   - Your approach to addressing the user's requests
   - Key decisions, technical concepts and code patterns
   - Specific details like:
     - file names
     - full code snippets
     - function signatures
     - file edits
   - Errors that you ran into and how you fixed them
   - Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
2. Double-check for technical accuracy and completeness, addressing each required element thoroughly."""

BASE_COMPACT_PROMPT = f"""Your task is to create a detailed summary of the conversation so far, paying close attention to the user's explicit requests and your previous actions.
This summary should be thorough in capturing technical details, code patterns, and architectural decisions that would be essential for continuing development work without losing context.

{DETAILED_ANALYSIS_BASE}

Your summary should include the following sections:

1. Primary Request and Intent: Capture all of the user's explicit requests and intents in detail
2. Key Technical Concepts: List all important technical concepts, technologies, and frameworks discussed.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Pay special attention to the most recent messages and include full code snippets where applicable and include a summary of why this file read or edit is important.
4. Errors and fixes: List all errors that you ran into, and how you fixed them. Pay special attention to specific user feedback that you received, especially if the user told you to do something differently.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages that are not tool results. These are critical for understanding the users' feedback and changing intent.
7. Pending Tasks: Outline any pending tasks that you have explicitly been asked to work on.
8. Current Work: Describe in detail precisely what was being worked on immediately before this summary request, paying special attention to the most recent messages from both user and assistant. Include file names and code snippets where applicable.
9. Optional Next Step: List the next step that you will take that is related to the most recent work you were doing. IMPORTANT: ensure that this step is DIRECTLY in line with the user's most recent explicit requests, and the task you were working on immediately before this summary request.

Please provide your summary based on the conversation so far, following this structure and ensuring precision and thoroughness in your response."""

PARTIAL_COMPACT_PROMPT = f"""Your task is to create a detailed summary of the RECENT portion of the conversation — the messages that follow earlier retained context. The earlier messages are being kept intact and do NOT need to be summarized. Focus your summary on what was discussed, learned, and accomplished in the recent messages only.

{DETAILED_ANALYSIS_PARTIAL}

Your summary should include the following sections:

1. Primary Request and Intent: Capture the user's explicit requests and intents from the recent messages
2. Key Technical Concepts: List important technical concepts, technologies, and frameworks discussed recently.
3. Files and Code Sections: Enumerate specific files and code sections examined, modified, or created. Include full code snippets where applicable.
4. Errors and fixes: List errors encountered and how they were fixed.
5. Problem Solving: Document problems solved and any ongoing troubleshooting efforts.
6. All user messages: List ALL user messages from the recent portion that are not tool results.
7. Pending Tasks: Outline any pending tasks from the recent messages.
8. Current Work: Describe precisely what was being worked on immediately before this summary request.
9. Optional Next Step: List the next step related to the most recent work. Include direct quotes from the most recent conversation.

Please provide your summary based on the RECENT messages only (after the retained earlier context), following this structure and ensuring precision and thoroughness in your response."""


def get_compact_prompt(custom_instructions: str | None = None) -> str:
  """Get the full compaction prompt.

  Args:
      custom_instructions: Optional custom summarization instructions.

  Returns:
      Complete prompt string with preamble and trailer.
  """
  prompt = NO_TOOLS_PREAMBLE + BASE_COMPACT_PROMPT
  if custom_instructions and custom_instructions.strip():
    prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"
  prompt += NO_TOOLS_TRAILER
  return prompt


def get_partial_compact_prompt(
  custom_instructions: str | None = None,
  *,
  direction: str = "from",
) -> str:
  """Get the partial compaction prompt.

  Args:
      custom_instructions: Optional custom summarization instructions.
      direction: 'from' (recent only) or 'up_to' (prefix summary).

  Returns:
      Complete prompt string.
  """
  template = PARTIAL_COMPACT_PROMPT  # 'up_to' variant omitted for brevity
  prompt = NO_TOOLS_PREAMBLE + template
  if custom_instructions and custom_instructions.strip():
    prompt += f"\n\nAdditional Instructions:\n{custom_instructions}"
  prompt += NO_TOOLS_TRAILER
  return prompt


def format_compact_summary(summary: str) -> str:
  """Format raw LLM summary by stripping <analysis> and cleaning <summary> tags.

  The <analysis> block is a drafting scratchpad that improves summary
  quality but has no informational value once the summary is written.

  Args:
      summary: Raw summary string from the LLM.

  Returns:
      Cleaned summary with analysis stripped and tags replaced.
  """
  formatted = summary

  # Strip analysis section
  formatted = re.sub(r"<analysis>[\s\S]*?</analysis>", "", formatted)

  # Extract and format summary section
  match = re.search(r"<summary>([\s\S]*?)</summary>", formatted)
  if match:
    content = match.group(1).strip()
    formatted = re.sub(
      r"<summary>[\s\S]*?</summary>",
      f"Summary:\n{content}",
      formatted,
    )

  # Clean up extra whitespace
  formatted = re.sub(r"\n\n+", "\n\n", formatted)
  return formatted.strip()


def get_compact_user_summary_message(
  summary: str,
  *,
  suppress_follow_up: bool = False,
  transcript_path: str | None = None,
  recent_preserved: bool = False,
) -> str:
  """Build the post-compaction summary message.

  Args:
      summary: The raw or formatted summary text.
      suppress_follow_up: If True, add continuation instructions.
      transcript_path: Path to full transcript for detail lookup.
      recent_preserved: Whether recent messages are kept verbatim.

  Returns:
      Formatted summary message for injection into context.
  """
  formatted = format_compact_summary(summary)

  base = (
    "This session is being continued from a previous conversation that "
    f"ran out of context. The summary below covers the earlier portion "
    f"of the conversation.\n\n{formatted}"
  )

  if transcript_path:
    base += (
      f"\n\nIf you need specific details from before compaction "
      f"(like exact code snippets, error messages, or content you "
      f"generated), read the full transcript at: {transcript_path}"
    )

  if recent_preserved:
    base += "\n\nRecent messages are preserved verbatim."

  if suppress_follow_up:
    base += (
      "\nContinue the conversation from where it left off without "
      "asking the user any further questions. Resume directly — do not "
      "acknowledge the summary, do not recap what was happening, do not "
      'preface with "I\'ll continue" or similar. Pick up the last task '
      "as if the break never happened."
    )

  return base
