# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for AgentDelegatePoC — bounded sub-agent delegation."""

import json

from tools.agent_delegate_poc import AgentDelegatePoC


def test_agent_delegate_poc_initialization():
    poc = AgentDelegatePoC(main_agent_context={"test": "context"})
    assert poc.main_agent_context == {"test": "context"}


def test_delegate_task_success():
    poc = AgentDelegatePoC(main_agent_context={})
    # delegate_task returns JSON string, so we parse it
    result_json = poc.delegate_task("test task", ["view_file"], 10)
    result = json.loads(result_json)
    assert result["status"] == "success"
    assert "sub_agent_id" in result


def test_delegate_task_timeout():
    poc = AgentDelegatePoC(main_agent_context={})

    def slow_mock(_agent_id, _task, _tools):
        import time

        time.sleep(5)
        return "should not reach"

    # Override the internal simulation method (matches actual signature)
    poc._simulate_sub_agent_execution = slow_mock
    result_json = poc.delegate_task("test timeout", ["view_file"], 1)
    result = json.loads(result_json)

    assert result["status"] == "timeout"
    assert "Timeout" in result["report"]
