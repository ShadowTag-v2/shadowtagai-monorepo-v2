"""System Prompt Section Registry — core implementation.

Ported from Claude Code v2.1.91 constants/systemPromptSections.ts.

Design invariants (preserved from source):
- Dependency-free: no circular imports allowed.
- Memoized sections: computed once, cached until clear/compact.
- Volatile sections: recomputed every turn (cache-breaking).
- Cache is a module-level dict, reset on clear_system_prompt_sections().
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional, Union

# Type alias for compute functions — can be sync or async.
ComputeFn = Callable[[], Union[Optional[str], Awaitable[Optional[str]]]]

# Module-level cache (replaces bootstrap/state.js in the TS version).
_section_cache: dict[str, Optional[str]] = {}
_beta_header_latches_cleared: bool = False


@dataclass(frozen=True, slots=True)
class SystemPromptSection:
    """A single registerable system prompt section.

    Attributes:
        name: Unique identifier for the section.
        compute: Callable that produces the section content.
        cache_break: If True, recomputes every turn (volatile).
    """

    name: str
    compute: ComputeFn
    cache_break: bool = field(default=False)


def system_prompt_section(
    name: str,
    compute: ComputeFn,
) -> SystemPromptSection:
    """Create a memoized system prompt section.

    Computed once, cached until clear_system_prompt_sections() is called
    (typically on /clear or /compact commands).
    """
    return SystemPromptSection(name=name, compute=compute, cache_break=False)


def dangerous_uncached_section(
    name: str,
    compute: ComputeFn,
    reason: str,  # noqa: ARG001 — documents WHY cache-breaking is necessary
) -> SystemPromptSection:
    """Create a volatile system prompt section that recomputes every turn.

    This WILL break the prompt cache when the value changes.
    The reason parameter documents why cache-breaking is necessary and is
    preserved for audit purposes (matches the TS _reason pattern).
    """
    return SystemPromptSection(name=name, compute=compute, cache_break=True)


async def _resolve_compute(compute: ComputeFn) -> Optional[str]:
    """Resolve a compute function, handling both sync and async callables."""
    result = compute()
    if asyncio.iscoroutine(result) or asyncio.isfuture(result):
        return await result
    return result  # type: ignore[return-value]


async def resolve_system_prompt_sections(
    sections: list[SystemPromptSection],
) -> list[Optional[str]]:
    """Resolve all system prompt sections, returning prompt strings.

    For memoized sections, returns the cached value if available.
    For volatile sections (cache_break=True), always recomputes.

    Returns:
        List of resolved prompt strings (or None for sections that
        returned None from their compute function).
    """

    async def _resolve_one(section: SystemPromptSection) -> Optional[str]:
        # Return cached value for memoized sections.
        if not section.cache_break and section.name in _section_cache:
            return _section_cache[section.name]

        # Compute fresh value.
        value = await _resolve_compute(section.compute)

        # Cache the result (even for volatile sections — the TS source does this).
        _section_cache[section.name] = value
        return value

    return list(await asyncio.gather(*[_resolve_one(s) for s in sections]))


def clear_system_prompt_sections() -> None:
    """Clear all system prompt section state.

    Called on /clear and /compact. Also resets beta header latches so a
    fresh conversation gets fresh evaluation of feature headers.
    """
    global _beta_header_latches_cleared  # noqa: PLW0603
    _section_cache.clear()
    _beta_header_latches_cleared = True


def get_section_cache() -> dict[str, Optional[str]]:
    """Read-only access to the section cache for diagnostics."""
    return dict(_section_cache)
