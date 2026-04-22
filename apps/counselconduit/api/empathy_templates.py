# apps/counselconduit/api/empathy_templates.py
"""S.E.U. Empathy Template Library — Randomized Empathy Acknowledgers.

Security hardening for Risk #63: Prevents adversarial prompt injection
by randomizing the empathy opener across 24 variants. Also provides
post-generation fingerprinting and output validation.

S.E.U. ordering: Safety → Empathy → Utility
All client-facing LLM responses MUST open with an empathy acknowledger
before delivering utility (legal analysis, research, advice).
"""

from __future__ import annotations

import hashlib
import logging
import random
from dataclasses import dataclass

logger = logging.getLogger("counselconduit.empathy_templates")


# ── Empathy Acknowledgers (24 variants, randomized per call) ──────────────


_EMPATHY_OPENERS: list[str] = [
    "We understand this is a stressful situation, and we're here to help.",
    "I hear you — navigating legal matters can feel overwhelming.",
    "Thank you for sharing this with us. You're taking an important step.",
    "I understand how difficult this situation must be for you.",
    "Your concerns are valid, and we want to make sure you feel supported.",
    "This sounds like a challenging situation, and we're here to guide you through it.",
    "I appreciate you trusting us with this. Let's work through it together.",
    "It takes courage to seek help, and we're glad you reached out.",
    "I can see why this situation is weighing on you. Let's break it down.",
    "We want you to know that you're not alone in this — we're here for you.",
    "Your feelings about this are completely understandable.",
    "I recognize this isn't easy to talk about, and I appreciate your openness.",
    "We're here to listen and help you make sense of what you're going through.",
    "I understand the urgency you're feeling. Let's make sure we address this.",
    "Thank you for being so open about your situation. It helps us help you.",
    "I want you to know we take your concerns seriously.",
    "You've done the right thing by reaching out. Let's explore your options.",
    "I can tell this matters deeply to you, and it matters to us too.",
    "We appreciate you walking us through this. Every detail helps.",
    "I understand how frustrating this must feel. Let's find a path forward.",
    "Your situation is unique, and we'll give it the attention it deserves.",
    "Thank you for your patience in explaining this. We want to get it right.",
    "I know dealing with legal matters can be daunting. We'll take it step by step.",
    "We're committed to making sure you feel heard and understood throughout this process.",
]

# Warm close templates — never use "goodbye" variants
_WARM_CLOSES: list[str] = [
    "Before we wrap up — is there anything else on your mind we should address?",
    "One more thing to consider: you can always come back to explore further.",
    "Take your time processing this. We're here whenever you need us.",
    "Remember, understanding your situation is the first step to resolving it.",
    "We'll have a full summary ready for your attorney to review.",
    "You've made real progress today. Your attorney will have everything they need.",
]

# "How are you feeling?" check-in templates (every 3rd response)
_CHECKIN_TEMPLATES: list[str] = [
    "Before we continue — how are you feeling about everything so far?",
    "I want to check in with you. Are you doing okay as we go through this?",
    "Let's pause for a moment. How are you feeling about what we've covered?",
    "I know this is a lot of information. How are you holding up?",
    "Before we move on, I want to make sure you're comfortable with everything.",
    "Take a breath if you need to. How are you feeling right now?",
]

# "One More Thing" cadence templates — post-utility hooks
_ONE_MORE_THING: list[str] = [
    "One more thing — there's an aspect of this you might not have considered yet.",
    "Before we move on, there's another angle worth exploring.",
    "Something else comes to mind that could be relevant to your situation.",
    "There's one more point that could strengthen your position.",
    "I also want to flag something that comes up often in cases like yours.",
    "One additional thought that might give you helpful context.",
]


# ── Template Selection ────────────────────────────────────────────────────


def get_empathy_opener(*, seed: str | None = None) -> str:
    """Get a randomized empathy opener.

    Args:
        seed: Optional session_id or message_id for deterministic selection.
              If None, uses true random selection.
    """
    if seed:
        idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_EMPATHY_OPENERS)
        return _EMPATHY_OPENERS[idx]
    return random.choice(_EMPATHY_OPENERS)  # noqa: S311


