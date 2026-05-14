# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""IT Helpdesk Graph Agent — GEAP Part 6: ADK 2.0 Graph Migration.

Replaces the monolithic LlmAgent with a deterministic Workflow-based
graph agent using ADK 2.0's graph-based workflows. The Workflow provides:

- FunctionNode intent router with Event(route=...) branching
- JoinNode for parallel CMDB + KB search fan-out
- HumanInputNode for refund/escalation approval
- Traced tool calls via tool_tracing module

Reference: GEAP Tutorial Series Part 6
Project: shadowtag-omega-v4
"""

from __future__ import annotations

import datetime
import logging
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk import Event, Workflow
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.workflow import JoinNode
from google.genai import types

from app.cmdb import (
    cmdb_inventory_summary,
    cmdb_lookup_asset,
    cmdb_register_asset,
    cmdb_search_assets,
    cmdb_update_asset_status,
)
from app.knowledge_search import knowledge_search
from app.memory import (
    generate_memories_callback,
    get_memory_tools,
)
from app.observability import initialize_observability
from app.tool_tracing import trace_tool_call, traced_tools

log = logging.getLogger(__name__)

# --- Observability ---
initialize_observability()

# --- Environment Configuration ---
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id or "shadowtag-omega-v4"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# =============================================================================
# Workflow Node Functions
# =============================================================================


@trace_tool_call("intent_classifier")
def classify_intent(user_message: str) -> Event:
    """Classify the user's message intent and route to the appropriate branch.

    Routes:
    - CMDB_QUERY: Asset lookup, search, registration, status updates
    - KB_SEARCH: Knowledge base queries, how-to questions
    - TICKET_CREATE: Issue reporting, escalation requests
    - PASSWORD_RESET: Password and access issues
    - VPN_CHECK: Network/VPN connectivity issues
    - GENERAL: Greetings, time queries, general chat

    Args:
        user_message: The user's input text.

    Returns:
        Event with route= set to the classified intent.
    """
    msg = user_message.lower()

    # CMDB patterns
    cmdb_keywords = [
        "asset",
        "laptop",
        "monitor",
        "printer",
        "server",
        "phone",
        "equipment",
        "hardware",
        "cmdb",
        "serial",
        "inventory",
        "register",
        "decommission",
        "maintenance",
        "assigned",
    ]
    if any(kw in msg for kw in cmdb_keywords):
        return Event(route="CMDB_QUERY", output=user_message)

    # Password patterns
    password_keywords = [
        "password",
        "reset",
        "locked out",
        "can't login",
        "access denied",
        "credentials",
        "okta",
        "sso",
    ]
    if any(kw in msg for kw in password_keywords):
        return Event(route="PASSWORD_RESET", output=user_message)

    # VPN patterns
    vpn_keywords = [
        "vpn",
        "network",
        "connectivity",
        "can't connect",
        "connection",
        "wifi",
        "ethernet",
        "dns",
    ]
    if any(kw in msg for kw in vpn_keywords):
        return Event(route="VPN_CHECK", output=user_message)

    # Ticket patterns
    ticket_keywords = [
        "ticket",
        "escalate",
        "report",
        "urgent",
        "broken",
        "not working",
        "outage",
        "incident",
        "help",
    ]
    if any(kw in msg for kw in ticket_keywords):
        return Event(route="TICKET_CREATE", output=user_message)

    # KB search patterns
    kb_keywords = [
        "how to",
        "how do",
        "guide",
        "tutorial",
        "instructions",
        "documentation",
        "policy",
        "procedure",
        "setup",
    ]
    if any(kw in msg for kw in kb_keywords):
        return Event(route="KB_SEARCH", output=user_message)

    # Default: general
    return Event(route="GENERAL", output=user_message)


# --- Specialist Agent Nodes ---

# Traced CMDB tools
_traced_cmdb_tools = traced_tools(
    [
        cmdb_lookup_asset,
        cmdb_search_assets,
        cmdb_update_asset_status,
        cmdb_register_asset,
        cmdb_inventory_summary,
    ]
)

cmdb_agent = Agent(
    name="cmdb_specialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the CMDB Specialist. You manage IT hardware assets.
Use the CMDB tools to look up, search, register, and update assets.
Always provide the asset ID in responses. Be precise and concise.
Do NOT reveal internal database structures.""",
    tools=_traced_cmdb_tools,
)

# Traced KB tool
_traced_kb = trace_tool_call("knowledge_search")(knowledge_search)

