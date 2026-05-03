#!/usr/bin/env python3
import json
import logging
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

logging.basicConfig(level=logging.INFO)

# --- CONFIG & TOOLS ---

try:
    with open("antigravity_system_prompt.txt") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "You are ANTIGRAVITY. (System prompt file not found.)"

TOOL_DEFINITIONS = {
    "function_declarations": [
        {
            "name": "code_search_tool",
            "description": "Search the codebase using regex (ripgrep). Use this to find code, definitions, or references.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "The regex or string to search for.",
                    },
                    "path": {
                        "type": "STRING",
                        "description": "Directory to search. Defaults to '.' (current dir).",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "list_files_tool",
            "description": "List files in a directory to understand the project structure.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "path": {
                        "type": "STRING",
                        "description": "Directory path to list. Defaults to '.'.",
                    },
                },
            },
        },
        {
            "name": "read_file_tool",
            "description": "Read the contents of a file. Returns the first 200 lines.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "path": {
                        "type": "STRING",
                        "description": "Path to the file to read.",
                    },
                },
                "required": ["path"],
            },
        },
    ],
}


def code_search_tool(query: str, path: str = ".") -> dict:
    """Executes ripgrep."""
    try:
        # Limit output to 200 lines to avoid blowing context
        cmd = ["rg", "-n", "--no-heading", "--max-columns=200", "--max-count=50", query, path]
        logging.info(f"Running: {' '.join(cmd)}")
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=5).decode("utf-8")
        lines = output.splitlines()
        if len(lines) >= 50:
            lines.append("... (truncated at 50 matches)")
        return {"result": "\n".join(lines)}
    except subprocess.CalledProcessError as e:
        # rg returns 1 if no matches found
        if e.returncode == 1:
            return {"result": "No matches found."}
        return {"error": f"Search failed: {e.output.decode('utf-8')}"}
    except Exception as e:
        return {"error": str(e)}


def list_files_tool(path: str = ".") -> dict:
    """Lists files using find (or ls)."""
    try:
        cmd = ["find", path, "-maxdepth", "2", "-not", "-path", "*/.*"]
        logging.info(f"Running: {' '.join(cmd)}")
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=2).decode("utf-8")
        return {"result": output}
    except Exception as e:
        return {"error": str(e)}


def read_file_tool(path: str) -> dict:
    """Reads file contents (first 200 lines)."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= 200:
                    lines.append("... (truncated at 200 lines)")
                    break
                lines.append(line.rstrip())
        return {"result": "\n".join(lines)}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except Exception as e:
        return {"error": str(e)}


# --- GEMINI CLIENT ---


def pick_model(tier: str) -> str:
    t = (tier or "FREE").upper()
    if t == "PRO":
        return "models/gemini-3.1-flash-lite-preview"
    if t == "FLASH":
        return "models/gemini-3.1-flash-lite-preview"
    return "models/gemini-3.1-flash-lite-preview"


def call_gemini_turn(model: str, conversation_history: list, tools=None) -> dict:
    """Make a single API call to Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={api_key}"
    body = {"contents": conversation_history, "tools": [tools] if tools else []}

    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"})

    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


TOOL_DISPATCH = {
    "code_search_tool": code_search_tool,
    "list_files_tool": list_files_tool,
    "read_file_tool": read_file_tool,
}


def execute_function_calls(parts: list) -> list:
    """Execute function calls and return EXACTLY one FunctionResponse per FunctionCall.

    The Gemini API enforces a strict 1:1 contract between FunctionCall parts
    in the model turn and FunctionResponse parts in the function turn.
    Violating this invariant causes a 400 Bad Request.

    Every call is individually wrapped in try/except so a single tool failure
    never drops a response from the batch.
    """
    responses = []
    for part in parts:
        fc = part.get("functionCall")
        if not fc:
            continue

        fn_name = fc.get("name", "__unknown__")
        args = fc.get("args", {})
        logging.info(f"🤖 Tool Call: {fn_name}({args})")

        try:
            tool_fn = TOOL_DISPATCH.get(fn_name)
            if tool_fn is None:
                result = {"error": f"Unknown tool: {fn_name}"}
            else:
                result = tool_fn(**args)
        except Exception as exc:
            logging.exception(f"Tool '{fn_name}' crashed")
            result = {"error": f"Tool execution failed: {exc!s}"}

        responses.append({"functionResponse": {"name": fn_name, "response": result}})

    # Invariant: response count MUST equal function-call count
    call_count = sum(1 for p in parts if "functionCall" in p)
    if len(responses) != call_count:
        logging.error(
            "CRITICAL: Response/call count mismatch — %d responses for %d calls",
            len(responses),
            call_count,
        )
    return responses


def run_agent_loop(model: str, user_msg: str) -> str:
    """Runs the ReAct loop: Prompt -> Model -> [Tool -> Model]* -> Answer"""
    history = [
        {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
        {"role": "user", "parts": [{"text": user_msg}]},
    ]

    max_turns = 5
    for _ in range(max_turns):
        try:
            resp = call_gemini_turn(model, history, tools=TOOL_DEFINITIONS)
        except Exception as e:
            return f"API Error: {e!s}"

        if "candidates" not in resp or not resp["candidates"]:
            return f"Error: No candidates. {json.dumps(resp)}"

        candidate = resp["candidates"][0]
        content = candidate.get("content") or {}
        model_parts = content.get("parts", [])

        # Add model response to history
        history.append({"role": "model", "parts": model_parts})

        # Check for function calls
        function_responses = execute_function_calls(model_parts)

        if function_responses:
            # If tools were called, add results to history and loop again
            history.append({"role": "function", "parts": function_responses})
        else:
            # No tools called, this is the final answer
            return "".join(p.get("text", "") for p in model_parts)

    return "Error: Max turns reached."


# --- SERVER ---


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/mission" or self.path == "/":
            length = int(self.headers.get("content-length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw or "{}")
            except Exception:
                self.send_error(400, "Invalid JSON")
                return

            mission = payload.get("mission") or ""
            tier = payload.get("tier") or "FREE"
            model = pick_model(tier)
            logging.info("Mission received (tier=%s, model=%s)", tier, model)

            try:
                answer = run_agent_loop(model, mission)
                resp = {"model": model, "answer": answer}
                data = json.dumps(resp).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                logging.exception("Agent loop failed")
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")


def run_server():
    port = int(os.environ.get("PORT", "8080"))
    server = HTTPServer(("", port), Handler)
    print(f"Server started on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
