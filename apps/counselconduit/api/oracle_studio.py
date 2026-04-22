# apps/counselconduit/api/oracle_studio.py
"""Oracle Studio — 7-Prompt Legal Research System with S.E.U. Framework.

The Oracle Studio runs a multi-prompt pipeline for deep legal research:

1. INTAKE — Parse the raw client question into structured legal issues
2. JURISDICTION — Identify applicable jurisdictions + governing law
3. AUTHORITY — Find primary authorities (statutes, regulations, case law)
4. ANALYSIS — Apply authorities to facts (IRAC/CREAC method)
5. COUNTER — Identify opposing arguments and weaknesses
6. SYNTHESIS — Generate the Oracle Memo with citations
7. ATTESTATION — Generate Kovel attestation receipt

S.E.U. Framework: Safety → Empathy → Utility ordering on all stages.
Each prompt is structurally isolated from user input (OWASP LLM01).
The system prompt is injected server-side, never from the client.

Prompt Repetition (arXiv 2512.14982) is applied at each stage for
non-reasoning models to boost accuracy by 1-8% at zero cost.
"""

from __future__ import annotations

import logging
from enum import StrEnum

from opentelemetry import trace
from pydantic import BaseModel, Field

logger = logging.getLogger("counselconduit.oracle_studio")
tracer = trace.get_tracer("counselconduit.oracle_studio")


# ── Oracle Stages ─────────────────────────────────────────────────────────


class OracleStage(StrEnum):
    INTAKE = "intake"
    JURISDICTION = "jurisdiction"
    AUTHORITY = "authority"
    ANALYSIS = "analysis"
    COUNTER = "counter"
    SYNTHESIS = "synthesis"
    ATTESTATION = "attestation"


# Safety directives — applied to every S.E.U. wrapped prompt
_SAFETY_DIRECTIVES = (
    "This is a privileged attorney-client communication protected under Kovel. "
    "Never log client PII. Never give direct legal advice — identify issues only. "
    "All outputs are for attorney review, not client consumption."
)

# System prompts — NEVER exposed to client, NEVER in logs (OWASP LLM07)
_SYSTEM_PROMPTS: dict[OracleStage, str] = {
    OracleStage.INTAKE: (
        "You are a legal intake specialist. Parse the following question into "
        "structured legal issues. Identify: (1) parties involved, (2) legal "
        "theories, (3) relevant facts, (4) relief sought. Output as structured JSON."
    ),
    OracleStage.JURISDICTION: (
        "You are a jurisdictional analyst. Given the legal issues identified, "
        "determine: (1) applicable jurisdictions (federal, state, international), "
        "(2) governing statutes, (3) any conflict of laws issues. Be precise."
    ),
    OracleStage.AUTHORITY: (
        "You are a legal research specialist. Find the most relevant primary "
        "authorities: (1) statutes and regulations, (2) binding case law, "
        "(3) persuasive authority. Provide full citations in Bluebook format."
    ),
    OracleStage.ANALYSIS: (
        "You are a legal analyst using the IRAC method. For each issue: "
        "(1) state the Issue, (2) identify the Rule from authorities, "
        "(3) Apply the rule to the facts, (4) state your Conclusion. "
        "Be objective and acknowledge uncertainty where it exists."
    ),
    OracleStage.COUNTER: (
        "You are an opposing counsel simulator. For each conclusion reached, "
        "identify: (1) the strongest counter-arguments, (2) distinguishing "
        "cases, (3) factual weaknesses, (4) procedural vulnerabilities."
    ),
    OracleStage.SYNTHESIS: (
        "You are drafting the Oracle Memo. Synthesize all preceding analysis "
        "into a professional legal memorandum with: (1) executive summary, "
        "(2) questions presented, (3) brief answers, (4) discussion with "
        "inline citations, (5) conclusion and recommendations. Use formal "
        "legal writing style. Every citation must be verifiable."
    ),
    OracleStage.ATTESTATION: ("Generate the Kovel attestation metadata for this session."),
}

# Non-reasoning models where prompt repetition improves accuracy
_NON_REASONING_MODELS = {
    "gemini-3.1-flash-lite-preview",
    "gpt-4.1",
    "gpt-4o-mini",
    "claude-3.5-haiku",
    "pplx-api",
}


