"""Research Tools for Multi-Source Orchestration

Defines FunctionTool declarations for Drive, Gmail, and Web search
to be used with GeminiFunctionCaller for parallel research execution.

Integration:
- Uses existing FunctionTool pattern from gemini_function_calling.py
- Connects to Google APIs via OAuth (already authenticated)
- Applies ATP_519_scan to aggregated results
"""

import os
from typing import Any

from src.core.gemini_function_calling import FunctionTool

# Google API imports (OAuth already configured)
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False


# ============================================================================
# DRIVE SEARCH TOOL
# ============================================================================


def drive_search_impl(
    query: str,
    max_results: int = 10,
    file_type: str | None = None,
    modified_after: str | None = None,
) -> dict[str, Any]:
    """Search Google Drive for documents matching query.

    Args:
        query: Search query string
        max_results: Maximum results to return (default 10)
        file_type: Optional filter (document, spreadsheet, presentation, pdf)
        modified_after: Optional ISO date to filter by modification date

    Returns:
        Dict with documents found, count, and metadata

    """
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "source": "drive",
            "status": "unavailable",
            "error": "Google APIs not installed",
            "results": [],
            "count": 0,
        }

    try:
        # Build Drive service (OAuth credentials from environment)
        creds = _get_google_credentials()
        if not creds:
            return {
                "source": "drive",
                "status": "not_authenticated",
                "error": "No valid Google credentials found",
                "results": [],
                "count": 0,
            }

        service = build("drive", "v3", credentials=creds)

        # Build query string
        search_query = f"fullText contains '{query}'"

        if file_type:
            mime_types = {
                "document": "application/vnd.google-apps.document",
                "spreadsheet": "application/vnd.google-apps.spreadsheet",
                "presentation": "application/vnd.google-apps.presentation",
                "pdf": "application/pdf",
            }
            if file_type in mime_types:
                search_query += f" and mimeType='{mime_types[file_type]}'"

        if modified_after:
            search_query += f" and modifiedTime > '{modified_after}'"

        # Execute search
        results = (
            service.files()
            .list(
                q=search_query,
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, webViewLink, owners)",
            )
            .execute()
        )

        files = results.get("files", [])

        return {
            "source": "drive",
            "status": "success",
            "query": query,
            "results": [
                {
                    "id": f.get("id"),
                    "name": f.get("name"),
                    "type": _mime_to_type(f.get("mimeType")),
                    "modified": f.get("modifiedTime"),
                    "link": f.get("webViewLink"),
                    "owner": f.get("owners", [{}])[0].get("displayName", "Unknown"),
                }
                for f in files
            ],
            "count": len(files),
        }

    except Exception as e:
        return {"source": "drive", "status": "error", "error": str(e), "results": [], "count": 0}


drive_search_tool = FunctionTool(
    name="drive_search",
    description="Search Google Drive for internal documents, spreadsheets, presentations and files. Use for internal company knowledge and documentation.",
    function=drive_search_impl,
    parameters={
        "query": {
            "type": "string",
            "description": "Search query string to find relevant Drive documents",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return (default 10)",
        },
        "file_type": {
            "type": "string",
            "description": "Optional: Filter by type (document, spreadsheet, presentation, pdf)",
        },
        "modified_after": {
            "type": "string",
            "description": "Optional: ISO date string to filter by modification date",
        },
    },
)


# ============================================================================
# GMAIL SEARCH TOOL
# ============================================================================


def gmail_search_impl(
    query: str, max_results: int = 10, include_attachments: bool = False,
) -> dict[str, Any]:
    """Search Gmail for email threads matching query.

    Args:
        query: Gmail search query (supports operators: from:, to:, subject:, etc.)
        max_results: Maximum threads to return (default 10)
        include_attachments: Whether to include attachment metadata

    Returns:
        Dict with email threads found, count, and metadata

    """
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "source": "gmail",
            "status": "unavailable",
            "error": "Google APIs not installed",
            "results": [],
            "count": 0,
        }

    try:
        creds = _get_google_credentials()
        if not creds:
            return {
                "source": "gmail",
                "status": "not_authenticated",
                "error": "No valid Google credentials found",
                "results": [],
                "count": 0,
            }

        service = build("gmail", "v1", credentials=creds)

        # Search for messages
        results = (
            service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        )

        messages = results.get("messages", [])

        # Get message details
        email_results = []
        for msg in messages[:max_results]:
            msg_detail = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"],
                )
                .execute()
            )

            headers = {
                h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])
            }

            result = {
                "id": msg["id"],
                "thread_id": msg_detail.get("threadId"),
                "subject": headers.get("Subject", "(no subject)"),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "date": headers.get("Date", ""),
                "snippet": msg_detail.get("snippet", ""),
            }

            if include_attachments:
                parts = msg_detail.get("payload", {}).get("parts", [])
                result["attachments"] = [p.get("filename") for p in parts if p.get("filename")]

            email_results.append(result)

        return {
            "source": "gmail",
            "status": "success",
            "query": query,
            "results": email_results,
            "count": len(email_results),
        }

    except Exception as e:
        return {"source": "gmail", "status": "error", "error": str(e), "results": [], "count": 0}


