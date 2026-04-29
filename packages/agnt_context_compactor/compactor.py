"""
Context Compaction Port
Implementation of the ~30% efficiency clear_tool_uses and clear_thinking API stripping.
"""


def compact_tool_uses(context_blocks: list) -> list:
    """
    Strips raw tool_use blocks from context if they match 'clear_tool_uses' pattern.
    Maintains semantic metadata while pruning heavy execution payloads.
    """
    compacted = []
    for block in context_blocks:
        if block.get("type") == "tool_use" and block.get("name") in ["clear_tool_uses", "clear_thinking"]:
            # Prune or summarize
            compacted.append({"type": "text", "text": f"[Compacted {block['name']} execution - {len(str(block.get('input', '')))} bytes removed]"})
        else:
            compacted.append(block)
    return compacted


def compact_thinking(context_blocks: list) -> list:
    """
    Strips raw reasoning traces from extended thinking models.
    """
    compacted = []
    for block in context_blocks:
        if block.get("type") == "thinking":
            # Convert to brief metadata log
            compacted.append({"type": "text", "text": "[Internal Reasoning Compacted]"})
        else:
            compacted.append(block)
    return compacted


def apply_context_compaction(context: dict) -> dict:
    """
    Main entrypoint for context compression.
    """
    if "messages" not in context:
        return context

    compressed_messages = []
    for message in context["messages"]:
        content = message.get("content", [])
        if isinstance(content, list):
            content = compact_tool_uses(content)
            content = compact_thinking(content)
        message["content"] = content
        compressed_messages.append(message)

    context["messages"] = compressed_messages
    return context
