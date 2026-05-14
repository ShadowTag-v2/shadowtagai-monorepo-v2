# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Function Registry for managing tool functions.

Provides a centralized registry for all tool functions that can be called
by the Gemini model.
"""

from typing import Dict, Any, List
from collections.abc import Callable
from .gemini_function_calling import FunctionTool


class FunctionRegistry:
    """
    Centralized registry for managing function tools.

    Example:
        ```python
        registry = FunctionRegistry()

        @registry.register(
            description="Research a topic",
            parameters={"query": {"type": "string"}}
        )
        def research(query: str) -> dict:
            return {"findings": f"Results for {query}"}

        tools = registry.get_all_tools()
        ```
    """

    def __init__(self):
        self.functions: dict[str, Callable] = {}
        self.tools: list[FunctionTool] = []

    def register(self, description: str, parameters: dict[str, Any], name: str = None) -> Callable:
        """
        Decorator to register a function as a tool.

        Args:
            description: Human-readable description of what the function does
            parameters: Parameter schema (e.g., {"query": {"type": "string"}})
            name: Optional custom name (defaults to function name)

        Returns:
            Decorator function
        """

        def decorator(func: Callable) -> Callable:
            func_name = name or func.__name__

            # Create FunctionTool
            tool = FunctionTool(name=func_name, description=description, function=func, parameters=parameters)

            # Register
            self.functions[func_name] = func
            self.tools.append(tool)

            return func

        return decorator

    def get_function(self, name: str) -> Callable:
        """Get a registered function by name."""
        if name not in self.functions:
            raise KeyError(f"Function '{name}' not registered")
        return self.functions[name]

    def get_tool(self, name: str) -> FunctionTool:
        """Get a registered tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        raise KeyError(f"Tool '{name}' not registered")

    def get_all_tools(self) -> list[FunctionTool]:
        """Get all registered tools."""
        return self.tools.copy()

    def get_all_functions(self) -> dict[str, Callable]:
        """Get all registered functions."""
        return self.functions.copy()

    def clear(self):
        """Clear all registered functions and tools."""
        self.functions.clear()
        self.tools.clear()
