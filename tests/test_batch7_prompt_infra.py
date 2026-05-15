"""Batch 7 — Prompt Infrastructure comprehensive test suite.

Tests for:
1. prompt_sections — SystemPromptSection registry (memoized + volatile)
2. tool_limits — Tool result size limit constants + utility functions
3. xml_tags — XML tag registry + wrap/unwrap helpers
4. prompt_assembler — Dynamic system prompt assembly pipeline
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

# Ensure packages are importable.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))


# ============================================================================
# 1. PROMPT SECTIONS — Registry Tests
# ============================================================================


class TestPromptSectionRegistry:
  """Test the SystemPromptSection memoization and resolution."""

  def setup_method(self) -> None:
    """Clear cache before each test."""
    from packages.prompt_sections.registry import clear_system_prompt_sections

    clear_system_prompt_sections()

  def test_system_prompt_section_creation(self) -> None:
    from packages.prompt_sections.registry import system_prompt_section

    section = system_prompt_section("test", lambda: "hello")
    assert section.name == "test"
    assert section.cache_break is False

  def test_dangerous_uncached_section_creation(self) -> None:
    from packages.prompt_sections.registry import dangerous_uncached_section

    section = dangerous_uncached_section(
      "volatile",
      lambda: "dynamic value",
      "servers change between turns",
    )
    assert section.name == "volatile"
    assert section.cache_break is True

  def test_resolve_memoized_sections(self) -> None:
    from packages.prompt_sections.registry import (
      resolve_system_prompt_sections,
      system_prompt_section,
    )

    call_count = 0

    def compute() -> str:
      nonlocal call_count
      call_count += 1
      return f"value-{call_count}"

    section = system_prompt_section("memo_test", compute)

    # First resolution — computes.
    result1 = asyncio.run(resolve_system_prompt_sections([section]))
    assert result1 == ["value-1"]
    assert call_count == 1

    # Second resolution — returns cached.
    result2 = asyncio.run(resolve_system_prompt_sections([section]))
    assert result2 == ["value-1"]  # Same value (cached)
    assert call_count == 1  # Not recomputed

  def test_resolve_volatile_sections_recompute(self) -> None:
    from packages.prompt_sections.registry import (
      dangerous_uncached_section,
      resolve_system_prompt_sections,
    )

    call_count = 0

    def compute() -> str:
      nonlocal call_count
      call_count += 1
      return f"volatile-{call_count}"

    section = dangerous_uncached_section(
      "volatile_test",
      compute,
      "testing volatility",
    )

    result1 = asyncio.run(resolve_system_prompt_sections([section]))
    assert result1 == ["volatile-1"]

    # Volatile section recomputes every time.
    result2 = asyncio.run(resolve_system_prompt_sections([section]))
    assert result2 == ["volatile-2"]
    assert call_count == 2

  def test_resolve_none_returning_section(self) -> None:
    from packages.prompt_sections.registry import (
      resolve_system_prompt_sections,
      system_prompt_section,
    )

    section = system_prompt_section("none_test", lambda: None)
    result = asyncio.run(resolve_system_prompt_sections([section]))
    assert result == [None]

  def test_resolve_async_compute(self) -> None:
    from packages.prompt_sections.registry import (
      resolve_system_prompt_sections,
      system_prompt_section,
    )

    async def async_compute() -> str:
      return "async-value"

    section = system_prompt_section("async_test", async_compute)
    result = asyncio.run(resolve_system_prompt_sections([section]))
    assert result == ["async-value"]

  def test_clear_resets_cache(self) -> None:
    from packages.prompt_sections.registry import (
      clear_system_prompt_sections,
      get_section_cache,
      resolve_system_prompt_sections,
      system_prompt_section,
    )

    call_count = 0

    def compute() -> str:
      nonlocal call_count
      call_count += 1
      return f"v{call_count}"

    section = system_prompt_section("clear_test", compute)
    asyncio.run(resolve_system_prompt_sections([section]))
    assert call_count == 1
    assert "clear_test" in get_section_cache()

    # Clear resets everything.
    clear_system_prompt_sections()
    assert "clear_test" not in get_section_cache()

    # Next resolution recomputes.
    asyncio.run(resolve_system_prompt_sections([section]))
    assert call_count == 2

  def test_mixed_sections_resolution(self) -> None:
    from packages.prompt_sections.registry import (
      dangerous_uncached_section,
      resolve_system_prompt_sections,
      system_prompt_section,
    )

    counter_a = 0
    counter_b = 0

    def compute_a() -> str:
      nonlocal counter_a
      counter_a += 1
      return f"a-{counter_a}"

    def compute_b() -> str:
      nonlocal counter_b
      counter_b += 1
      return f"b-{counter_b}"

    sections = [
      system_prompt_section("cached_a", compute_a),
      dangerous_uncached_section("volatile_b", compute_b, "test"),
    ]

    result1 = asyncio.run(resolve_system_prompt_sections(sections))
    assert result1 == ["a-1", "b-1"]

    result2 = asyncio.run(resolve_system_prompt_sections(sections))
    assert result2 == ["a-1", "b-2"]  # a cached, b recomputed


# ============================================================================
# 2. TOOL LIMITS — Constants Tests
# ============================================================================


class TestToolLimits:
  """Test tool result size limit constants and utilities."""

  def test_default_max_result_size_chars(self) -> None:
    from packages.tool_limits import DEFAULT_MAX_RESULT_SIZE_CHARS

    assert DEFAULT_MAX_RESULT_SIZE_CHARS == 50_000

  def test_max_tool_result_tokens(self) -> None:
    from packages.tool_limits import MAX_TOOL_RESULT_TOKENS

    assert MAX_TOOL_RESULT_TOKENS == 100_000

  def test_bytes_per_token(self) -> None:
    from packages.tool_limits import BYTES_PER_TOKEN

    assert BYTES_PER_TOKEN == 4

  def test_max_tool_result_bytes_derived(self) -> None:
    from packages.tool_limits import (
      BYTES_PER_TOKEN,
      MAX_TOOL_RESULT_BYTES,
      MAX_TOOL_RESULT_TOKENS,
    )

    assert MAX_TOOL_RESULT_BYTES == MAX_TOOL_RESULT_TOKENS * BYTES_PER_TOKEN
    assert MAX_TOOL_RESULT_BYTES == 400_000

  def test_per_message_budget(self) -> None:
    from packages.tool_limits import MAX_TOOL_RESULTS_PER_MESSAGE_CHARS

    assert MAX_TOOL_RESULTS_PER_MESSAGE_CHARS == 200_000

  def test_tool_summary_max_length(self) -> None:
    from packages.tool_limits import TOOL_SUMMARY_MAX_LENGTH

    assert TOOL_SUMMARY_MAX_LENGTH == 50

  def test_image_limits(self) -> None:
    from packages.tool_limits import (
      API_IMAGE_MAX_BASE64_SIZE,
      IMAGE_MAX_HEIGHT,
      IMAGE_MAX_WIDTH,
      IMAGE_TARGET_RAW_SIZE,
    )

    assert API_IMAGE_MAX_BASE64_SIZE == 5 * 1024 * 1024
    assert IMAGE_TARGET_RAW_SIZE == (API_IMAGE_MAX_BASE64_SIZE * 3) // 4
    assert IMAGE_MAX_WIDTH == 2000
    assert IMAGE_MAX_HEIGHT == 2000

  def test_pdf_limits(self) -> None:
    from packages.tool_limits import (
      API_PDF_MAX_PAGES,
      PDF_AT_MENTION_INLINE_THRESHOLD,
      PDF_EXTRACT_SIZE_THRESHOLD,
      PDF_MAX_EXTRACT_SIZE,
      PDF_MAX_PAGES_PER_READ,
      PDF_TARGET_RAW_SIZE,
    )

    assert PDF_TARGET_RAW_SIZE == 20 * 1024 * 1024
    assert API_PDF_MAX_PAGES == 100
    assert PDF_EXTRACT_SIZE_THRESHOLD == 3 * 1024 * 1024
    assert PDF_MAX_EXTRACT_SIZE == 100 * 1024 * 1024
    assert PDF_MAX_PAGES_PER_READ == 20
    assert PDF_AT_MENTION_INLINE_THRESHOLD == 10

  def test_media_limit(self) -> None:
    from packages.tool_limits import API_MAX_MEDIA_PER_REQUEST

    assert API_MAX_MEDIA_PER_REQUEST == 100

  def test_is_result_over_limit_under(self) -> None:
    from packages.tool_limits import is_result_over_limit

    assert is_result_over_limit(49_999) is False
    assert is_result_over_limit(50_000) is False

  def test_is_result_over_limit_over(self) -> None:
    from packages.tool_limits import is_result_over_limit

    assert is_result_over_limit(50_001) is True
    assert is_result_over_limit(100_000) is True

  def test_is_result_over_limit_custom(self) -> None:
    from packages.tool_limits import is_result_over_limit

    # Custom limit lower than system cap — respected.
    assert is_result_over_limit(25_001, custom_limit=25_000) is True
    assert is_result_over_limit(24_999, custom_limit=25_000) is False

    # Custom limit higher than system cap — capped at system max.
    assert is_result_over_limit(50_001, custom_limit=100_000) is True

  def test_is_message_over_budget(self) -> None:
    from packages.tool_limits import is_message_over_budget

    assert is_message_over_budget(199_999) is False
    assert is_message_over_budget(200_000) is False
    assert is_message_over_budget(200_001) is True

  def test_is_message_over_budget_override(self) -> None:
    from packages.tool_limits import is_message_over_budget

    assert is_message_over_budget(150_001, budget_override=150_000) is True
    assert is_message_over_budget(149_999, budget_override=150_000) is False


# ============================================================================
# 3. XML TAGS — Tag Registry Tests
# ============================================================================


class TestXmlTags:
  """Test XML tag constants and utility functions."""

  def test_command_tags(self) -> None:
    from packages.xml_tags import (
      COMMAND_ARGS_TAG,
      COMMAND_MESSAGE_TAG,
      COMMAND_NAME_TAG,
    )

    assert COMMAND_NAME_TAG == "command-name"
    assert COMMAND_MESSAGE_TAG == "command-message"
    assert COMMAND_ARGS_TAG == "command-args"

  def test_terminal_output_tags(self) -> None:
    from packages.xml_tags import (
      BASH_INPUT_TAG,
      BASH_STDERR_TAG,
      BASH_STDOUT_TAG,
      LOCAL_COMMAND_CAVEAT_TAG,
      LOCAL_COMMAND_STDERR_TAG,
      LOCAL_COMMAND_STDOUT_TAG,
      TERMINAL_OUTPUT_TAGS,
    )

    assert BASH_INPUT_TAG == "bash-input"
    assert BASH_STDOUT_TAG == "bash-stdout"
    assert BASH_STDERR_TAG == "bash-stderr"
    assert len(TERMINAL_OUTPUT_TAGS) == 6
    assert BASH_INPUT_TAG in TERMINAL_OUTPUT_TAGS
    assert LOCAL_COMMAND_STDOUT_TAG in TERMINAL_OUTPUT_TAGS
    assert LOCAL_COMMAND_STDERR_TAG in TERMINAL_OUTPUT_TAGS
    assert LOCAL_COMMAND_CAVEAT_TAG in TERMINAL_OUTPUT_TAGS

  def test_task_notification_tags(self) -> None:
    from packages.xml_tags import (
      OUTPUT_FILE_TAG,
      STATUS_TAG,
      SUMMARY_TAG,
      TASK_ID_TAG,
      TASK_NOTIFICATION_TAG,
      TASK_TYPE_TAG,
      TOOL_USE_ID_TAG,
    )

    assert TASK_NOTIFICATION_TAG == "task-notification"
    assert TASK_ID_TAG == "task-id"
    assert TOOL_USE_ID_TAG == "tool-use-id"
    assert TASK_TYPE_TAG == "task-type"
    assert OUTPUT_FILE_TAG == "output-file"
    assert STATUS_TAG == "status"
    assert SUMMARY_TAG == "summary"

  def test_inter_agent_tags(self) -> None:
    from packages.xml_tags import (
      CHANNEL_MESSAGE_TAG,
      CHANNEL_TAG,
      CROSS_SESSION_MESSAGE_TAG,
      TEAMMATE_MESSAGE_TAG,
    )

    assert TEAMMATE_MESSAGE_TAG == "teammate-message"
    assert CHANNEL_MESSAGE_TAG == "channel-message"
    assert CHANNEL_TAG == "channel"
    assert CROSS_SESSION_MESSAGE_TAG == "cross-session-message"

  def test_planning_review_tags(self) -> None:
    from packages.xml_tags import (
      REMOTE_REVIEW_PROGRESS_TAG,
      REMOTE_REVIEW_TAG,
      ULTRAPLAN_TAG,
    )

    assert ULTRAPLAN_TAG == "ultraplan"
    assert REMOTE_REVIEW_TAG == "remote-review"
    assert REMOTE_REVIEW_PROGRESS_TAG == "remote-review-progress"

  def test_fork_tags(self) -> None:
    from packages.xml_tags import FORK_BOILERPLATE_TAG, FORK_DIRECTIVE_PREFIX

    assert FORK_BOILERPLATE_TAG == "fork-boilerplate"
    assert FORK_DIRECTIVE_PREFIX == "Your directive: "

  def test_common_help_args(self) -> None:
    from packages.xml_tags import COMMON_HELP_ARGS

    assert "help" in COMMON_HELP_ARGS
    assert "-h" in COMMON_HELP_ARGS
    assert "--help" in COMMON_HELP_ARGS

  def test_common_info_args(self) -> None:
    from packages.xml_tags import COMMON_INFO_ARGS

    assert "list" in COMMON_INFO_ARGS
    assert "status" in COMMON_INFO_ARGS
    assert "?" in COMMON_INFO_ARGS
    assert len(COMMON_INFO_ARGS) == 13

  def test_wrap_xml_tag(self) -> None:
    from packages.xml_tags import wrap_xml_tag

    result = wrap_xml_tag("bash-stdout", "hello world")
    assert result == "<bash-stdout>hello world</bash-stdout>"

  def test_wrap_xml_tag_empty_content(self) -> None:
    from packages.xml_tags import wrap_xml_tag

    result = wrap_xml_tag("status", "")
    assert result == "<status></status>"

  def test_wrap_xml_tag_multiline(self) -> None:
    from packages.xml_tags import wrap_xml_tag

    result = wrap_xml_tag("summary", "line1\nline2\nline3")
    assert result == "<summary>line1\nline2\nline3</summary>"

  def test_unwrap_xml_tag_present(self) -> None:
    from packages.xml_tags import unwrap_xml_tag

    text = "prefix <bash-stdout>output here</bash-stdout> suffix"
    result = unwrap_xml_tag("bash-stdout", text)
    assert result == "output here"

  def test_unwrap_xml_tag_absent(self) -> None:
    from packages.xml_tags import unwrap_xml_tag

    text = "no tags here"
    result = unwrap_xml_tag("bash-stdout", text)
    assert result is None

  def test_unwrap_xml_tag_multiline(self) -> None:
    from packages.xml_tags import unwrap_xml_tag

    text = "<summary>line1\nline2</summary>"
    result = unwrap_xml_tag("summary", text)
    assert result == "line1\nline2"

  def test_is_terminal_output_tag(self) -> None:
    from packages.xml_tags import is_terminal_output_tag

    assert is_terminal_output_tag("bash-input") is True
    assert is_terminal_output_tag("bash-stdout") is True
    assert is_terminal_output_tag("bash-stderr") is True
    assert is_terminal_output_tag("local-command-stdout") is True
    assert is_terminal_output_tag("unknown-tag") is False
    assert is_terminal_output_tag("teammate-message") is False


# ============================================================================
# 4. PROMPT ASSEMBLER — Assembly Pipeline Tests
# ============================================================================


class TestPromptAssembler:
  """Test the dynamic system prompt assembly pipeline."""

  def setup_method(self) -> None:
    """Clear section cache before each test."""
    from packages.prompt_sections.registry import clear_system_prompt_sections

    clear_system_prompt_sections()

  def test_system_prompt_dynamic_boundary_value(self) -> None:
    from packages.prompt_assembler import SYSTEM_PROMPT_DYNAMIC_BOUNDARY

    assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY == "__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__"

  def test_cyber_risk_instruction_content(self) -> None:
    from packages.prompt_assembler import CYBER_RISK_INSTRUCTION

    assert "Assist with authorized security testing" in CYBER_RISK_INSTRUCTION
    assert "supply chain compromise" in CYBER_RISK_INSTRUCTION
    assert "CTF challenges" in CYBER_RISK_INSTRUCTION

  def test_basic_assembly(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(
      cwd="/test/workspace",
      model_id="test-model",
      is_git_repo=True,
    )
    result = asyncio.run(assemble_system_prompt(config))

    # Should be a list of non-None strings.
    assert isinstance(result, list)
    assert all(isinstance(s, str) for s in result)
    assert len(result) > 0

  def test_boundary_marker_present(self) -> None:
    from packages.prompt_assembler import (
      SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
      PromptConfig,
      assemble_system_prompt,
    )

    config = PromptConfig(use_global_cache_scope=True)
    result = asyncio.run(assemble_system_prompt(config))
    assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY in result

  def test_boundary_marker_absent_when_disabled(self) -> None:
    from packages.prompt_assembler import (
      SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
      PromptConfig,
      assemble_system_prompt,
    )

    config = PromptConfig(use_global_cache_scope=False)
    result = asyncio.run(assemble_system_prompt(config))
    assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY not in result

  def test_static_before_dynamic(self) -> None:
    from packages.prompt_assembler import (
      SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
      PromptConfig,
      assemble_system_prompt,
    )

    config = PromptConfig(use_global_cache_scope=True)
    result = asyncio.run(assemble_system_prompt(config))

    boundary_idx = result.index(SYSTEM_PROMPT_DYNAMIC_BOUNDARY)

    # Static sections come before boundary.
    for section in result[:boundary_idx]:
      assert section != SYSTEM_PROMPT_DYNAMIC_BOUNDARY

    # Dynamic sections come after.
    assert boundary_idx > 0
    assert boundary_idx < len(result) - 1  # Not last element

  def test_cyber_risk_in_intro(self) -> None:
    from packages.prompt_assembler import (
      CYBER_RISK_INSTRUCTION,
      PromptConfig,
      assemble_system_prompt,
    )

    config = PromptConfig()
    result = asyncio.run(assemble_system_prompt(config))
    intro = result[0]
    assert CYBER_RISK_INSTRUCTION in intro

  def test_env_info_in_output(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(
      cwd="/my/test/dir",
      model_id="gemini-test",
      is_git_repo=False,
    )
    result = asyncio.run(assemble_system_prompt(config))
    full_prompt = "\n".join(result)
    assert "/my/test/dir" in full_prompt
    assert "gemini-test" in full_prompt

  def test_language_section_included(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(language_preference="Japanese")
    result = asyncio.run(assemble_system_prompt(config))
    full_prompt = "\n".join(result)
    assert "Japanese" in full_prompt

  def test_language_section_excluded_when_none(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(language_preference=None)
    result = asyncio.run(assemble_system_prompt(config))
    full_prompt = "\n".join(result)
    assert "# Language" not in full_prompt

  def test_mcp_instructions_included(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(mcp_instructions="Use Firebase MCP for all deploys.")
    result = asyncio.run(assemble_system_prompt(config))
    full_prompt = "\n".join(result)
    assert "Use Firebase MCP for all deploys." in full_prompt

  def test_memory_prompt_included(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig(memory_prompt="Previous session: deployed v2.1.")
    result = asyncio.run(assemble_system_prompt(config))
    full_prompt = "\n".join(result)
    assert "Previous session: deployed v2.1." in full_prompt

  def test_sync_assembly(self) -> None:
    from packages.prompt_assembler import PromptAssembler, PromptConfig

    config = PromptConfig(cwd="/sync/test")
    assembler = PromptAssembler(config)
    result = assembler.assemble_sync()
    assert isinstance(result, list)
    assert len(result) > 0

  def test_no_none_in_output(self) -> None:
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt

    config = PromptConfig()
    result = asyncio.run(assemble_system_prompt(config))
    assert None not in result


# ============================================================================
# CROSS-PACKAGE INTEGRATION TESTS
# ============================================================================


class TestCrossPackageIntegration:
  """Integration tests across Batch 7 packages."""

  def test_xml_tags_with_tool_limits_summary_truncation(self) -> None:
    from packages.tool_limits import TOOL_SUMMARY_MAX_LENGTH
    from packages.xml_tags import wrap_xml_tag

    long_summary = "A" * (TOOL_SUMMARY_MAX_LENGTH + 50)
    truncated = long_summary[:TOOL_SUMMARY_MAX_LENGTH]
    wrapped = wrap_xml_tag("summary", truncated)
    assert len(truncated) == TOOL_SUMMARY_MAX_LENGTH
    assert f"<summary>{truncated}</summary>" == wrapped

  def test_prompt_assembler_uses_section_registry(self) -> None:
    """Verify assembler delegates to the section registry correctly."""
    from packages.prompt_assembler import PromptConfig, assemble_system_prompt
    from packages.prompt_sections.registry import (
      clear_system_prompt_sections,
      get_section_cache,
    )

    clear_system_prompt_sections()
    config = PromptConfig(cwd="/integration/test")
    asyncio.run(assemble_system_prompt(config))

    # Cache should have entries from the dynamic sections.
    cache = get_section_cache()
    assert "env_info" in cache
    assert "language" in cache
    assert "memory" in cache

  def test_full_pipeline_e2e(self) -> None:
    """End-to-end: assemble prompt, check boundary, verify structure."""
    from packages.prompt_assembler import (
      CYBER_RISK_INSTRUCTION,
      SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
      PromptConfig,
      assemble_system_prompt,
    )
    from packages.prompt_sections.registry import clear_system_prompt_sections

    clear_system_prompt_sections()

    config = PromptConfig(
      cwd="/e2e/workspace",
      model_id="gemini-3.1-flash-lite-preview-thinking",
      is_git_repo=True,
      language_preference="English",
      mcp_instructions="Firebase MCP: Use for all deploys.",
      memory_prompt="Last session: completed Batch 6.",
      use_global_cache_scope=True,
    )

    result = asyncio.run(assemble_system_prompt(config))

    # Structure checks.
    assert len(result) > 5
    assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY in result
    boundary_idx = result.index(SYSTEM_PROMPT_DYNAMIC_BOUNDARY)

    # Static prefix.
    assert CYBER_RISK_INSTRUCTION in result[0]
    assert "# System" in result[1]

    # Dynamic suffix.
    full_dynamic = "\n".join(result[boundary_idx + 1 :])
    assert "/e2e/workspace" in full_dynamic
    assert "English" in full_dynamic
    assert "Last session: completed Batch 6." in full_dynamic
    assert "Firebase MCP: Use for all deploys." in full_dynamic


if __name__ == "__main__":
  pytest.main([__file__, "-v", "--tb=short"])
