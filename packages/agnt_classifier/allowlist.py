# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tool Allowlist — Defines auto-approved tools that skip classification.

Ported from Claude Code v2.1.91: SAFE_YOLO_ALLOWLISTED_TOOLS (25 tools).
Mapped to AGNT tool identifiers.

Reference: AGNT STATE B Spec P2.2
"""

from __future__ import annotations

# --- Auto-Approved Tools (skip classifier entirely) ---
# These tools have no destructive side effects and can run under YOLO/STATE A.

SAFE_ALLOWLIST: set[str] = {
    # Read-only file operations
    "view_file",
    "list_dir",
    "grep_search",
    # Search & research
    "search_web",
    "read_url_content",
    # MCP read-only operations
    "mcp_chrome-devtools-mcp_take_snapshot",
    "mcp_chrome-devtools-mcp_take_screenshot",
    "mcp_chrome-devtools-mcp_list_pages",
    "mcp_chrome-devtools-mcp_list_console_messages",
    "mcp_chrome-devtools-mcp_list_network_requests",
    "mcp_chrome-devtools-mcp_get_console_message",
    "mcp_chrome-devtools-mcp_get_network_request",
    "mcp_google-developer-knowledge_search_documents",
    "mcp_google-developer-knowledge_get_documents",
    "mcp_google-developer-knowledge_answer_query",
    "mcp_sequential-thinking_sequentialthinking",
    "mcp_firebase-mcp-server_firebase_get_environment",
    "mcp_firebase-mcp-server_firebase_get_project",
    "mcp_firebase-mcp-server_firebase_list_projects",
    "mcp_firebase-mcp-server_firebase_list_apps",
    "mcp_firebase-mcp-server_firebase_get_sdk_config",
    "mcp_firebase-mcp-server_firebase_get_security_rules",
    "mcp_firebase-mcp-server_firestore_get_document",
    "mcp_firebase-mcp-server_firestore_list_documents",
    "mcp_firebase-mcp-server_firestore_list_collections",
    "mcp_firebase-mcp-server_functions_get_logs",
    "mcp_StitchMCP_list_projects",
    "mcp_StitchMCP_get_project",
    "mcp_StitchMCP_get_screen",
    "mcp_StitchMCP_list_screens",
    "mcp_StitchMCP_list_design_systems",
    # Status checks
    "command_status",
}

# --- Classifier-Required Tools ---
# These require Stage 1 (fast) or Stage 2 (thinking) classification.

CLASSIFIER_REQUIRED: set[str] = {
    # File mutations
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    # Shell execution
    "run_command",
    "send_command_input",
    # MCP mutations
    "mcp_firebase-mcp-server_firestore_add_document",
    "mcp_firebase-mcp-server_firestore_update_document",
    "mcp_firebase-mcp-server_firestore_delete_document",
    "mcp_firebase-mcp-server_firebase_init",
    "mcp_chrome-devtools-mcp_click",
    "mcp_chrome-devtools-mcp_fill",
    "mcp_chrome-devtools-mcp_navigate_page",
    "mcp_chrome-devtools-mcp_evaluate_script",
    "mcp_StitchMCP_generate_screen_from_text",
    "mcp_StitchMCP_edit_screens",
    "mcp_StitchMCP_create_design_system",
    # Browser interactions
    "browser_subagent",
}


def is_allowlisted(tool_id: str) -> bool:
    """Check if a tool is in the auto-approved allowlist."""
    return tool_id in SAFE_ALLOWLIST


def requires_classifier(tool_id: str) -> bool:
    """Check if a tool requires classifier evaluation."""
    if is_allowlisted(tool_id):
        return False
    return tool_id in CLASSIFIER_REQUIRED or tool_id not in SAFE_ALLOWLIST
