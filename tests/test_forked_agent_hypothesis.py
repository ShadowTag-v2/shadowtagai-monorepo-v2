# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Deep Hypothesis property tests for forked_agent.py.

Validates invariants across all ForkedAgent data structures:
  1. TokenUsage accumulation associativity + identity
  2. cache_hit_rate in [0.0, 1.0]
  3. total_input_tokens = sum of components
  4. CacheSafeParams is frozen
  5. SubagentContext unique IDs
  6. create_subagent_context deep-copy isolation
  7. extract_result_text edge cases
  8. save/get_last_cache_safe_params roundtrip
"""

from __future__ import annotations

import os
import sys

import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

sys.path.insert(0, "packages")

from agnt_services.forked_agent import (
    CacheSafeParams,
    SubagentContext,
    SubagentContextOverrides,
    TokenUsage,
    accumulate_usage,
    create_subagent_context,
    extract_result_text,
    get_last_cache_safe_params,
    save_cache_safe_params,
)

_FUZZ = int(os.environ.get("HYPOTHESIS_FUZZ_MULTIPLIER", "1"))
_HC = [HealthCheck.too_slow]

non_neg = st.integers(min_value=0, max_value=2**32)
usage_st = st.builds(
    TokenUsage,
    input_tokens=non_neg,
    output_tokens=non_neg,
    cache_read_input_tokens=non_neg,
    cache_creation_input_tokens=non_neg,
    service_tier=st.text(max_size=20),
)
safe_text = st.text(min_size=0, max_size=200)
msg_st = st.fixed_dictionaries({"role": st.sampled_from(["user", "assistant", "system"]), "content": safe_text})


class TestTokenUsageAccumulation:
    @given(a=usage_st, b=usage_st)
    @settings(max_examples=300 * _FUZZ, suppress_health_check=_HC)
    def test_adds_fields(self, a, b):
        r = accumulate_usage(a, b)
        assert r.input_tokens == a.input_tokens + b.input_tokens
        assert r.output_tokens == a.output_tokens + b.output_tokens
        assert r.cache_read_input_tokens == a.cache_read_input_tokens + b.cache_read_input_tokens

    @given(a=usage_st)
    @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
    def test_identity(self, a):
        r = accumulate_usage(a, TokenUsage())
        assert r.input_tokens == a.input_tokens

    @given(a=usage_st, b=usage_st, c=usage_st)
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_associativity(self, a, b, c):
        ab_c = accumulate_usage(accumulate_usage(a, b), c)
        a_bc = accumulate_usage(a, accumulate_usage(b, c))
        assert ab_c.input_tokens == a_bc.input_tokens
        assert ab_c.output_tokens == a_bc.output_tokens


class TestTokenUsageDerived:
    @given(usage=usage_st)
    @settings(max_examples=300 * _FUZZ, suppress_health_check=_HC)
    def test_total_sum(self, usage):
        assert usage.total_input_tokens == (
            usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation_input_tokens
        )

    @given(usage=usage_st)
    @settings(max_examples=300 * _FUZZ, suppress_health_check=_HC)
    def test_rate_bounded(self, usage):
        assert 0.0 <= usage.cache_hit_rate <= 1.0

    def test_rate_zero_total(self):
        assert TokenUsage().cache_hit_rate == 0.0


class TestCacheSafeParamsFrozen:
    def test_cannot_set_prompt(self):
        p = CacheSafeParams(system_prompt="t")
        with pytest.raises(AttributeError):
            p.system_prompt = "x"  # type: ignore[misc]

    @given(prompt=safe_text)
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_roundtrip(self, prompt):
        assert CacheSafeParams(system_prompt=prompt).system_prompt == prompt


class TestSubagentContextIDs:
    @given(n=st.integers(min_value=2, max_value=50))
    @settings(max_examples=50 * _FUZZ, suppress_health_check=_HC)
    def test_unique_agent_ids(self, n):
        ids = [SubagentContext().agent_id for _ in range(n)]
        assert len(set(ids)) == n

    @given(n=st.integers(min_value=2, max_value=50))
    @settings(max_examples=50 * _FUZZ, suppress_health_check=_HC)
    def test_unique_chain_ids(self, n):
        ids = [SubagentContext().query_chain_id for _ in range(n)]
        assert len(set(ids)) == n


class TestSubagentIsolation:
    @given(messages=st.lists(msg_st, max_size=10))
    @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
    def test_deep_copy(self, messages):
        parent = [m.copy() for m in messages]
        ctx = create_subagent_context(parent_messages=parent)
        ctx.messages.append({"role": "injected", "content": "BAD"})
        assert len(parent) == len(messages)

    @given(depth=st.integers(min_value=-1, max_value=100))
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_depth_increment(self, depth):
        ctx = create_subagent_context(parent_depth=depth)
        assert ctx.query_depth == depth + 1

    @given(aid=st.text(min_size=1, max_size=36))
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_overrides(self, aid):
        ctx = create_subagent_context(overrides=SubagentContextOverrides(agent_id=aid))
        assert ctx.agent_id == aid


class TestExtractResultText:
    @given(default=safe_text)
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_empty_default(self, default):
        assert extract_result_text([], default_text=default) == default

    @given(content=st.text(min_size=1, max_size=200))
    @settings(max_examples=200 * _FUZZ, suppress_health_check=_HC)
    def test_last_assistant(self, content):
        assume(content.strip())
        msgs = [{"role": "user", "content": "q"}, {"role": "assistant", "content": content}]
        assert extract_result_text(msgs) == content


class TestCacheSafeParamsStore:
    @given(prompt=safe_text)
    @settings(max_examples=100 * _FUZZ, suppress_health_check=_HC)
    def test_roundtrip(self, prompt):
        p = CacheSafeParams(system_prompt=prompt)
        save_cache_safe_params(p)
        assert get_last_cache_safe_params() is p

    def test_none_roundtrip(self):
        save_cache_safe_params(None)
        assert get_last_cache_safe_params() is None