# ── Models ─────────────────────────────────────────────────────────────────


class OracleRequest(BaseModel):
    """Client's research request to Oracle Studio."""

    session_id: str
    attorney_id: str
    firm_id: str
    client_id: str
    question: str = Field(..., min_length=10, max_length=10000)
    model_preference: str | None = None
    include_counter: bool = True
    jurisdiction_hint: str | None = None


class OracleStageResult(BaseModel):
    """Result from a single Oracle stage."""

    stage: OracleStage
    content: str
    model_used: str
    tokens_consumed: int
    citations: list[str] = Field(default_factory=list)


class OracleResponse(BaseModel):
    """Complete Oracle Studio response."""

    session_id: str
    stages: list[OracleStageResult]
    memo: str  # The final synthesized memo
    total_tokens: int
    attestation_id: str | None = None
    citations: list[str] = Field(default_factory=list)


# ── Prompt Repetition (arXiv 2512.14982) ──────────────────────────────────


def _apply_prompt_repetition(
    system_prompt: str,
    user_content: str,
    model_id: str,
    stage: OracleStage,
) -> tuple[str, str]:
    """Apply prompt repetition for non-reasoning models.

    Returns (system_prompt, user_content) — either original or with
    the user content repeated for accuracy boost.
    """
    if model_id not in _NON_REASONING_MODELS:
        return system_prompt, user_content

    # Repeat the instruction at the end of user content
    repeated = (
        f"{user_content}\n\n---\n\n[INSTRUCTION REPEAT — {stage.value.upper()}]\n{system_prompt}\n\nAnalyze the above content and respond precisely."
    )
    return system_prompt, repeated


# ── LiteLLM Integration ──────────────────────────────────────────────────


async def _call_llm(
    system_prompt: str,
    user_content: str,
    model_id: str,
    stage: OracleStage,
) -> tuple[str, int]:
    """Call LLM via LiteLLM with prompt repetition for non-reasoning models.

    Returns (response_text, tokens_consumed).
    Instrumented with OpenTelemetry tracing.
    """
    with tracer.start_as_current_span(
        f"oracle.llm.{stage.value}",
        attributes={
            "oracle.stage": stage.value,
            "oracle.model": model_id,
            "oracle.prompt_repetition": model_id in _NON_REASONING_MODELS,
        },
    ) as span:
        # Apply prompt repetition
        sys_prompt, user_msg = _apply_prompt_repetition(system_prompt, user_content, model_id, stage)

        try:
            import litellm

            response = await litellm.acompletion(
                model=model_id,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=4096,
                temperature=0.3,  # Lower temp for legal precision
            )

            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0

            span.set_attribute("oracle.tokens", tokens)
            span.set_attribute("oracle.response_length", len(content))

            logger.info(
                "LLM call: stage=%s model=%s tokens=%d",
                stage.value,
                model_id,
                tokens,
            )
            return content, tokens

        except ImportError:
            span.set_attribute("oracle.error", "litellm_not_installed")
            logger.warning("litellm not installed — returning placeholder")
            return f"[{stage.value}] Analysis pending — litellm not installed", 0
        except Exception as e:
            span.set_attribute("oracle.error", str(e))
            span.record_exception(e)
            logger.error("LLM call failed: stage=%s error=%s", stage.value, e)
            return f"[{stage.value}] Error: LLM call failed", 0


# ── Pipeline Execution ────────────────────────────────────────────────────


