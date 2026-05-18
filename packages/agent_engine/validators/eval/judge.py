# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import json
from openai import OpenAI
from shared.config import settings

SYS_JUDGE = """Evaluate the agent's output against the expected behavior.
Return strictly JSON with {"pass": bool, "reason": "string"}
"""


class EvalJudge:
  def __init__(self) -> None:
    self.client = OpenAI()

  def grade(self, query: str, output: str, expected_behavior: str) -> dict:
    prompt = {
      "query": query,
      "agent_output": output,
      "expected_behavior": expected_behavior,
    }
    resp = self.client.chat.completions.create(
      model=settings.eval_judge_model,
      messages=[
        {"role": "system", "content": SYS_JUDGE},
        {"role": "user", "content": json.dumps(prompt)},
      ],
      temperature=0,
      response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)
