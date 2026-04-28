# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# ------------------------------------------------------------------------------
# AgentService Stub - Restored for ShadowTag Omega v2
# ------------------------------------------------------------------------------


class AgentService:
    @staticmethod
    def list_agents():
        return [{"id": "judge_six", "name": "Judge 6", "model": "gemini-3.1-flash-lite-preview"}]

    @staticmethod
    def get_agent(agent_id: str):
        if agent_id == "judge_six":
            return {"id": "judge_six", "status": "active"}
        return None