async def run_oracle_pipeline(req: OracleRequest) -> OracleResponse:
    """Execute the full 7-stage Oracle Studio pipeline.

    Each stage passes its output to the next stage as context.
    System prompts are structurally isolated (OWASP LLM01).
    Prompt repetition applied for non-reasoning models (arXiv 2512.14982).
    Instrumented with OpenTelemetry distributed tracing.
    """
    with tracer.start_as_current_span(
        "oracle.pipeline",
        attributes={
            "oracle.session_id": req.session_id,
            "oracle.attorney_id": req.attorney_id,
            "oracle.firm_id": req.firm_id,
            "oracle.include_counter": req.include_counter,
        },
    ):
        try:
            from apps.counselconduit.api.model_router import (
                ModelRequest,
                select_model,
            )
        except ImportError:
            from api.model_router import (  # type: ignore[no-redef]
                ModelRequest,
                select_model,
            )

        stages: list[OracleStageResult] = []
        total_tokens = 0
        context = req.question

        # Add jurisdiction hint if provided
        if req.jurisdiction_hint:
            context = f"[Jurisdiction: {req.jurisdiction_hint}]\n\n{context}"

    # Select model
    model_config = select_model(
        ModelRequest(
            preferred_model=req.model_preference,
            query_complexity="high",  # Legal research = always high
            user_tier="professional",
        )
    )
    model_id = model_config.model_id

    for stage in OracleStage:
        if stage == OracleStage.COUNTER and not req.include_counter:
            continue
        if stage == OracleStage.ATTESTATION:
            # Attestation is handled separately by kovel_attestation.py
            break

        system_prompt = _SYSTEM_PROMPTS[stage]

        # S.E.U. wrapping for client-facing stages (INTAKE and SYNTHESIS)
        if stage in (OracleStage.INTAKE, OracleStage.SYNTHESIS):
            try:
                try:
                    from apps.counselconduit.api.empathy_templates import wrap_seu_prompt
                except ImportError:
                    from api.empathy_templates import wrap_seu_prompt  # type: ignore[no-redef]

                system_prompt = wrap_seu_prompt(
                    safety_instructions=_SAFETY_DIRECTIVES,
                    utility_prompt=system_prompt,
                    session_id=req.session_id,
                    include_one_more_thing=(stage == OracleStage.SYNTHESIS),
                )
            except Exception as e:
                logger.warning("S.E.U. wrapping failed (using raw prompt): %s", e)

        # Call LLM with prompt repetition
        content, tokens = await _call_llm(
            system_prompt=system_prompt,
            user_content=context,
            model_id=model_id,
            stage=stage,
        )

        # Fingerprint client-facing outputs (Risk #63)
        if stage in (OracleStage.INTAKE, OracleStage.SYNTHESIS):
            try:
                try:
                    from apps.counselconduit.api.empathy_templates import (
                        fingerprint_output,
                        get_empathy_opener,
                    )
                except ImportError:
                    from api.empathy_templates import (  # type: ignore[no-redef]
                        fingerprint_output,
                        get_empathy_opener,
                    )

                expected = get_empathy_opener(seed=req.session_id)
                fp = fingerprint_output(content, expected)
                if fp.mutation_detected:
                    logger.warning(
                        "Empathy mutation detected: stage=%s session=%s",
                        stage.value,
                        req.session_id,
                    )
            except Exception:
                pass  # Fingerprinting is non-fatal

        result = OracleStageResult(
            stage=stage,
            content=content,
            model_used=model_id,
            tokens_consumed=tokens,
        )

        stages.append(result)
        total_tokens += tokens

        # Chain: each stage's output becomes next stage's context
        context = f"{context}\n\n--- {stage.value.upper()} ---\n{content}"

    # Extract memo from synthesis stage
    memo = next(
        (s.content for s in stages if s.stage == OracleStage.SYNTHESIS),
        "Oracle memo generation pending.",
    )

    # Collect all citations
    all_citations = []
    for stage_result in stages:
        all_citations.extend(stage_result.citations)

    # Store session in Firestore
    try:
        try:
            from apps.counselconduit.api.firestore_client import store_session
        except ImportError:
            from api.firestore_client import store_session  # type: ignore[no-redef]

        await store_session(
            req.firm_id,
            {
                "session_id": req.session_id,
                "attorney_id": req.attorney_id,
                "client_id": req.client_id,
                "model_used": model_id,
                "total_tokens": total_tokens,
                "stage_count": len(stages),
                "type": "oracle_studio",
            },
        )
    except Exception as e:
        logger.warning("Firestore store failed (non-fatal): %s", e)

    return OracleResponse(
        session_id=req.session_id,
        stages=stages,
        memo=memo,
        total_tokens=total_tokens,
        citations=list(set(all_citations)),
    )
