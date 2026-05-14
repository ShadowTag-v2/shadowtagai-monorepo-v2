# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json

from openai import OpenAI

from policy_engine.objection.rules import REJECTION_RULES
from shared.config import settings
from shared.types import PolicyDecision, Verdict

SYSTEM = """You are Gate 1, a semantic objection engine.
Return ONLY strict JSON.
You evaluate pull request diffs against policy rules.
Prefer REJECT when a high-risk violation is clearly present.
Prefer REVIEW when evidence is mixed.
"""

SCHEMA_EXAMPLE = {
    "verdict": "reject",
    "rule_id": "security_regression",
    "reason": "The diff logs raw email addresses and API tokens.",
    "evidence": ["logger.info(user.email)", "os.environ['API_KEY']"],
    "confidence": 0.96,
    "metadata": {"severity": "high"},
}


class ObjectionEngine:
    def __init__(self) -> None:
        self.client = OpenAI()

    def evaluate_diff(self, pr_title: str, diff_text: str, changed_files: list[str]) -> PolicyDecision:
        prompt = {
            "rules": REJECTION_RULES,
            "pr_title": pr_title,
            "changed_files": changed_files,
            "diff": diff_text[:40000],
            "output_schema": SCHEMA_EXAMPLE,
        }

        resp = self.client.chat.completions.create(
            model=settings.eval_judge_model,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(prompt)},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        text = resp.choices[0].message.content.strip()
        data = json.loads(text)

        return PolicyDecision(
            verdict=Verdict(data["verdict"]),
            rule_id=data["rule_id"],
            reason=data["reason"],
            evidence=data.get("evidence", []),
            confidence=float(data.get("confidence", 0.0)),
            metadata=data.get("metadata", {}),
        )

    def raise_if_rejected(self, decision: PolicyDecision) -> None:
        if decision.verdict == Verdict.REJECT:
            raise RuntimeError(f"[Gate1:{decision.rule_id}] {decision.reason} | evidence={decision.evidence}")
