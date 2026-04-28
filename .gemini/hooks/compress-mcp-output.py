#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
AfterTool Hook: Compress verbose MCP JSON output to flat CSV.
Saves ~70% of context tokens on list_log_entries, list_timeseries, etc.

Invariant #71: AfterTool hooks MUST compress verbose JSON output.
Protocol: stdin=JSON (hook input), stdout=JSON (hook output), stderr=debug.
"""

import json
import sys
import csv
import io


def compress_log_entries(data: list) -> str:
    """Convert Cloud Logging entries to CSV."""
    if not data:
        return "No log entries found."
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["timestamp", "severity", "logName", "textPayload"])
    for entry in data[:100]:  # Cap at 100 entries
        writer.writerow(
            [
                entry.get("timestamp", ""),
                entry.get("severity", ""),
                entry.get("logName", "").split("/")[-1],
                str(entry.get("textPayload", entry.get("jsonPayload", "")))[:200],
            ]
        )
    return out.getvalue()


def compress_timeseries(data: list) -> str:
    """Convert Cloud Monitoring timeseries to CSV."""
    if not data:
        return "No timeseries data found."
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["metric", "resource", "time", "value"])
    for ts in data[:50]:
        metric = ts.get("metric", {}).get("type", "unknown")
        resource = ts.get("resource", {}).get("type", "unknown")
        for point in ts.get("points", [])[:20]:
            interval = point.get("interval", {})
            value = point.get("value", {})
            val_str = str(list(value.values())[0]) if value else ""
            writer.writerow([metric.split("/")[-1], resource, interval.get("endTime", ""), val_str])
    return out.getvalue()


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError, EOFError:
        # No input or bad JSON — pass through
        json.dump({"decision": "allow"}, sys.stdout)
        return

    tool_name = hook_input.get("toolName", "")
    tool_output = hook_input.get("toolResult", "")

    print(f"[compress-mcp-output] Processing tool: {tool_name}", file=sys.stderr)

    # Only compress known verbose tools
    compressed = None
    try:
        if isinstance(tool_output, str):
            parsed = json.loads(tool_output)
        else:
            parsed = tool_output

        if "list_log_entries" in tool_name:
            entries = parsed if isinstance(parsed, list) else parsed.get("entries", [])
            compressed = compress_log_entries(entries)
        elif "list_timeseries" in tool_name or "query_range" in tool_name:
            series = parsed if isinstance(parsed, list) else parsed.get("timeSeries", [])
            compressed = compress_timeseries(series)
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        print(f"[compress-mcp-output] Skipping compression: {e}", file=sys.stderr)

    if compressed:
        original_len = len(str(tool_output))
        compressed_len = len(compressed)
        savings = round((1 - compressed_len / max(original_len, 1)) * 100)
        print(
            f"[compress-mcp-output] Compressed {original_len} → {compressed_len} chars ({savings}% saved)",
            file=sys.stderr,
        )

        json.dump({"decision": "allow", "toolResultOverride": compressed}, sys.stdout)
    else:
        json.dump({"decision": "allow"}, sys.stdout)


if __name__ == "__main__":
    main()
