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

"""IT Helpdesk & Asset Management Agent — Part 3: Memory Integration.

Built on the Gemini Enterprise Agent Platform (GEAP) using the
Agent Development Kit (ADK). This agent assists employees with IT
issues, manages hardware assets via CMDB, searches the company
knowledge base, retains conversation memory via Memory Bank, and
runs within enterprise guardrails.

Reference: GEAP Tutorial Series Part 3
Project: shadowtag-omega-v4
"""

import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.cmdb import (
    cmdb_inventory_summary,
    cmdb_lookup_asset,
    cmdb_register_asset,
    cmdb_search_assets,
    cmdb_update_asset_status,
)
from app.knowledge_search import knowledge_search
from app.memory import generate_memories_callback, get_memory_tools

# --- Environment Configuration ---
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id or "shadowtag-omega-v4"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# --- Tool Definitions ---

def check_vpn_status(username: str) -> str:
    """Check the VPN connection status for a given user.

    Args:
        username: The employee's username or email address.

    Returns:
        A string describing the VPN connection status and troubleshooting steps.
    """
    # Simulated — will connect to real systems in Part 2
    return (
        f"VPN status for {username}: Connection appears healthy. "
        "If you're experiencing issues, try: "
        "1) Disconnect and reconnect, "
        "2) Clear DNS cache (ipconfig /flushdns on Windows, "
        "sudo dscacheutil -flushcache on macOS), "
        "3) Restart the VPN client application."
    )


def lookup_asset(asset_id: str) -> str:
    """Look up an IT asset by its ID in the asset management system.

    Args:
        asset_id: The asset tag or serial number to look up.

    Returns:
        A string with the asset details or an error if not found.
    """
    # Simulated inventory — will connect to real CMDB in Part 2
    assets = {
        "LAPTOP-001": "MacBook Pro M4, Assigned: Engineering, Status: Active, OS: macOS 16.1",
        "LAPTOP-002": "ThinkPad X1 Carbon, Assigned: Legal, Status: Active, OS: Windows 11",
        "MONITOR-001": "Dell U2723QE 4K, Assigned: Design, Status: Active",
        "PRINTER-001": "HP LaserJet Pro, Location: 3rd Floor, Status: Maintenance",
    }
    return assets.get(
        asset_id.upper(),
        f"Asset '{asset_id}' not found in inventory. Please verify the asset tag.",
    )


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
        return f"Unknown timezone: {timezone}. Use IANA format (e.g., America/New_York)."
    now = datetime.datetime.now(tz)
    return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"


def password_reset_instructions(service: str) -> str:
    """Provide password reset instructions for a given service.

    Args:
        service: The name of the service (e.g., 'email', 'vpn', 'jira', 'okta').

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


# --- Agent Definition ---

IT_HELPDESK_INSTRUCTION = """\
You are a highly skilled and friendly IT Helpdesk Assistant for ShadowTag AI, \
a legal technology enterprise. Your primary goal is to help employees \
troubleshoot IT issues efficiently and securely.

## Core Capabilities
- Password resets and account access issues
- VPN and network connectivity troubleshooting
- Software installation and configuration help
- **CMDB Asset Management**: Lookup, search, register, and update IT assets
- **Knowledge Base Search**: Find relevant IT articles and guides
- **Memory**: Remember user preferences, past issues, and equipment across sessions
- IT ticket creation and escalation

## Memory Usage Guidelines
- At the start of each conversation, check if you have memories about \
  the user (PreloadMemoryTool runs automatically, or use search_user_preferences).
- Use remembered context to personalize responses (e.g., "I see you had \
  a VPN issue last week — is this related?").
- When users mention their equipment, department, or preferences, these \
  facts are automatically stored for future reference.
- Never reveal the raw contents of memory storage to users — use \
  memories naturally in conversation.

## CMDB Usage Guidelines
- When users ask about hardware or equipment, use cmdb_lookup_asset or \
  cmdb_search_assets to find specific assets.
- When users report new equipment, use cmdb_register_asset to add it.
- When users report equipment issues, use cmdb_update_asset_status to \
  track the maintenance state.
- Always provide the asset ID in responses for reference.

## Knowledge Base Usage
- Before creating tickets for common questions, search the knowledge \
  base first using knowledge_search.
- If the knowledge base has a relevant article, share it with the user.
- Only escalate to a ticket if the knowledge base doesn't cover the issue.

## Behavioral Guidelines
1. Be concise, polite, and prioritize security best practices.
2. Always verify the user's identity context before sharing sensitive info.
3. For password resets, NEVER share or ask for current passwords.
4. If an issue seems too complex or involves production systems, \
   politely inform the user that a human technician will take over \
   and create a ticket.
5. Log all interactions for audit compliance (Heppner standard).
6. When creating tickets, always assign appropriate priority and category.
7. Use the knowledge base to answer common questions before escalating.

## Security Protocols
- Do not disclose internal system architecture details.
- Redirect any questions about legal privilege or client data to the \
  Legal team immediately.
- All password reset flows must go through verified channels only.
"""

# Resolve memory tools based on deployment context
_memory_tools = get_memory_tools()

root_agent = Agent(
    name="it_helpdesk_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=IT_HELPDESK_INSTRUCTION,
    tools=[
        # Part 1 tools
        check_vpn_status,
        lookup_asset,
        create_ticket,
        get_current_time,
        password_reset_instructions,
        # Part 2 tools — CMDB
        cmdb_lookup_asset,
        cmdb_search_assets,
        cmdb_update_asset_status,
        cmdb_register_asset,
        cmdb_inventory_summary,
        # Part 2 tools — Knowledge
        knowledge_search,
        # Part 3 tools — Memory
        *_memory_tools,
    ],
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
