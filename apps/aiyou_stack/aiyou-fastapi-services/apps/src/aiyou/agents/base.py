import ast
import io
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

from src.shadowtag_v4.tools.registry import registry


class SandboxedExecutor:
    """Restricted Python executor for orchestration scripts.
    Provides a safe subset of Python for tool orchestration.
    """

    # Allowed built-in functions (safe subset)
    ALLOWED_BUILTINS = {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "filter",
        "float",
        "frozenset",
        "int",
        "isinstance",
        "len",
        "list",
        "map",
        "max",
        "min",
        "print",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
        "True",
        "False",
        "None",
    }

    # Forbidden AST nodes (dangerous operations)
    FORBIDDEN_NODES = {
        ast.Import,
        ast.ImportFrom,  # No imports
        ast.AsyncFunctionDef,
        ast.AsyncFor,
        ast.AsyncWith,
        ast.Await,  # No async
        ast.Global,
        ast.Nonlocal,  # No scope manipulation
    }

    # Forbidden attribute access
    FORBIDDEN_ATTRS = {
        "__class__",
        "__bases__",
        "__subclasses__",
        "__mro__",
        "__code__",
        "__globals__",
        "__builtins__",
        "__import__",
        "__getattribute__",
        "__setattr__",
        "__delattr__",
    }

    def __init__(self, tool_executor: callable):
        """Initialize sandbox with a tool executor function.

        Args:
            tool_executor: Function that takes (tool_name, **kwargs) and returns result

        """
        self.tool_executor = tool_executor
        self.execution_log = []

    def _validate_ast(self, tree: ast.AST) -> None:
        """Validate AST for forbidden patterns."""
        for node in ast.walk(tree):
            # Check forbidden node types
            if type(node) in self.FORBIDDEN_NODES:
                raise SecurityError(f"Forbidden operation: {type(node).__name__}")

            # Check forbidden attribute access
            if isinstance(node, ast.Attribute) and node.attr in self.FORBIDDEN_ATTRS:
                raise SecurityError(f"Forbidden attribute access: {node.attr}")

            # Check forbidden function calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in (
                    "eval",
                    "exec",
                    "compile",
                    "open",
                    "__import__",
                ):
                    raise SecurityError(f"Forbidden function: {node.func.id}")

    def _create_safe_globals(self) -> dict[str, Any]:
        """Create restricted globals for script execution."""
        import builtins

        safe_builtins = {}
        for name in self.ALLOWED_BUILTINS:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)

        # Add None, True, False explicitly
        safe_builtins["None"] = None
        safe_builtins["True"] = True
        safe_builtins["False"] = False

        return {
            "__builtins__": safe_builtins,
            "call_tool": self._safe_tool_call,
            "results": {},  # Store intermediate results
        }

    def _safe_tool_call(self, tool_name: str, **kwargs) -> Any:
        """Wrapper for tool calls that logs execution."""
        self.execution_log.append(
            {
                "tool": tool_name,
                "inputs": kwargs,
            },
        )
        result = self.tool_executor(tool_name, **kwargs)
        self.execution_log[-1]["output"] = result
        return result

    def execute(self, script: str, timeout: float = 30.0) -> dict[str, Any]:
        """Execute a sandboxed Python script.

        Args:
            script: Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dict with 'output', 'results', 'log', and 'error' keys

        """
        import signal

        self.execution_log = []

        # Parse and validate
        try:
            tree = ast.parse(script)
            self._validate_ast(tree)
        except SyntaxError as e:
            return {
                "output": "",
                "results": {},
                "log": [],
                "error": f"Syntax error: {e}",
            }
        except SecurityError as e:
            return {"output": "", "results": {}, "log": [], "error": str(e)}

        # Prepare execution environment
        safe_globals = self._create_safe_globals()
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Timeout handler
        def timeout_handler(signum, frame):
            raise TimeoutError("Script execution timed out")

        # Execute with timeout and output capture
        try:
            # Set timeout (Unix only)
            if hasattr(signal, "SIGALRM"):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(compile(tree, "<orchestration>", "exec"), safe_globals)

            return {
                "output": stdout_capture.getvalue(),
                "results": safe_globals.get("results", {}),
                "log": self.execution_log,
                "error": None,
            }
        except TimeoutError as e:
            return {
                "output": stdout_capture.getvalue(),
                "results": {},
                "log": self.execution_log,
                "error": str(e),
            }
        except Exception as e:
            return {
                "output": stdout_capture.getvalue(),
                "results": {},
                "log": self.execution_log,
                "error": f"{type(e).__name__}: {e}",
            }
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)