gmail_search_tool = FunctionTool(
    name="gmail_search",
    description="Search Gmail for email threads matching query. Returns subjects, senders, dates, and snippets. Use for finding decisions, communications, and context from email threads.",
    function=gmail_search_impl,
    parameters={
        "query": {
            "type": "string",
            "description": "Gmail search query (supports operators: from:, to:, subject:, etc.)",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of email threads to return (default 10)",
        },
        "include_attachments": {
            "type": "boolean",
            "description": "Whether to include attachment metadata (default false)",
        },
    },
)


# ============================================================================
# WEB SEARCH TOOL
# ============================================================================


def web_search_impl(
    query: str,
    max_results: int = 10,
    site_filter: str | None = None,
    date_restrict: str | None = None,
) -> dict[str, Any]:
    """Search the public web for information.

    Args:
        query: Web search query
        max_results: Maximum results (default 10)
        site_filter: Optional domain restriction (e.g., 'arxiv.org')
        date_restrict: Optional recency filter (d=day, w=week, m=month, y=year)

    Returns:
        Dict with search results, count, and metadata

    """
    try:
        # Use Google Custom Search API if available
        api_key = os.environ.get("GOOGLE_SEARCH_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

        if api_key and search_engine_id:
            return _google_custom_search(
                query, max_results, site_filter, date_restrict, api_key, search_engine_id,
            )

        # Fallback: Return empty with note to use built-in WebSearch
        return {
            "source": "web",
            "status": "fallback_required",
            "note": "Use built-in WebSearch tool - Google Custom Search not configured",
            "query": query,
            "results": [],
            "count": 0,
        }

    except Exception as e:
        return {"source": "web", "status": "error", "error": str(e), "results": [], "count": 0}


def _google_custom_search(
    query: str,
    max_results: int,
    site_filter: str | None,
    date_restrict: str | None,
    api_key: str,
    search_engine_id: str,
) -> dict[str, Any]:
    """Execute Google Custom Search API query."""
    from googleapiclient.discovery import build

    service = build("customsearch", "v1", developerKey=api_key)

    # Build search query
    search_query = query
    if site_filter:
        search_query = f"site:{site_filter} {query}"

    # Execute search
    results = (
        service.cse()
        .list(
            q=search_query,
            cx=search_engine_id,
            num=min(max_results, 10),  # API limit is 10 per request
            dateRestrict=date_restrict,
        )
        .execute()
    )

    items = results.get("items", [])

    return {
        "source": "web",
        "status": "success",
        "query": query,
        "results": [
            {
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "displayLink": item.get("displayLink"),
            }
            for item in items
        ],
        "count": len(items),
        "total_results": results.get("searchInformation", {}).get("totalResults", 0),
    }


web_search_tool = FunctionTool(
    name="web_search",
    description="Search the public web for information on a topic. Returns titles, URLs, and snippets from relevant pages. Use for external/public information, trends, and competitor research.",
    function=web_search_impl,
    parameters={
        "query": {"type": "string", "description": "Web search query"},
        "max_results": {"type": "integer", "description": "Maximum number of results (default 10)"},
        "site_filter": {
            "type": "string",
            "description": "Optional: Restrict to specific domain (e.g., 'arxiv.org')",
        },
        "date_restrict": {
            "type": "string",
            "description": "Optional: Restrict by recency (d=day, w=week, m=month, y=year)",
        },
    },
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _get_google_credentials() -> Credentials | None:
    """Get Google OAuth credentials from environment or credential file.

    Looks for:
    1. GOOGLE_APPLICATION_CREDENTIALS env var
    2. ~/.config/google/credentials.json
    3. OAuth token from prior authentication
    """
    try:
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and os.path.exists(creds_path):
            # Load from file
            from google.oauth2 import service_account

            return service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=[
                    "https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/gmail.readonly",
                ],
            )

        # Try user credentials
        token_path = os.path.expanduser("~/.config/google/token.json")
        if os.path.exists(token_path):
            from google.oauth2.credentials import Credentials

            return Credentials.from_authorized_user_file(token_path)

        return None

    except Exception:
        return None


def _mime_to_type(mime_type: str) -> str:
    """Convert MIME type to friendly name."""
    mime_map = {
        "application/vnd.google-apps.document": "document",
        "application/vnd.google-apps.spreadsheet": "spreadsheet",
        "application/vnd.google-apps.presentation": "presentation",
        "application/pdf": "pdf",
        "application/vnd.google-apps.folder": "folder",
    }
    return mime_map.get(mime_type, mime_type.rsplit("/", maxsplit=1)[-1] if mime_type else "unknown")


# ============================================================================
# TOOL REGISTRY
# ============================================================================

RESEARCH_TOOLS = [drive_search_tool, gmail_search_tool, web_search_tool]


def get_research_tools() -> list[FunctionTool]:
    """Get all research tools for registration with GeminiFunctionCaller."""
    return RESEARCH_TOOLS


def check_tool_availability() -> dict[str, bool]:
    """Check which research tools are available based on credentials/config."""
    creds = _get_google_credentials()
    has_search_api = bool(
        os.environ.get("GOOGLE_SEARCH_API_KEY") and os.environ.get("GOOGLE_SEARCH_ENGINE_ID"),
    )

    return {
        "drive_search": creds is not None,
        "gmail_search": creds is not None,
        "web_search": has_search_api or True,  # Fallback available
        "google_apis_installed": GOOGLE_APIS_AVAILABLE,
    }