def get_warm_close(*, seed: str | None = None) -> str:
    """Get a randomized warm close template."""
    if seed:
        idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_WARM_CLOSES)
        return _WARM_CLOSES[idx]
    return random.choice(_WARM_CLOSES)  # noqa: S311


def get_checkin(*, seed: str | None = None) -> str:
    """Get a 'How are you feeling?' check-in template."""
    if seed:
        idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_CHECKIN_TEMPLATES)
        return _CHECKIN_TEMPLATES[idx]
    return random.choice(_CHECKIN_TEMPLATES)  # noqa: S311


def get_one_more_thing(*, seed: str | None = None) -> str:
    """Get a 'One More Thing' cadence hook."""
    if seed:
        idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % len(_ONE_MORE_THING)
        return _ONE_MORE_THING[idx]
    return random.choice(_ONE_MORE_THING)  # noqa: S311


def should_checkin(message_index: int) -> bool:
    """Returns True if this is a check-in turn (every 3rd response)."""
    return message_index > 0 and message_index % 3 == 0


# ── Output Fingerprinting (Risk #63 mitigation) ──────────────────────────


@dataclass
class EmpathyFingerprint:
    """Fingerprint for verifying empathy layer integrity."""

    expected_opener: str
    opener_hash: str
    is_intact: bool
    mutation_detected: bool


def fingerprint_output(
    response_text: str,
    expected_opener: str,
) -> EmpathyFingerprint:
    """Verify that the empathy acknowledger was preserved in the output.

    Detects if the empathy layer was stripped or mutated by the model
    or by a prompt injection attack.
    """
    opener_hash = hashlib.sha256(expected_opener.encode()).hexdigest()[:16]

    # Check if opener appears in the first 500 chars of response
    is_intact = expected_opener.lower()[:40] in response_text.lower()[:500]

    # Check for mutation: opener words should appear even if reworded
    opener_words = set(expected_opener.lower().split())
    response_start_words = set(response_text.lower()[:300].split())
    overlap = len(opener_words & response_start_words)
    mutation_detected = not is_intact and overlap < len(opener_words) * 0.3

    if mutation_detected:
        logger.warning(
            "Empathy layer mutation detected: opener_hash=%s overlap=%d/%d",
            opener_hash,
            overlap,
            len(opener_words),
        )

    return EmpathyFingerprint(
        expected_opener=expected_opener,
        opener_hash=opener_hash,
        is_intact=is_intact,
        mutation_detected=mutation_detected,
    )


# ── S.E.U. Prompt Wrapper ────────────────────────────────────────────────


def wrap_seu_prompt(
    *,
    safety_instructions: str,
    utility_prompt: str,
    session_id: str | None = None,
    include_checkin: bool = False,
    include_one_more_thing: bool = False,
) -> str:
    """Wrap a utility prompt in S.E.U. ordering.

    Safety → Empathy → Utility

    Args:
        safety_instructions: Safety directives (Judge 6, Kovel, privilege).
        utility_prompt: The actual functional prompt (legal analysis, etc.).
        session_id: For deterministic template selection.
        include_checkin: Add a check-in template.
        include_one_more_thing: Add a "One More Thing" cadence hook.
    """
    empathy = get_empathy_opener(seed=session_id)

    parts = [
        f"[SAFETY]\n{safety_instructions}",
        f"\n[EMPATHY]\nOpen your response with this empathy acknowledgement (you may paraphrase naturally): \"{empathy}\"",
        f"\n[UTILITY]\n{utility_prompt}",
    ]

    if include_checkin:
        checkin = get_checkin(seed=session_id)
        parts.append(f"\n[CHECK-IN]\nInclude a natural check-in: \"{checkin}\"")

    if include_one_more_thing:
        hook = get_one_more_thing(seed=session_id)
        parts.append(f"\n[CADENCE]\nEnd with a forward hook: \"{hook}\"")

    return "\n".join(parts)
