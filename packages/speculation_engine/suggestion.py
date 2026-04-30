# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Prompt Suggestion — Stage 1 of the Speculation Engine.

Architecture (ported from Claude Code v2.1.91 promptSuggestion.ts):
  5-layer enablement gates -> cache-safe forked agent -> 12-rule client filter -> RL telemetry.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from speculation_engine.telemetry import log_suggestion_event

MIN_ASSISTANT_TURNS = 2
CACHE_COLD_THRESHOLD = 10_000
MAX_SUGGESTION_WORDS = 12
MAX_SUGGESTION_CHARS = 100

SINGLE_WORD_ALLOWLIST = frozenset(
    {
        "yes",
        "yeah",
        "yep",
        "yup",
        "sure",
        "ok",
        "okay",
        "no",
        "nope",
        "push",
        "commit",
        "deploy",
        "stop",
        "continue",
        "proceed",
        "test",
        "build",
        "run",
        "lint",
        "fix",
        "undo",
        "retry",
    }
)


class SuppressReason(StrEnum):
    DISABLED = "disabled"
    NON_INTERACTIVE = "non_interactive"
    SWARM_TEAMMATE = "swarm_teammate"
    FEATURE_FLAG_OFF = "feature_flag_off"
    ENV_OVERRIDE = "env_override"
    TOO_FEW_TURNS = "too_few_turns"
    LAST_RESPONSE_ERROR = "last_response_error"
    CACHE_COLD = "cache_cold"
    PENDING_PERMISSION = "pending_permission"
    ELICITATION_ACTIVE = "elicitation_active"
    PLAN_MODE = "plan_mode"
    RATE_LIMITED = "rate_limited"


class FilterReason(StrEnum):
    DONE = "done"
    META_TEXT = "meta_text"
    META_WRAPPED = "meta_wrapped"
    ERROR_MESSAGE = "error_message"
    PREFIXED_LABEL = "prefixed_label"
    TOO_FEW_WORDS = "too_few_words"
    TOO_MANY_WORDS = "too_many_words"
    TOO_LONG = "too_long"
    MULTIPLE_SENTENCES = "multiple_sentences"
    HAS_FORMATTING = "has_formatting"
    EVALUATIVE = "evaluative"
    CLAUDE_VOICE = "claude_voice"


@dataclass
class SuggestionConfig:
    enabled: bool = True
    feature_flag_enabled: bool = True
    is_interactive: bool = True
    is_swarm_leader: bool = True
    env_override: bool | None = None
    min_assistant_turns: int = MIN_ASSISTANT_TURNS
    cache_cold_threshold: int = CACHE_COLD_THRESHOLD


@dataclass
class SuggestionResult:
    suggestion: str | None = None
    suppressed: bool = False
    suppress_reason: SuppressReason | None = None
    filtered: bool = False
    filter_reason: FilterReason | None = None
    generation_request_id: str | None = None
    generation_time_ms: float = 0.0


@dataclass
class SuggestionOutcome:
    suggestion: str
    was_accepted: bool = False
    similarity: float = 0.0
    time_to_accept_ms: float | None = None
    time_to_ignore_ms: float | None = None
    generation_request_id: str | None = None
    displayed_at: float = field(default_factory=time.time)


@dataclass
class SessionState:
    suggestion_enabled: bool = True
    pending_permission: bool = False
    elicitation_active: bool = False
    plan_mode: bool = False
    rate_limited: bool = False
    assistant_turn_count: int = 0
    last_response_error: bool = False
    last_request_tokens: int = 0


def check_enablement_gates(config: SuggestionConfig) -> SuppressReason | None:
    if config.env_override is not None and not config.env_override:
        return SuppressReason.ENV_OVERRIDE
    if not config.feature_flag_enabled:
        return SuppressReason.FEATURE_FLAG_OFF
    if not config.is_interactive:
        return SuppressReason.NON_INTERACTIVE
    if not config.is_swarm_leader:
        return SuppressReason.SWARM_TEAMMATE
    if not config.enabled:
        return SuppressReason.DISABLED
    return None


def get_suggestion_suppress_reason(
    state: SessionState,
    config: SuggestionConfig,
) -> SuppressReason | None:
    if not state.suggestion_enabled:
        return SuppressReason.DISABLED
    if state.pending_permission:
        return SuppressReason.PENDING_PERMISSION
    if state.elicitation_active:
        return SuppressReason.ELICITATION_ACTIVE
    if state.plan_mode:
        return SuppressReason.PLAN_MODE
    if state.rate_limited:
        return SuppressReason.RATE_LIMITED
    if state.assistant_turn_count < config.min_assistant_turns:
        return SuppressReason.TOO_FEW_TURNS
    if state.last_response_error:
        return SuppressReason.LAST_RESPONSE_ERROR
    if state.last_request_tokens > config.cache_cold_threshold:
        return SuppressReason.CACHE_COLD
    return None


