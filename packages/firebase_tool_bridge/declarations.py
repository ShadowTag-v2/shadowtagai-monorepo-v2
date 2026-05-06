# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Declarations — auto-generate Firebase AI Logic FunctionDeclarations.

Converts Python function signatures + RegisteredFunction metadata into
Firebase-compatible FunctionDeclaration JSON Schema objects.

Firebase AI Logic requires OpenAPI-compatible schemas:
    {
        "name": "get_weather",
        "description": "Fetch weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }

This module introspects Python type hints and docstrings to produce
conformant schemas without manual JSON authoring.
"""

from __future__ import annotations

import inspect
import logging
from collections.abc import Callable
from typing import Any, Union, get_args, get_origin, get_type_hints

from firebase_tool_bridge.registry import FunctionRegistry, RegisteredFunction

logger = logging.getLogger(__name__)

# Python type → JSON Schema type mapping.
_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _python_type_to_schema(annotation: Any) -> dict[str, Any]:
    """Convert a Python type annotation to a JSON Schema type descriptor.

    Supports:
        - Primitive types (str, int, float, bool)
        - list[T] → {"type": "array", "items": {...}}
        - dict[str, T] → {"type": "object"}
        - Optional[T] → nullable variant of T
        - Literal["a", "b"] → {"type": "string", "enum": ["a", "b"]}
        - Unannotated → {"type": "string"} (safe fallback)

    Args:
        annotation: A Python type annotation.

    Returns:
        JSON Schema type descriptor dict.
    """
    if annotation is inspect.Parameter.empty or annotation is Any:
        return {"type": "string"}

    # Handle Optional[T] (Union[T, None])
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        # Filter out NoneType for Optional[T]
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            return _python_type_to_schema(non_none[0])
        # Multi-type union: fall back to string
        return {"type": "string"}

    # Handle Literal["a", "b", "c"]
    if hasattr(annotation, "__origin__") and str(annotation.__origin__) == "typing.Literal":
        values = list(get_args(annotation))
        if all(isinstance(v, str) for v in values):
            return {"type": "string", "enum": values}
        return {"type": "string", "enum": [str(v) for v in values]}

    # Handle list[T]
    if origin is list:
        if args:
            items_schema = _python_type_to_schema(args[0])
            return {"type": "array", "items": items_schema}
        return {"type": "array"}

    # Handle dict[K, V]
    if origin is dict:
        return {"type": "object"}

    # Direct type match
    if annotation in _TYPE_MAP:
        return {"type": _TYPE_MAP[annotation]}

    # Fallback
    logger.debug("Unmapped type annotation %s, defaulting to string", annotation)
    return {"type": "string"}


def _parse_docstring_params(fn: Callable[..., Any]) -> dict[str, str]:
    """Extract parameter descriptions from a Google-style docstring.

    Parses the 'Args:' section of a Google-style docstring.

    Args:
        fn: The function to extract docstring params from.

    Returns:
        Dict mapping parameter name to its description string.
    """
    doc = inspect.getdoc(fn)
    if not doc:
        return {}

    params: dict[str, str] = {}
    in_args_section = False

    for line in doc.split("\n"):
        stripped = line.strip()

        if stripped.lower().startswith("args:"):
            in_args_section = True
            continue

        if in_args_section:
            # End of Args section
            if stripped and not stripped.startswith("-") and ":" not in stripped[:40]:
                if stripped.lower().startswith(("returns:", "raises:", "yields:", "note:", "example:")):
                    break

            # Parse "param_name: description" or "param_name (type): description"
            if ":" in stripped:
                parts = stripped.lstrip("- ").split(":", 1)
                if len(parts) == 2:
                    param_name = parts[0].strip()
                    # Strip type hints in parens: "city (str)" → "city"
                    if "(" in param_name:
                        param_name = param_name.split("(")[0].strip()
                    description = parts[1].strip()
                    if param_name and description:
                        params[param_name] = description

    return params


def function_to_declaration(
    registered: RegisteredFunction,
    *,
    param_overrides: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Convert a RegisteredFunction to a Firebase FunctionDeclaration.

    Args:
        registered: The registered function to convert.
        param_overrides: Optional per-parameter schema overrides.
            Example: {"unit": {"enum": ["celsius", "fahrenheit"]}}

    Returns:
        Firebase-compatible FunctionDeclaration dict.

    Example:
        >>> decl = function_to_declaration(registered_fn)
        >>> print(decl)
        {
            "name": "get_weather",
            "description": "Fetch weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    """
    param_overrides = param_overrides or {}
    sig = inspect.signature(registered.callable)
    docstring_params = _parse_docstring_params(registered.callable)

    # Resolve PEP 563 stringified annotations to actual types.
    try:
        resolved_hints = get_type_hints(registered.callable)
    except Exception:
        resolved_hints = {}

    properties: dict[str, Any] = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        # Skip self/cls for methods
        if param_name in ("self", "cls"):
            continue

        # Use resolved type hints (handles `from __future__ import annotations`)
        annotation = resolved_hints.get(param_name, param.annotation)

        # Build parameter schema
        schema = _python_type_to_schema(annotation)

        # Add description from docstring
        if param_name in docstring_params:
            schema["description"] = docstring_params[param_name]

        # Apply overrides (enum constraints, custom descriptions, etc.)
        if param_name in param_overrides:
            schema.update(param_overrides[param_name])

        properties[param_name] = schema

        # Track required params (no default value)
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    declaration: dict[str, Any] = {
        "name": registered.name,
        "description": registered.description,
    }

    if properties:
        parameters: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }
        if required:
            parameters["required"] = required
        declaration["parameters"] = parameters

    return declaration


def registry_to_declarations(
    registry: FunctionRegistry,
    *,
    overrides: dict[str, dict[str, dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Convert all registered functions to FunctionDeclaration list.

    This is the primary entry point for generating the tool config
    that gets passed to the Firebase AI model initialization.

    Args:
        registry: The function registry to convert.
        overrides: Optional nested dict mapping function_name →
            param_name → schema overrides.

    Returns:
        List of Firebase-compatible FunctionDeclaration dicts,
        sorted alphabetically by function name.
    """
    overrides = overrides or {}
    declarations: list[dict[str, Any]] = []

    for registered in registry.list_all():
        fn_overrides = overrides.get(registered.name)
        decl = function_to_declaration(
            registered,
            param_overrides=fn_overrides,
        )
        declarations.append(decl)

    logger.info(
        "Generated %d FunctionDeclarations from registry",
        len(declarations),
    )
    return declarations
