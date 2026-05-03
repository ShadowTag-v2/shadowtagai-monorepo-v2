"""Batch 4 Service Port Tests — thinking_config, token_estimation,
prompt_sections, prompt_assembler, policy_limits.

Validates parity with Claude Code v2.1.91 TypeScript implementations.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest

# ── token_estimation ──────────────────────────────────────────────
from packages.token_estimation.estimator import (
    DEFAULT_BYTES_PER_TOKEN,
    IMAGE_MAX_TOKEN_SIZE,
    bytes_per_token_for_file_type,
    rough_token_estimate,
    rough_token_estimate_for_block,
    rough_token_estimate_for_content,
    rough_token_estimate_for_file_type,
    rough_token_estimate_for_messages,
)

# ── thinking_config ───────────────────────────────────────────────
from packages.thinking_config import (
    ThinkingConfig,
    find_thinking_trigger_positions,
    has_ultrathink_keyword,
    is_ultrathink_enabled,
    model_supports_adaptive_thinking,
    model_supports_thinking,
    should_enable_thinking_by_default,
)

# ── prompt_sections ───────────────────────────────────────────────
from packages.prompt_sections.registry import (
    clear_system_prompt_sections,
    dangerous_uncached_section,
    get_section_cache,
    resolve_system_prompt_sections,
    system_prompt_section,
)

# ── prompt_assembler ──────────────────────────────────────────────
from packages.prompt_assembler.assembler import (
    SYSTEM_PROMPT_DYNAMIC_BOUNDARY,
    PromptAssembler,
    PromptConfig,
    assemble_system_prompt,
)

# ── policy_limits ─────────────────────────────────────────────────
from packages.tool_gateway.policy_limits import (
    ESSENTIAL_TRAFFIC_DENY_ON_MISS,
    PolicyLimitsService,
    PolicyRestriction,
    PolicyVerdict,
)


# =====================================================================
# TOKEN ESTIMATION
# =====================================================================


class TestRoughTokenEstimate:
    def test_empty_string(self):
        assert rough_token_estimate("") == 0

    def test_short_string(self):
        assert rough_token_estimate("hi") == max(1, round(2 / DEFAULT_BYTES_PER_TOKEN))

    def test_known_length(self):
        text = "a" * 100
        assert rough_token_estimate(text) == round(100 / DEFAULT_BYTES_PER_TOKEN)

    def test_custom_bytes_per_token(self):
        text = "a" * 100
        assert rough_token_estimate(text, 2) == 50

    def test_minimum_is_one(self):
        assert rough_token_estimate("x") >= 1


class TestBytesPerTokenForFileType:
    def test_json_files(self):
        for ext in ("json", "jsonl", "jsonc"):
            assert bytes_per_token_for_file_type(ext) == 2

    def test_default_file_type(self):
        for ext in ("py", "ts", "txt", "md", ""):
            assert bytes_per_token_for_file_type(ext) == DEFAULT_BYTES_PER_TOKEN


class TestRoughTokenEstimateForFileType:
    def test_json_uses_smaller_ratio(self):
        content = "a" * 100
        json_est = rough_token_estimate_for_file_type(content, "json")
        py_est = rough_token_estimate_for_file_type(content, "py")
        assert json_est > py_est


class TestRoughTokenEstimateForBlock:
    def test_string_block(self):
        assert rough_token_estimate_for_block("hello world") == rough_token_estimate("hello world")

    def test_text_block(self):
        block = {"type": "text", "text": "hello world"}
        assert rough_token_estimate_for_block(block) == rough_token_estimate("hello world")

    def test_image_block(self):
        assert rough_token_estimate_for_block({"type": "image"}) == IMAGE_MAX_TOKEN_SIZE

    def test_document_block(self):
        assert rough_token_estimate_for_block({"type": "document"}) == IMAGE_MAX_TOKEN_SIZE

    def test_tool_result_string(self):
        block = {"type": "tool_result", "content": "result text"}
        assert rough_token_estimate_for_block(block) == rough_token_estimate("result text")

    def test_tool_result_none(self):
        assert rough_token_estimate_for_block({"type": "tool_result", "content": None}) == 0

    def test_tool_result_list(self):
        block = {
            "type": "tool_result",
            "content": [
                {"type": "text", "text": "a" * 40},
                {"type": "text", "text": "b" * 40},
            ],
        }
        expected = rough_token_estimate("a" * 40) + rough_token_estimate("b" * 40)
        assert rough_token_estimate_for_block(block) == expected

    def test_tool_use_block(self):
        block = {"type": "tool_use", "name": "read_file", "input": {"path": "/tmp/x"}}
        serialized = "read_file" + json.dumps({"path": "/tmp/x"}, separators=(",", ":"))
        assert rough_token_estimate_for_block(block) == rough_token_estimate(serialized)

    def test_thinking_block(self):
        block = {"type": "thinking", "thinking": "let me reason..."}
        assert rough_token_estimate_for_block(block) == rough_token_estimate("let me reason...")

    def test_redacted_thinking_block(self):
        block = {"type": "redacted_thinking", "data": "abc123"}
        assert rough_token_estimate_for_block(block) == rough_token_estimate("abc123")

    def test_unknown_block_type(self):
        block = {"type": "custom", "value": 42}
        result = rough_token_estimate_for_block(block)
        assert result > 0


class TestRoughTokenEstimateForContent:
    def test_none_content(self):
        assert rough_token_estimate_for_content(None) == 0

    def test_string_content(self):
        assert rough_token_estimate_for_content("hello") == rough_token_estimate("hello")

    def test_block_list(self):
        blocks = [{"type": "text", "text": "a" * 40}, {"type": "text", "text": "b" * 40}]
        expected = rough_token_estimate("a" * 40) + rough_token_estimate("b" * 40)
        assert rough_token_estimate_for_content(blocks) == expected


class TestRoughTokenEstimateForMessages:
    def test_assistant_message(self):
        msgs = [{"type": "assistant", "message": {"content": "hello world"}}]
        assert rough_token_estimate_for_messages(msgs) == rough_token_estimate("hello world")

    def test_user_message(self):
        msgs = [{"type": "user", "message": {"content": "help me"}}]
        assert rough_token_estimate_for_messages(msgs) == rough_token_estimate("help me")

    def test_attachment_message(self):
        msgs = [{"type": "attachment", "attachment": {"content": "file data"}}]
        assert rough_token_estimate_for_messages(msgs) == rough_token_estimate("file data")

    def test_mixed_messages(self):
        msgs = [
            {"type": "assistant", "message": {"content": "a" * 40}},
            {"type": "user", "message": {"content": "b" * 40}},
            {"type": "attachment", "attachment": {"content": "c" * 40}},
        ]
        expected = sum(rough_token_estimate(c * 40) for c in "abc")
        assert rough_token_estimate_for_messages(msgs) == expected

    def test_empty_messages(self):
        assert rough_token_estimate_for_messages([]) == 0


# =====================================================================
# THINKING CONFIG
# =====================================================================


class TestThinkingConfig:
    def test_dataclass_creation(self):
        cfg = ThinkingConfig(type="adaptive")
        assert cfg.type == "adaptive"
        assert cfg.budget_tokens == 0

    def test_enabled_with_budget(self):
        cfg = ThinkingConfig(type="enabled", budget_tokens=8192)
        assert cfg.type == "enabled"
        assert cfg.budget_tokens == 8192

    def test_frozen(self):
        cfg = ThinkingConfig(type="disabled")
        with pytest.raises(AttributeError):
            cfg.type = "enabled"  # type: ignore[misc]


class TestUltrathinkKeyword:
    def test_basic_match(self):
        assert has_ultrathink_keyword("please ultrathink about this")

    def test_case_insensitive(self):
        assert has_ultrathink_keyword("ULTRATHINK now")
        assert has_ultrathink_keyword("UltraThink")

    def test_no_match(self):
        assert not has_ultrathink_keyword("think harder")
        assert not has_ultrathink_keyword("megathink")

    def test_word_boundary(self):
        assert not has_ultrathink_keyword("myultrathinkmode")

    def test_empty_string(self):
        assert not has_ultrathink_keyword("")


class TestFindThinkingTriggerPositions:
    def test_single_match(self):
        positions = find_thinking_trigger_positions("please ultrathink")
        assert len(positions) == 1
        assert positions[0].word.lower() == "ultrathink"
        assert positions[0].start == 7
        assert positions[0].end == 17

    def test_multiple_matches(self):
        positions = find_thinking_trigger_positions("ultrathink then ultrathink again")
        assert len(positions) == 2

    def test_no_matches(self):
        assert find_thinking_trigger_positions("nothing here") == []


class TestModelSupportsThinking:
    def test_known_models(self):
        assert model_supports_thinking("gemini-3.1-pro")
        assert model_supports_thinking("gemini-3.1-flash")
        assert model_supports_thinking("gemini-2.5-pro")
        assert model_supports_thinking("gemini-3.1-flash-lite-preview-thinking")

    def test_provider_prefix_stripped(self):
        assert model_supports_thinking("models/gemini-3.1-pro")
        assert model_supports_thinking("publishers/google/models/gemini-3.1-pro")

    def test_versioned_variant(self):
        assert model_supports_thinking("gemini-3.1-pro-002")

    def test_unknown_model(self):
        assert not model_supports_thinking("gpt-4o")
        assert not model_supports_thinking("claude-opus-4")


class TestModelSupportsAdaptiveThinking:
    def test_pro_models(self):
        assert model_supports_adaptive_thinking("gemini-3.1-pro")
        assert model_supports_adaptive_thinking("gemini-3-pro")
        assert model_supports_adaptive_thinking("gemini-2.5-pro")

    def test_flash_not_adaptive(self):
        assert not model_supports_adaptive_thinking("gemini-3.1-flash")


class TestIsUltrathinkEnabled:
    def test_default_enabled(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            assert is_ultrathink_enabled() is True

    def test_override_disabled(self):
        with mock.patch.dict(os.environ, {"AGNT_FC_OVERRIDES": "ultrathink=false"}):
            assert is_ultrathink_enabled() is False

    def test_override_enabled(self):
        with mock.patch.dict(os.environ, {"AGNT_FC_OVERRIDES": "ultrathink=true"}):
            assert is_ultrathink_enabled() is True


class TestShouldEnableThinkingByDefault:
    def test_default_enabled(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            assert should_enable_thinking_by_default() is True

    def test_max_tokens_positive(self):
        with mock.patch.dict(os.environ, {"MAX_THINKING_TOKENS": "1024"}):
            assert should_enable_thinking_by_default() is True

    def test_max_tokens_zero(self):
        with mock.patch.dict(os.environ, {"MAX_THINKING_TOKENS": "0"}):
            assert should_enable_thinking_by_default() is False

    def test_override_disabled(self):
        with mock.patch.dict(os.environ, {"AGNT_FC_OVERRIDES": "thinking_enabled=false"}, clear=True):
            assert should_enable_thinking_by_default() is False


# =====================================================================
# PROMPT SECTIONS
# =====================================================================


class TestSystemPromptSection:
    def test_memoized_section(self):
        section = system_prompt_section("test", lambda: "content")
        assert section.name == "test"
        assert section.cache_break is False

    def test_volatile_section(self):
        section = dangerous_uncached_section("vol", lambda: "dynamic", "reason")
        assert section.name == "vol"
        assert section.cache_break is True


class TestResolveSections:
    def setup_method(self):
        clear_system_prompt_sections()

    def test_resolve_sync_compute(self):
        sections = [system_prompt_section("a", lambda: "hello")]
        result = asyncio.run(resolve_system_prompt_sections(sections))
        assert result == ["hello"]

    def test_resolve_async_compute(self):
        async def async_compute():
            return "async_result"

        sections = [system_prompt_section("b", async_compute)]
        result = asyncio.run(resolve_system_prompt_sections(sections))
        assert result == ["async_result"]

    def test_caching_memoized(self):
        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return f"v{call_count}"

        sections = [system_prompt_section("c", compute)]
        r1 = asyncio.run(resolve_system_prompt_sections(sections))
        r2 = asyncio.run(resolve_system_prompt_sections(sections))
        assert r1 == ["v1"]
        assert r2 == ["v1"]
        assert call_count == 1

    def test_volatile_recomputes(self):
        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return f"v{call_count}"

        sections = [dangerous_uncached_section("d", compute, "test")]
        r1 = asyncio.run(resolve_system_prompt_sections(sections))
        r2 = asyncio.run(resolve_system_prompt_sections(sections))
        assert r1 == ["v1"]
        assert r2 == ["v2"]
        assert call_count == 2

    def test_none_result(self):
        sections = [system_prompt_section("e", lambda: None)]
        result = asyncio.run(resolve_system_prompt_sections(sections))
        assert result == [None]

    def test_clear_resets_cache(self):
        call_count = 0

        def compute():
            nonlocal call_count
            call_count += 1
            return f"v{call_count}"

        sections = [system_prompt_section("f", compute)]
        asyncio.run(resolve_system_prompt_sections(sections))
        clear_system_prompt_sections()
        r2 = asyncio.run(resolve_system_prompt_sections(sections))
        assert r2 == ["v2"]

    def test_get_section_cache(self):
        sections = [system_prompt_section("g", lambda: "cached_val")]
        asyncio.run(resolve_system_prompt_sections(sections))
        cache = get_section_cache()
        assert cache["g"] == "cached_val"
        assert isinstance(cache, dict)


# =====================================================================
# PROMPT ASSEMBLER
# =====================================================================


class TestPromptConfig:
    def test_defaults(self):
        cfg = PromptConfig()
        assert cfg.model_id == "gemini-3.1-flash-lite-preview-thinking"
        assert cfg.is_git_repo is True
        assert cfg.use_global_cache_scope is True
        assert cfg.language_preference is None
        assert cfg.mcp_instructions is None


class TestPromptAssembler:
    def setup_method(self):
        clear_system_prompt_sections()

    def test_boundary_marker_present(self):
        cfg = PromptConfig(use_global_cache_scope=True)
        result = asyncio.run(assemble_system_prompt(cfg))
        assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY in result

    def test_boundary_marker_absent(self):
        cfg = PromptConfig(use_global_cache_scope=False)
        result = asyncio.run(assemble_system_prompt(cfg))
        assert SYSTEM_PROMPT_DYNAMIC_BOUNDARY not in result

    def test_static_sections_present(self):
        cfg = PromptConfig()
        result = asyncio.run(assemble_system_prompt(cfg))
        joined = "\n".join(result)
        assert "interactive agent" in joined
        assert "# System" in joined
        assert "# Doing tasks" in joined
        assert "# Output Efficiency" in joined

    def test_env_info_included(self):
        cfg = PromptConfig(cwd="/test/dir")
        result = asyncio.run(assemble_system_prompt(cfg))
        joined = "\n".join(result)
        assert "/test/dir" in joined

    def test_language_section(self):
        cfg = PromptConfig(language_preference="Spanish")
        result = asyncio.run(assemble_system_prompt(cfg))
        joined = "\n".join(result)
        assert "Spanish" in joined

    def test_no_language_when_none(self):
        cfg = PromptConfig(language_preference=None)
        result = asyncio.run(assemble_system_prompt(cfg))
        assert all("# Language" not in s for s in result)

    def test_mcp_instructions_volatile(self):
        cfg = PromptConfig(mcp_instructions="Use firebase MCP")
        assembler = PromptAssembler(cfg)
        defs = assembler._build_dynamic_section_defs()
        mcp_section = next(d for d in defs if d.name == "mcp_instructions")
        assert mcp_section.cache_break is True

    def test_cyber_risk_instruction(self):
        cfg = PromptConfig()
        result = asyncio.run(assemble_system_prompt(cfg))
        joined = "\n".join(result)
        assert "authorized security testing" in joined

    def test_sync_wrapper(self):
        cfg = PromptConfig()
        assembler = PromptAssembler(cfg)
        result = assembler.assemble_sync()
        assert isinstance(result, list)
        assert len(result) > 0


# =====================================================================
# POLICY LIMITS
# =====================================================================


class TestPolicyLimitsService:
    def setup_method(self):
        PolicyLimitsService.reset_for_testing()

    def teardown_method(self):
        PolicyLimitsService.reset_for_testing()

    def test_singleton(self):
        a = PolicyLimitsService.get_instance()
        b = PolicyLimitsService.get_instance()
        assert a is b

    def test_reset_clears_singleton(self):
        a = PolicyLimitsService.get_instance()
        PolicyLimitsService.reset_for_testing()
        b = PolicyLimitsService.get_instance()
        assert a is not b

    def test_fail_open_no_cache(self):
        svc = PolicyLimitsService.get_instance()
        assert svc.is_policy_allowed("anything") is True

    def test_fail_open_verdict(self):
        svc = PolicyLimitsService.get_instance()
        assert svc.get_policy_verdict("anything") == PolicyVerdict.UNKNOWN

    def test_essential_traffic_deny_on_miss(self):
        svc = PolicyLimitsService.get_instance()
        svc._essential_traffic_only = True
        for policy in ESSENTIAL_TRAFFIC_DENY_ON_MISS:
            assert svc.is_policy_allowed(policy) is False
            assert svc.get_policy_verdict(policy) == PolicyVerdict.DENIED

    def test_session_cache_allowed(self):
        svc = PolicyLimitsService.get_instance()
        svc._session_cache = {
            "allow_remote": PolicyRestriction(allowed=True),
        }
        assert svc.is_policy_allowed("allow_remote") is True
        assert svc.get_policy_verdict("allow_remote") == PolicyVerdict.ALLOWED

    def test_session_cache_denied(self):
        svc = PolicyLimitsService.get_instance()
        svc._session_cache = {
            "allow_remote": PolicyRestriction(allowed=False, reason="org policy"),
        }
        assert svc.is_policy_allowed("allow_remote") is False
        assert svc.get_policy_verdict("allow_remote") == PolicyVerdict.DENIED

    def test_unknown_policy_in_cache(self):
        svc = PolicyLimitsService.get_instance()
        svc._session_cache = {"other_policy": PolicyRestriction(allowed=True)}
        assert svc.is_policy_allowed("nonexistent") is True
        assert svc.get_policy_verdict("nonexistent") == PolicyVerdict.UNKNOWN

    def test_file_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc = PolicyLimitsService.get_instance()
            svc.configure(config_home=Path(tmp))
            restrictions = {
                "test_policy": PolicyRestriction(allowed=False, reason="blocked", metadata={"org": "acme"}),
            }
            svc._save_cached_restrictions(restrictions)
            assert svc.cache_path.exists()

            loaded = svc._load_cached_restrictions()
            assert loaded is not None
            assert "test_policy" in loaded
            assert loaded["test_policy"].allowed is False
            assert loaded["test_policy"].reason == "blocked"

    def test_load_from_org_policies(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            policy_file = tmp_path / "org_policies.json"
            policy_file.write_text(
                json.dumps(
                    {
                        "restrictions": {
                            "allow_sharing": {"allowed": False, "reason": "compliance"},
                        }
                    }
                )
            )

            svc = PolicyLimitsService.get_instance()
            svc.configure(config_home=tmp_path)
            svc.load()

            assert svc.is_policy_allowed("allow_sharing") is False
            svc.stop_polling()

    def test_load_empty_policies(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc = PolicyLimitsService.get_instance()
            svc.configure(config_home=Path(tmp))
            svc.load()
            assert svc.is_policy_allowed("anything") is True
            svc.stop_polling()

    def test_checksum_stability(self):
        r = {"a": PolicyRestriction(allowed=True, reason="ok")}
        c1 = PolicyLimitsService._compute_checksum(r)
        c2 = PolicyLimitsService._compute_checksum(r)
        assert c1 == c2
        assert c1 is not None
        assert c1.startswith("sha256:")

    def test_checksum_none(self):
        assert PolicyLimitsService._compute_checksum(None) is None

    def test_retry_delay_exponential(self):
        d1 = PolicyLimitsService._get_retry_delay(1)
        d3 = PolicyLimitsService._get_retry_delay(3)
        assert d3 > d1

    def test_cache_path_default(self):
        svc = PolicyLimitsService.get_instance()
        assert "tool_gateway" in str(svc.cache_path)
        assert svc.cache_path.name == "policy-limits.json"

    def test_clear_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc = PolicyLimitsService.get_instance()
            svc.configure(config_home=Path(tmp))
            svc._session_cache = {"x": PolicyRestriction(allowed=True)}
            svc.clear_cache()
            assert svc._session_cache is None
