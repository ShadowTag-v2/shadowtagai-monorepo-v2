from __future__ import annotations

import logging
from agent_engine.validators.eval.cases import EVAL_SUITE
from agent_engine.validators.eval.judge import EvalJudge

logger = logging.getLogger("EvalHarness")


def run_compliance_eval_suite(agent_invoke_fn) -> bool:
    """
    agent_invoke_fn: Callable[[str, dict], str]
    Takes (prompt_id, variables) and returns the agent's literal output string.
    """
    judge = EvalJudge()
    all_passed = True

    for case in EVAL_SUITE:
        logger.info(f"Running Eval: {case.name}")
        output = agent_invoke_fn(case.prompt_id, case.variables)

        query_context = f"Variables: {case.variables}"
        result = judge.grade(query_context, output, case.expected_behavior)

        if result.get("pass"):
            logger.info(f"[PASS] {case.name}")
        else:
            logger.error(f"[FAIL] {case.name} - Reason: {result.get('reason')}")
            all_passed = False

    return all_passed
