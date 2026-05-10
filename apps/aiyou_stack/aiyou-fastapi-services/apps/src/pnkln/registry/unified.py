from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: dict
    function: Callable
    is_kernel_chain: bool = False
    cost_per_call: float = 0.0


class UnifiedRegistry:
    """Central registry for all AI tools, functions, and 'Kernel Chains'.
    Supports auto-generation of Gemini function schemas and monetization integration.
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict = None,
        is_kernel_chain: bool = False,
        cost: float = 0.0,
    ):
        """Decorator to register a function as a tool."""
        if parameters is None:
            parameters = {}

        def decorator(func: Callable):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters,
                function=func,
                is_kernel_chain=is_kernel_chain,
                cost_per_call=cost,
            )
            return func

        return decorator

    def get_tool(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def generate_gemini_schema(self) -> list[dict]:
        """Converts registered tools into Gemini Function Declaration format."""
        schemas = []
        for tool in self._tools.values():
            schemas.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            )
        return schemas

    def execute(self, tool_name: str, **kwargs) -> Any:
        """Executes a tool by name, handling any necessary wraps."""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")

        # Here we could inject monetization tracking hooks
        # e.g., monetization.track_request(api_key, tool_name)

        return tool.function(**kwargs)


# Global Registry Instance
registry = UnifiedRegistry()


# Example Usage / Standard Tools
@registry.register(
    name="get_current_price",
    description="Get the current price of a stock",
    parameters={"type": "object", "properties": {"symbol": {"type": "string"}}},
    cost=0.01,
)
def get_current_price(symbol: str):
    # Dummy implementation
    return {"symbol": symbol, "price": 150.00}


@registry.register(
    name="kernel_chain_analyze",
    description="Run a deep kernel analysis chain",
    is_kernel_chain=True,
    cost=0.50,
)
def kernel_chain_analyze(data: str):
    return f"Analyzed: {data}"
