# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging

from src.governance.judge_six.sentinel import JudgeSentinel


class GeminiCodeAssistProxy:
    """GOD MODE: Direct Write Capability."""

    def __init__(self):
        self.judge = JudgeSentinel()

    def trigger_smart_action(self, file_path: str, new_content: str):
        """The 'Throttle' mentioned in the Walkthrough.
        Writes code to disk ONLY if Judge 6 approves.
        """
        logging.info(f"⚡ GOD MODE: Attempting write to {file_path}")

        # 1. THE BRAKE (Judge 6)
        # We verify the *content*, not just the intent.
        verdict = self.judge.evaluate(new_content)

        if verdict["status"] == "BLOCKED":
            logging.error(f"⛔ BLOCKED: {verdict['reason']}")
            return {"status": "BLOCKED", "reason": verdict["reason"]}

        # 2. THE THROTTLE (Write)
        try:
            with open(file_path, "w") as f:
                f.write(new_content)
            logging.info("✅ WRITE SUCCESS.")
            return {"status": "APPLIED_AUTOMATICALLY"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}


god_mode = GeminiCodeAssistProxy()