class SecurityError(Exception):
    """Raised when sandbox detects forbidden operations."""


class AntigravityAgent:
    """Base agent class supporting Advanced Tool Use patterns."""

    def __init__(self, name: str, model: str = "claude-3-5-sonnet-20241022"):
        self.name = name
        self.model = model
        # Pattern 1: Load ONLY the search tool initially
        self.tools = [self._get_search_tool_def()]

    def _get_search_tool_def(self):
        return {
            "name": "search_tools",
            "description": "Search for available tools to perform tasks. Use this when you don't have a specific tool loaded.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for tool capabilities",
                    },
                },
                "required": ["query"],
            },
        }

    def execute_tool_search(self, query: str):
        """Execute the search and load found tools into context."""
        found_tools = registry.search(query)
        # Dynamically add found tools to the agent's active toolset
        for tool in found_tools:
            if tool not in self.tools:
                self.tools.append(tool)
        return f"Found and loaded {len(found_tools)} tools: {[t['name'] for t in found_tools]}"

    def _execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name. Override this for actual tool implementations."""
        tool_def = registry.get_tool(tool_name)
        if not tool_def:
            return {"error": f"Tool '{tool_name}' not found"}

        # Mock execution - return example output if available
        examples = tool_def.get("examples", [])
        if examples:
            return examples[0].get("output", {"status": "executed", "tool": tool_name})
        return {"status": "executed", "tool": tool_name, "inputs": kwargs}

    def execute_python_orchestration(self, script: str, timeout: float = 30.0) -> dict[str, Any]:
        """Executes a sandboxed Python script that orchestrates multiple tool calls.
        This keeps intermediate data out of the LLM context.

        The script has access to:
        - call_tool(name, **kwargs): Execute a registered tool
        - results: Dict to store intermediate results
        - Safe built-ins: list, dict, str, int, print, range, etc.

        Security features:
        - No imports allowed
        - No file/network access
        - No dangerous built-ins (eval, exec, open, etc.)
        - Execution timeout (default 30s)
        - AST validation before execution

        Example script:
            # Fetch orders and check budget
            orders = call_tool("search_customer_orders", status="shipped")
            budget = call_tool("check_budget_compliance", department="engineering")

            # Process locally (not in LLM context)
            total = sum(o['total'] for o in orders if isinstance(orders, list))
            results['summary'] = {
                'order_count': len(orders) if isinstance(orders, list) else 0,
                'total_value': total,
                'budget_ok': budget.get('compliant', False)
            }

        Returns:
            Dict with keys:
            - output: Captured stdout from the script
            - results: The 'results' dict from script execution
            - log: List of tool calls made [{tool, inputs, output}, ...]
            - error: Error message if execution failed, else None

        """
        sandbox = SandboxedExecutor(tool_executor=self._execute_tool)
        result = sandbox.execute(script, timeout=timeout)

        # Summarize for returning to LLM (keep it concise)
        if result["error"]:
            return {
                "status": "error",
                "error": result["error"],
                "partial_log": result["log"][:3],  # First 3 calls for debugging
            }

        return {
            "status": "success",
            "tools_called": len(result["log"]),
            "tool_names": [entry["tool"] for entry in result["log"]],
            "results": result["results"],
            "output": result["output"][:1000] if result["output"] else None,  # Truncate long output
        }
