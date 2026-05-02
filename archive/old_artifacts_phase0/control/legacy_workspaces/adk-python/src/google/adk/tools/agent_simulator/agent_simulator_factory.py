# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from google.adk.tools.agent_simulator.agent_simulator_config import AgentSimulatorConfig
from google.adk.tools.agent_simulator.agent_simulator_engine import AgentSimulatorEngine
from google.adk.tools.agent_simulator.agent_simulator_plugin import AgentSimulatorPlugin
from google.adk.tools.base_tool import BaseTool

from ...utils.feature_decorator import experimental


@experimental
class AgentSimulatorFactory:
    """Factory for creating AgentSimulator instances."""

    @staticmethod
    def create_callback(
        config: AgentSimulatorConfig,
    ) -> Callable[[BaseTool, dict[str, Any], Any], Awaitable[dict[str, Any] | None]]:
        """Creates a callback function for AgentSimulator.

        Args:
          config: The configuration for the AgentSimulator.

        Returns:
          A callable that can be used as a before_tool_callback or after_tool_callback.
        """
        simulator_engine = AgentSimulatorEngine(config)

        async def _agent_simulator_callback(tool: BaseTool, args: dict[str, Any], tool_context: Any) -> dict[str, Any] | None:
            return await simulator_engine.simulate(tool, args, tool_context)

        return _agent_simulator_callback

    @staticmethod
    def create_plugin(
        config: AgentSimulatorConfig,
    ) -> AgentSimulatorPlugin:
        """Creates an ADK Plugin for AgentSimulator.

        Args:
          config: The configuration for the AgentSimulator.

        Returns:
          An instance of AgentSimulatorPlugin that can be used as an ADK plugin.
        """
        simulator_engine = AgentSimulatorEngine(config)
        return AgentSimulatorPlugin(simulator_engine)
