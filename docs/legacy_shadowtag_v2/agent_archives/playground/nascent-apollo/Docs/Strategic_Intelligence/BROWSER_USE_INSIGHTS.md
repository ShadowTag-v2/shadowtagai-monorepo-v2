# BROWSER-USE INSIGHTS

## SOURCE: browser_use/mcp/controller.py
```python
"""MCP (Model Context Protocol) tool wrapper for browser-use.

This module provides integration between MCP tools and browser-use's action registry system.
MCP tools are dynamically discovered and registered as browser-use actions.
"""

import asyncio
import logging
from typing import Any

from pydantic import Field, create_model

from browser_use.agent.views import ActionResult
from browser_use.tools.registry.service import Registry

logger = logging.getLogger(__name__)

try:
	from mcp import ClientSession, StdioServerParameters
	from mcp.client.stdio import stdio_client
	from mcp.types import TextContent, Tool

	MCP_AVAILABLE = True
except ImportError:
	MCP_AVAILABLE = False
	logger.warning('MCP SDK not installed. Install with: pip install mcp')


class MCPToolWrapper:
	"""Wrapper to integrate MCP tools as browser-use actions."""

	def __init__(self, registry: Registry, mcp_command: str, mcp_args: list[str] | None = None):
		"""Initialize MCP tool wrapper.

		Args:
			registry: Browser-use action registry to register MCP tools
			mcp_command: Command to start MCP server (e.g., "npx")
			mcp_args: Arguments for MCP command (e.g., ["@playwright/mcp@latest"])
		"""
		if not MCP_AVAILABLE:
			raise ImportError('MCP SDK not installed. Install with: pip install mcp')

		self.registry = registry
		self.mcp_command = mcp_command
		self.mcp_args = mcp_args or []
		self.session: ClientSession | None = None
		self._tools: dict[str, Tool] = {}
		self._registered_actions: set[str] = set()
		self._shutdown_event = asyncio.Event()

...
```

## SOURCE: browser_use/skill_cli/commands/browser.py
```python
"""Browser control commands."""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any

from browser_use.skill_cli.sessions import SessionInfo

logger = logging.getLogger(__name__)

COMMANDS = {
	'open',
	'click',
	'type',
	'input',
	'scroll',
	'back',
	'screenshot',
	'state',
	'switch',
	'close-tab',
	'keys',
	'select',
	'eval',
	'extract',
	'cookies',
	'wait',
	'hover',
	'dblclick',
	'rightclick',
	'get',
}


async def _execute_js(session: SessionInfo, js: str) -> Any:
	"""Execute JavaScript in the browser via CDP."""
	bs = session.browser_session
	# Get or create a CDP session for the focused target
	cdp_session = await bs.get_or_create_cdp_session(target_id=None, focus=False)
	if not cdp_session:
		raise RuntimeError('No active browser session')

	result = await cdp_session.cdp_client.send.Runtime.evaluate(
		params={'expression': js, 'returnByValue': True},
		session_id=cdp_session.session_id,
	)
	return result.get('result', {}).get('value')

...
```

## SOURCE: browser_use/skill_cli/commands/agent.py
```python
"""Agent task command handler."""

import logging
import os
from typing import Any

from browser_use.skill_cli.api_key import APIKeyRequired, require_api_key
from browser_use.skill_cli.sessions import SessionInfo

logger = logging.getLogger(__name__)


async def handle(session: SessionInfo, params: dict[str, Any]) -> Any:
	"""Handle agent run command.

	Requires API key for LLM access.
	Runs a browser-use agent with the given task.
	"""
	task = params.get('task')
	max_steps = params.get('max_steps', 100)

	if not task:
		return {'success': False, 'error': 'No task provided'}

	# Check API key for LLM access
	try:
		api_key = require_api_key('Agent tasks')
	except APIKeyRequired as e:
		return {'success': False, 'error': str(e)}

	try:
		# Import agent and LLM
		from browser_use.agent.service import Agent

		# Try to get LLM from environment
		llm = await get_llm()
		if llm is None:
			return {
				'success': False,
				'error': 'No LLM configured. Set BROWSER_USE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY',
			}

		# Create and run agent
		agent = Agent(
			task=task,
			llm=llm,
			browser_session=session.browser_session,
		)

		logger.info(f'Running agent task: {task}')
...
```

