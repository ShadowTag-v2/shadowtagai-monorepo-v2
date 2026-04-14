#!/usr/bin/env python3
"""ACP (Agent Client Protocol) Server
JSON-RPC server for IDE integration (JetBrains, Zed, VSCode).
"""

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from src.shadowtag_v4.cursor_features import CursorFeatures
from src.shadowtag_v4.services.gemini_core import GeminiAntigravity


@dataclass
class ACPRequest:
    """ACP JSON-RPC request."""

    jsonrpc: str = "2.0"
    id: int = 0
    method: str = ""
    params: dict[str, Any] = None


@dataclass
class ACPResponse:
    """ACP JSON-RPC response."""

    jsonrpc: str = "2.0"
    id: int = 0
    result: Any = None
    error: dict[str, Any] | None = None


class ACPServer:
    """Agent Client Protocol server.
    Provides cursor-style code intelligence backed by Gemini.
    """

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.gemini = GeminiAntigravity()
        self.cursor = CursorFeatures(workspace_root=self.workspace_root)

        # Method handlers
        self.methods = {
            "initialize": self.handle_initialize,
            "complete": self.handle_complete,
            "generate": self.handle_generate,
            "explain": self.handle_explain,
            "refactor": self.handle_refactor,
            "search": self.handle_search,
            "findSymbol": self.handle_find_symbol,
            "getContext": self.handle_get_context,
            "chat": self.handle_chat,
        }

    async def handle_request(self, request_data: str) -> str:
        """Handle incoming JSON-RPC request.

        Args:
            request_data: JSON string

        Returns:
            JSON response string

        """
        try:
            req = json.loads(request_data)
            method = req.get("method", "")
            params = req.get("params", {})
            req_id = req.get("id", 0)

            if method in self.methods:
                result = await self.methods[method](params)
                response = ACPResponse(id=req_id, result=result)
            else:
                response = ACPResponse(
                    id=req_id, error={"code": -32601, "message": f"Method not found: {method}"},
                )

            return json.dumps(asdict(response))

        except json.JSONDecodeError as e:
            return json.dumps(
                asdict(ACPResponse(error={"code": -32700, "message": f"Parse error: {e}"})),
            )
        except Exception as e:
            return json.dumps(
                asdict(ACPResponse(error={"code": -32603, "message": f"Internal error: {e}"})),
            )

    async def handle_initialize(self, params: dict) -> dict:
        """Initialize connection with capabilities."""
        return {
            "capabilities": {
                "completionProvider": True,
                "generateProvider": True,
                "explainProvider": True,
                "refactorProvider": True,
                "searchProvider": True,
            },
            "serverInfo": {"name": "ShadowTag-v4 ACP Server", "version": "1.0.0"},
        }

    async def handle_complete(self, params: dict) -> dict:
        """Code completion at cursor.

        Params:
            file_path: Current file
            line: Cursor line
            column: Cursor column
            prefix: Text before cursor
        """
        file_path = params.get("file_path", "")
        line = params.get("line", 0)
        prefix = params.get("prefix", "")

        # Generate context
        prompt = self.cursor.generate_prompt_context(
            file_path, line, f"Complete the code after: {prefix}",
        )

        # Get completion from Gemini
        result = self.gemini.generate_text(prompt)

        return {"completions": [{"text": result, "kind": "snippet"}]}

    async def handle_generate(self, params: dict) -> dict:
        """Generate code based on task description.

        Params:
            file_path: Current file
            line: Cursor line
            task: What to generate
        """
        file_path = params.get("file_path", "")
        line = params.get("line", 0)
        task = params.get("task", "")

        prompt = self.cursor.generate_prompt_context(file_path, line, task)
        result = self.gemini.generate_text(prompt)

        return {"code": result}

    async def handle_explain(self, params: dict) -> dict:
        """Explain selected code.

        Params:
            code: Code to explain
            file_path: Optional file context
        """
        code = params.get("code", "")
        file_path = params.get("file_path", "")

        prompt = f"""Explain this code concisely:

```python
{code}
```

File: {file_path}

Provide:
1. What it does (1-2 sentences)
2. Key concepts used
3. Potential issues or improvements
"""
        result = self.gemini.generate_text(prompt)

        return {"explanation": result}

    async def handle_refactor(self, params: dict) -> dict:
        """Refactor code with specific instruction.

        Params:
            code: Code to refactor
            instruction: How to refactor
        """
        code = params.get("code", "")
        instruction = params.get("instruction", "improve readability")

        prompt = f"""Refactor this code: {instruction}

```python
{code}
```

Return only the refactored code, no explanations.
"""
        result = self.gemini.generate_text(prompt)

        return {"refactored": result}

    async def handle_search(self, params: dict) -> dict:
        """Search codebase or GitHub.

        Params:
            query: Search query
            scope: "local" or "github"
            repo: GitHub repo (for github scope)
        """
        query = params.get("query", "")
        scope = params.get("scope", "local")
        repo = params.get("repo")

        if scope == "github":
            results = self.cursor.github_search(query, repo)
        else:
            results = self.cursor.search_code(query)

        return {"results": results}

    async def handle_find_symbol(self, params: dict) -> dict:
        """Find symbol definition.

        Params:
            symbol: Symbol name
        """
        symbol = params.get("symbol", "")
        symbols = self.cursor.find_symbol(symbol)

        return {
            "symbols": [
                {
                    "name": s.name,
                    "kind": s.kind,
                    "file": s.file_path,
                    "line": s.line,
                    "signature": s.signature,
                }
                for s in symbols
            ],
        }

    async def handle_get_context(self, params: dict) -> dict:
        """Get code context for current position.

        Params:
            file_path: Current file
            line: Cursor line
        """
        file_path = params.get("file_path", "")
        line = params.get("line", 0)

        context = self.cursor.get_context(file_path, line)
        related = self.cursor.get_related_files(file_path)

        return {
            "symbols": [
                asdict(s)
                if hasattr(s, "__dict__")
                else {"name": s.name, "kind": s.kind, "file": s.file_path, "line": s.line}
                for s in context.symbols
            ],
            "imports": context.imports,
            "related_files": related,
        }

    async def handle_chat(self, params: dict) -> dict:
        """Chat with context.

        Params:
            message: User message
            file_path: Optional file context
            line: Optional cursor line
        """
        message = params.get("message", "")
        file_path = params.get("file_path", "")
        line = params.get("line", 0)

        if file_path:
            context = self.cursor.get_context(file_path, line)
            prompt = f"""Context from {file_path}:
```python
{context.content[:2000]}
```

User question: {message}
"""
        else:
            prompt = message

        result = self.gemini.generate_text(prompt)

        return {"response": result}

    async def serve_stdio(self):
        """Serve over stdin/stdout (for IDE integration)."""
        import sys

        print("///▞ ACP Server ready (stdio)", file=sys.stderr)

        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                response = await self.handle_request(line.strip())
                print(response, flush=True)

            except Exception as e:
                error_response = ACPResponse(error={"code": -32603, "message": str(e)})
                print(json.dumps(asdict(error_response)), flush=True)

    async def serve_tcp(self, host: str = "127.0.0.1", port: int = 9999):
        """Serve over TCP socket."""

        async def handle_client(reader, writer):
            addr = writer.get_extra_info("peername")
            print(f"///▞ ACP Client connected: {addr}")

            while True:
                try:
                    data = await reader.readline()
                    if not data:
                        break

                    response = await self.handle_request(data.decode().strip())
                    writer.write((response + "\n").encode())
                    await writer.drain()

                except Exception as e:
                    error = ACPResponse(error={"code": -32603, "message": str(e)})
                    writer.write((json.dumps(asdict(error)) + "\n").encode())
                    await writer.drain()

            writer.close()
            print(f"///▞ ACP Client disconnected: {addr}")

        server = await asyncio.start_server(handle_client, host, port)
        print(f"///▞ ACP Server listening on {host}:{port}")

        async with server:
            await server.serve_forever()


async def main():
    """Run ACP server."""
    import argparse

    parser = argparse.ArgumentParser(description="ShadowTag-v4 ACP Server")
    parser.add_argument("--mode", choices=["stdio", "tcp"], default="tcp")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--workspace", type=str, default=None)
    args = parser.parse_args()

    server = ACPServer(workspace_root=args.workspace)

    if args.mode == "stdio":
        await server.serve_stdio()
    else:
        await server.serve_tcp(port=args.port)


if __name__ == "__main__":
    asyncio.run(main())
