"""Vulture whitelist — known false positives for dead code analysis."""

# dream_consolidation.py: NotebookLM is imported dynamically in try/except
from notebooklm import NotebookLM  # noqa: F401

_ = NotebookLM

# --- Pytest fixture false positives ---
# These variables are injected by pytest's fixture mechanism and look unused to vulture.
# Format: variable_name  (file: description)

# apps/agent-starter-pack/shadowtag-agent/tests/integration/test_server_e2e.py
server_fixture = None  # noqa: F841 — pytest fixture injection

# apps/aiyou_stack/aiyou-fastapi-services/tests/test_support_builder.py
setup_database = None  # noqa: F841 — pytest fixture injection

# apps/aiyou_stack/aiyou-fastapi-services/tests/agents/test_market_analyst.py
mock_anthropic_client = None  # noqa: F841 — pytest fixture injection

# apps/aiyou_stack/aiyou-fastapi-services/tests/test_tower_pilot.py
mock_bq = None  # noqa: F841 — pytest fixture injection

# apps/aiyou_stack/aiyou-fastapi-services/src/pso_nn/tests/test_weight_optimizer.py
unused_weights = None  # noqa: F841 — intentional test variable name

# apps/slides_agent_demo/tests/integration/test_server_e2e.py (mirror)
# server_fixture already whitelisted above

# --- Conditional import false positives ---
# cor_autogen_integration.py: autogen imports are inside try/except
import autogen  # noqa: F401
from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent  # noqa: F401

_ = autogen
_ = AssistantAgent
_ = GroupChat
_ = GroupChatManager
_ = UserProxyAgent

# agents.py router: conditional tool schemas
A2UI_GENERATOR_TOOL_SCHEMA = None  # noqa: F841
COMFYUI_IMAGE_TOOL_SCHEMA = None  # noqa: F841
WORKSPACE_SEARCH_TOOL_SCHEMA = None  # noqa: F841

# knowledge.py: conditional import stub
verify_workspace_access = None  # noqa: F841

# omega_kernel.py: billing_v1 used inside try/except
from google.cloud import billing_v1  # noqa: F401

_ = billing_v1
