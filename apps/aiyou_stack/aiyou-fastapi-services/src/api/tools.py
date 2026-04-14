from duckduckgo_search import DDGS

WEB_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "perform_web_search",
        "description": "Perform stateless web searches on the internet",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
}

WORKSPACE_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_workspace_knowledge",
        "description": "Perform stateful searches inside private documents",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
}

A2UI_GENERATOR_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_a2ui",
        "description": "Emit interactive declarative React JSON payloads directly into the local client view",
        "parameters": {
            "type": "object",
            "properties": {
                "component_type": {
                    "type": "string",
                    "enum": ["SupplyChainDashboard", "SandTable", "DataGrid"],
                },
                "schema_data": {"type": "object"},
                "sub_components": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["component_type", "schema_data"],
        },
    },
}


def perform_web_search(query: str) -> str:
    try:
        results = DDGS().text(query, max_results=3)
        return (
            "\n---\n".join(
                [
                    f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nURL: {r.get('href')}"
                    for r in results
                ],
            )
            if results
            else "No results."
        )
    except Exception as e:
        return f"Search failed: {e!s}"
