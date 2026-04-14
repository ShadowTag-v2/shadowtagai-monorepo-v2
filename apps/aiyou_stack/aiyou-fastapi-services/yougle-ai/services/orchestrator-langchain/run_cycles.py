# from .chains import chain_a, chain_b, cursor_plan_mode
# from ..moderation_safety.router import moderate
# from ..shadowtag_audit.writer import attest


async def run_all(query: str, user_id: str | None, mode="default"):
    """Run1 -> Run2 -> Run3 Orchestration Loop
    """
    # Run1 – Chain A original
    # a_out = await chain_a.run1(query, mode=mode)

    # Run2 – reverse-engineer using Cursor Plan Mode
    # a_explain = await cursor_plan_mode.reverse_engineer(a_out.artifact)

    # Run3 – Chain B recreates from A's explanation
    # b_out = await chain_b.run3_from_spec(query, spec=a_explain.plan, mode=mode)

    # Adjudicate (simple: prefer passing tests + higher reranker score)
    # winner = await _adjudicate(a_out, b_out, a_explain.tests)

    # Safety pass (Google+Hive)
    # safe = await moderate(winner.content, media=winner.media)

    # Attest evidence (hashes, model, versions, tests, moderation)
    # receipt = await attest(user_id=user_id, query=query, result=winner, moderation=safe)

    return {
        "answer": "Placeholder Answer",  # safe.content,
        "explanation": "Placeholder Explanation",  # a_explain.plan,
        "diff": None,  # winner.diff,        # deltas between A and B if any
        "audit_receipt": "REC-12345",  # receipt    # ShadowTag reference
    }


async def _merge(a_out, b_out):
    """Merge two outputs when neither is clearly better. Placeholder."""
    return a_out  # Default: prefer A until real merge logic is implemented


async def _adjudicate(a_out, b_out, tests):
    # 1) quick tests from Run2
    a_ok = await tests.run(a_out.artifact)
    b_ok = await tests.run(b_out.artifact)
    # 2) reranker score (higher is better)
    a_score = await b_out.reranker.score(a_out.support)
    b_score = await a_out.reranker.score(b_out.support)
    # policy: prefer passing tests; tie → higher score; else merge
    if a_ok and (a_score >= b_score or not b_ok):
        return a_out
    if b_ok and (b_score > a_score or not a_ok):
        return b_out
    return await _merge(a_out, b_out)
