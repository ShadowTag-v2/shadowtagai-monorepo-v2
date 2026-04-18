"""LLM Orchestrator
Handles dual-review loop with GPT-5 and HF pool.
"""

import asyncio
import os
from typing import Any

from openai import AsyncOpenAI

from app.core.model_spec import SYSTEM_ARBITER, SYSTEM_DRAFTER, SYSTEM_REVIEWER
from app.models.orchestrator import DraftSpec
from app.services.hf_pool import HFClientPool

# Initialize OpenAI client lazily
aclient = None


def get_aclient():
    global aclient
    if not aclient:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fallback for dev/test if not set, or raise
            api_key = "REDACTED_API_KEY"
        aclient = AsyncOpenAI(api_key=api_key)
    return aclient


async def gpt5(system: str, user: str, temperature: float = 0.2) -> str:
    """Wrapper for GPT-5 (or strongest available model)"""
    client = get_aclient()
    try:
        resp = await client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Placeholder for GPT-5 as it's not public API yet
            temperature=temperature,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        # Fallback or re-raise
        raise e


async def produce_with_dual_review(
    pool: HFClientPool,
    spec: DraftSpec,
    hf_gen_kwargs: dict[str, Any] | None = None,
) -> dict[str, str]:
    prompt = f"Task: {spec.task}\nConstraints: {spec.constraints or {}}\nStyle: {spec.style or 'default'}"

    # 1) Draft via HF pool (cheap/fast)
    # Using SYSTEM_DRAFTER as part of the prompt for HF models if they support system prompts,
    # or just prepending it. Most HF text-gen endpoints take a single string.
    full_prompt = f"{SYSTEM_DRAFTER}\n\n{prompt}"
    draft = await pool.text_generate(full_prompt, **(hf_gen_kwargs or {"max_new_tokens": 400}))

    # 2) Two parallel GPT-5 reviews
    review_payload = f"Draft:\n{draft}\n\nTask:\n{spec.task}"
    r1, r2 = await asyncio.gather(
        gpt5(SYSTEM_REVIEWER, review_payload),
        gpt5(SYSTEM_REVIEWER, review_payload),
    )

    # 3) Arbiter (GPT-5) to synthesize the final
    arb_payload = f"Task:\n{spec.task}\n\nDraft:\n{draft}\n\nReview A:\n{r1}\n\nReview B:\n{r2}\n"
    final_answer = await gpt5(SYSTEM_ARBITER, arb_payload)

    return {"draft": draft, "review_a": r1, "review_b": r2, "final": final_answer}