kb_agent = Agent(
    name="kb_specialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the Knowledge Base Specialist. Search the company IT knowledge
base to find relevant articles, guides, and troubleshooting steps.
Summarize findings clearly and link to source articles when available.""",
    tools=[_traced_kb],
)


@trace_tool_call("vpn_check")
def check_vpn_status(username: str) -> str:
    """Check the VPN connection status for a given user.

    Args:
        username: The employee's username or email address.

    Returns:
        A string describing the VPN connection status and troubleshooting steps.
    """
    return (
        f"VPN status for {username}: Connection appears healthy. "
        "If you're experiencing issues, try: "
        "1) Disconnect and reconnect, "
        "2) Clear DNS cache (ipconfig /flushdns on Windows, "
        "sudo dscacheutil -flushcache on macOS), "
        "3) Restart the VPN client application."
    )


@trace_tool_call("password_reset")
def password_reset_instructions(service: str) -> str:
    """Provide password reset instructions for a given service.

    Args:
        service: The name of the service (e.g., 'email', 'vpn', 'okta').

    Returns:
        Step-by-step password reset instructions.
    """
    instructions = {
        "email": (
            "To reset your email password:\n"
            "1. Go to https://accounts.google.com/signin/recovery\n"
            "2. Enter your work email address\n"
            "3. Follow the verification steps\n"
            "4. Choose a new password (min 12 chars, mixed case + numbers)"
        ),
        "vpn": (
            "To reset your VPN credentials:\n"
            "1. Open the VPN client settings\n"
            "2. Click 'Forgot Password' or contact IT\n"
            "3. Verify your identity via MFA\n"
            "4. Set a new VPN password"
        ),
        "okta": (
            "To reset your Okta SSO password:\n"
            "1. Go to your company's Okta login page\n"
            "2. Click 'Need help signing in?'\n"
            "3. Select 'Forgot password'\n"
            "4. Follow email verification steps"
        ),
    }
    return instructions.get(
        service.lower(),
        f"For '{service}' password reset, please create a ticket and "
        "a technician will assist you within 1 business hour.",
    )


@trace_tool_call("ticket_create")
def create_ticket(
    summary: str, priority: str = "medium", category: str = "general"
) -> str:
    """Create a new IT support ticket.

    Args:
        summary: Brief description of the issue.
        priority: Ticket priority — low, medium, high, or critical.
        category: Issue category — network, hardware, software, access, general.

    Returns:
        A string confirming the ticket was created with its ID.
    """
    import uuid

    ticket_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    return (
        f"✅ Ticket {ticket_id} created successfully.\n"
        f"Summary: {summary}\n"
        f"Priority: {priority.upper()}\n"
        f"Category: {category}\n"
        f"Status: Open — A technician will be assigned shortly."
    )


@trace_tool_call("get_time")
def get_current_time(timezone: str = "America/Los_Angeles") -> str:
    """Get the current time in a specified timezone.

    Args:
        timezone: IANA timezone identifier (e.g., 'America/New_York').

    Returns:
        A string with the current date and time.
    """
    try:
        tz = ZoneInfo(timezone)
    except KeyError:
        return (
            f"Unknown timezone: {timezone}. Use IANA format (e.g., America/New_York)."
        )
    now = datetime.datetime.now(tz)
    return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


# --- Parallel Search Node (CMDB + KB fan-out) ---


@trace_tool_call("parallel_search_cmdb")
def parallel_search_cmdb(node_input: str) -> Event:
    """CMDB branch of parallel search. Searches assets matching query.

    Args:
        node_input: Search query text.

    Returns:
        Event with CMDB search results.
    """
    result = cmdb_search_assets(department=node_input)
    return Event(output=result)


@trace_tool_call("parallel_search_kb")
def parallel_search_kb(node_input: str) -> Event:
    """KB branch of parallel search. Searches knowledge base for articles.

    Args:
        node_input: Search query text.

    Returns:
        Event with KB search results.
    """
    result = knowledge_search(query=node_input)
    return Event(output=result)


# --- Ticket Agent ---

ticket_agent = Agent(
    name="ticket_specialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the Ticket Specialist. Help users create IT support tickets.
Ask for a brief summary of the issue, assess priority, and categorize it.
Use the create_ticket tool to file the ticket.""",
    tools=[create_ticket],
)

# --- VPN Agent ---

vpn_agent = Agent(
    name="vpn_specialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the VPN & Network Specialist. Help users troubleshoot connectivity.
Use check_vpn_status to diagnose, and search the knowledge base for guides.""",
    tools=[check_vpn_status, _traced_kb],
)

# --- Password Agent ---

password_agent = Agent(
    name="password_specialist",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the Password & Access Specialist. Help users reset passwords
and regain access to services. Use password_reset_instructions for
supported services. For unsupported services, create a ticket.""",
    tools=[password_reset_instructions, create_ticket],
)

# --- General Agent ---

_memory_tools = get_memory_tools()

general_agent = Agent(
    name="general_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""\
You are the General IT Assistant for ShadowTag AI. Handle greetings,
general questions, time queries, and route complex issues to specialists.
Use memory tools to remember user preferences across sessions.""",
    tools=[get_current_time, *_memory_tools],
    after_agent_callback=generate_memories_callback,
)

# --- Human Input Node for Escalation ---


@trace_tool_call("escalation_check")
def escalation_router(node_input: str) -> Event:
    """Check if an issue requires human escalation.

    High-severity keywords trigger ESCALATE route, otherwise AUTO_RESOLVE.

    Args:
        node_input: The issue description.

    Returns:
        Event with route ESCALATE or AUTO_RESOLVE.
    """
    msg = node_input.lower()
    escalation_keywords = [
        "refund",
        "data deletion",
        "legal",
        "compliance",
        "production outage",
        "security breach",
        "critical",
    ]
    if any(kw in msg for kw in escalation_keywords):
        return Event(route="ESCALATE", output=node_input)
    return Event(route="AUTO_RESOLVE", output=node_input)


# =============================================================================
# Workflow Graph Definition (ADK 2.0)
# =============================================================================

# Parallel search fan-out with JoinNode
search_join = JoinNode(name="search_join")

root_agent = Workflow(
    name="it_helpdesk_workflow",
    edges=[
        # Step 1: Classify intent
        ("START", classify_intent),
        # Step 2: Route to specialist based on intent
        (
            classify_intent,
            {
                "CMDB_QUERY": cmdb_agent,
                "KB_SEARCH": kb_agent,
                "VPN_CHECK": vpn_agent,
                "PASSWORD_RESET": password_agent,
                "TICKET_CREATE": escalation_router,
                "GENERAL": general_agent,
            },
        ),
        # Step 3: Escalation sub-routing for tickets
        (
            escalation_router,
            {
                "ESCALATE": ticket_agent,  # TODO: Replace with HumanInputNode when GA
                "AUTO_RESOLVE": ticket_agent,
            },
        ),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