SUGGESTION_PROMPT = (
    "[SUGGESTION MODE: Suggest what the user might naturally type next.]\n"
    'THE TEST: Would they think "I was just about to type that"?\n'
    "Rules: 2-12 words max. Match user style. No Claude voice. Silence is valid."
)

_META_PATTERNS = re.compile(r"nothing found|no suggestion|stay silent|^silence$", re.I)
_META_WRAPPED = re.compile(r"^\s*[\(\[].+[\)\]]\s*$")
_PREFIXED_LABEL = re.compile(r"^\w+:\s+")
_MULTIPLE_SENTENCES = re.compile(r"[.!?]\s+[A-Z]")
_FORMATTING = re.compile(r"[\n*]")
_EVALUATIVE = re.compile(r"(?:thanks|thank you|looks good|great job|well done)", re.I)
_CLAUDE_VOICE = re.compile(r"^(?:let me|i'll|i will|here's|here is|i can)", re.I)
_ERROR_MSG = re.compile(r"(?:api error|rate limit|timeout|500|503)", re.I)


def should_filter_suggestion(text: str) -> FilterReason | None:
    s = text.strip()
    if not s:
        return FilterReason.META_TEXT
    if s.lower() == "done":
        return FilterReason.DONE
    if _META_PATTERNS.search(s):
        return FilterReason.META_TEXT
    if _META_WRAPPED.match(s):
        return FilterReason.META_WRAPPED
    if _ERROR_MSG.search(s):
        return FilterReason.ERROR_MESSAGE
    if _PREFIXED_LABEL.match(s):
        return FilterReason.PREFIXED_LABEL
    words = s.split()
    if len(words) == 1 and s.lower() not in SINGLE_WORD_ALLOWLIST and not s.startswith("/"):
        return FilterReason.TOO_FEW_WORDS
    if len(words) > MAX_SUGGESTION_WORDS:
        return FilterReason.TOO_MANY_WORDS
    if len(s) >= MAX_SUGGESTION_CHARS:
        return FilterReason.TOO_LONG
    if _MULTIPLE_SENTENCES.search(s):
        return FilterReason.MULTIPLE_SENTENCES
    if _FORMATTING.search(s):
        return FilterReason.HAS_FORMATTING
    if _EVALUATIVE.search(s):
        return FilterReason.EVALUATIVE
    if _CLAUDE_VOICE.match(s):
        return FilterReason.CLAUDE_VOICE
    return None


def try_generate_suggestion(
    messages: list[dict[str, Any]],
    state: SessionState,
    config: SuggestionConfig,
    *,
    generate_fn: Any | None = None,
    abort_signal: bool = False,
) -> SuggestionResult:
    start_time = time.monotonic()
    if abort_signal:
        return SuggestionResult(suppressed=True, suppress_reason=SuppressReason.DISABLED)
    gate = check_enablement_gates(config)
    if gate is not None:
        log_suggestion_event(event="suppressed", reason=gate.value, source="gate")
        return SuggestionResult(suppressed=True, suppress_reason=gate)
    sr = get_suggestion_suppress_reason(state, config)
    if sr is not None:
        log_suggestion_event(event="suppressed", reason=sr.value, source="state")
        return SuggestionResult(suppressed=True, suppress_reason=sr)
    if generate_fn is None:
        return SuggestionResult(suppressed=True, suppress_reason=SuppressReason.DISABLED)
    try:
        text, gen_id = generate_fn(messages, SUGGESTION_PROMPT)
    except Exception:
        return SuggestionResult(generation_time_ms=(time.monotonic() - start_time) * 1000)
    gen_time = (time.monotonic() - start_time) * 1000
    if not text:
        return SuggestionResult(generation_time_ms=gen_time)
    fr = should_filter_suggestion(text)
    if fr is not None:
        log_suggestion_event(event="filtered", reason=fr.value, suggestion=text)
        return SuggestionResult(filtered=True, filter_reason=fr, generation_request_id=gen_id, generation_time_ms=gen_time)
    return SuggestionResult(suggestion=text, generation_request_id=gen_id, generation_time_ms=gen_time)


def log_suggestion_outcome(outcome: SuggestionOutcome, user_input: str) -> None:
    now = time.time()
    outcome.was_accepted = user_input.strip() == outcome.suggestion.strip()
    if outcome.was_accepted:
        outcome.time_to_accept_ms = (now - outcome.displayed_at) * 1000
    else:
        outcome.time_to_ignore_ms = (now - outcome.displayed_at) * 1000
    if outcome.suggestion:
        outcome.similarity = min(len(user_input) / max(len(outcome.suggestion), 1), 1.0)
    log_suggestion_event(
        event="outcome",
        accepted=outcome.was_accepted,
        similarity=outcome.similarity,
        time_to_accept_ms=outcome.time_to_accept_ms,
        time_to_ignore_ms=outcome.time_to_ignore_ms,
        generation_request_id=outcome.generation_request_id,
    )
