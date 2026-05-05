# apps/counselconduit/api/middleware/prompt_guard.py
"""Prompt Injection Guardrails — OWASP LLM01.

Structural isolation of system prompts from user input.
Detects known injection patterns and blocks before LLM processing.

Defense-in-depth layers:
1. Input pattern matching (known injection templates)
2. System prompt isolation (never concatenate user input into system context)
3. Output filtering (strip any leaked system prompt fragments)
"""

from __future__ import annotations

import logging
import re

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("counselconduit.prompt_guard")

# ── Known Injection Patterns ──────────────────────────────────────────────

# These patterns indicate prompt injection attempts
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    # Direct instruction override
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?above\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?previous", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?previous", re.IGNORECASE),
    # System prompt extraction
    re.compile(r"(print|show|reveal|display|output)\s+(your\s+)?(system\s+)?prompt", re.IGNORECASE),
    re.compile(r"what\s+(are|is)\s+your\s+(system\s+)?(instructions|prompt|rules)", re.IGNORECASE),
    re.compile(r"repeat\s+(the\s+)?text\s+above", re.IGNORECASE),
    # Role hijacking
    re.compile(r"you\s+are\s+now\s+(a|an|the)\s+", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+)?(you\s+)?(are|were)\s+(a|an)", re.IGNORECASE),
    re.compile(r"pretend\s+(you\s+)?(are|to\s+be)", re.IGNORECASE),
    re.compile(r"new\s+instructions?:", re.IGNORECASE),
    re.compile(r"override\s+(system|safety|security)", re.IGNORECASE),
    # Data exfiltration
    re.compile(r"(send|post|fetch|curl|wget)\s+.*(http|ftp|ssh)", re.IGNORECASE),
    re.compile(r"execute\s+(shell|bash|cmd|command|code)", re.IGNORECASE),
    # Delimiter attacks
    re.compile(r"<\|system\|>", re.IGNORECASE),
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"```system", re.IGNORECASE),
]

# System prompt fragments that must never appear in outputs
_SYSTEM_PROMPT_MARKERS: list[str] = [
    "kovel doctrine",
    "privileged communication",
    "counselconduit internal",
    "system_prompt",
    "NEVER_REVEAL",
]


def detect_injection(text: str) -> str | None:
    """Check text for known injection patterns. Returns matched pattern or None."""
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group()
    return None


def filter_output(text: str) -> str:
    """Strip any leaked system prompt fragments from LLM output."""
    filtered = text
    for marker in _SYSTEM_PROMPT_MARKERS:
        if marker.lower() in filtered.lower():
            logger.warning("System prompt leak detected and stripped: %s", marker)
            filtered = re.sub(
                re.escape(marker),
                "[REDACTED]",
                filtered,
                flags=re.IGNORECASE,
            )
    return filtered


class PromptGuardMiddleware(BaseHTTPMiddleware):
    """OWASP LLM01: Prompt injection detection and blocking.

    Scans request bodies for known injection patterns on LLM-adjacent routes.
    Does NOT replace proper system prompt isolation — that must be done at
    the LLM call site (gemini_rag.py).
    """

    # Routes that process user text for LLM consumption
    _LLM_ROUTES = {"/query", "/chat", "/oracle", "/stream"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Only scan LLM-adjacent routes
        if not any(route in path for route in self._LLM_ROUTES):
            return await call_next(request)

        # Only scan POST/PUT bodies
        if request.method in ("POST", "PUT"):
            try:
                body = await request.body()
                body_text = body.decode("utf-8", errors="ignore")

                injection = detect_injection(body_text)
                if injection:
                    logger.warning(
                        "Prompt injection BLOCKED: pattern='%s' path=%s ip=%s",
                        injection[:50],
                        path,
                        request.headers.get("X-Forwarded-For", "unknown"),
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "code": "PROMPT_INJECTION_DETECTED",
                            "message": "Your request contains content that cannot be processed. Please rephrase.",
                        },
                    )
            except HTTPException:
                raise
            except Exception:
                # Don't block on parse errors — let the route handler deal with it
                pass

        return await call_next(request)
