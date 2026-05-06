# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for declarations.py — FunctionDeclaration schema generation."""

from __future__ import annotations


from firebase_tool_bridge.declarations import (
    function_to_declaration,
    registry_to_declarations,
    _python_type_to_schema,
    _parse_docstring_params,
)
from firebase_tool_bridge.registry import FunctionRegistry, RegisteredFunction, RiskTier


# ── Fixture functions ──────────────────────────────────────────


def get_weather(city: str, unit: str = "celsius") -> dict:
    """Fetch current weather for a city.

    Args:
        city: The city name to look up.
        unit: Temperature unit (celsius or fahrenheit).

    Returns:
        Weather data dict.
    """
    return {"city": city, "temp": 22, "unit": unit}


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        Sum of a and b.
    """
    return a + b


def no_params() -> str:
    """A function with no parameters."""
    return "hello"


def untyped_params(name, count):
    """A function with untyped parameters.

    Args:
        name: The name to greet.
        count: How many times.
    """
    return name * count


def complex_types(
    tags: list[str],
    metadata: dict[str, int],
    active: bool = True,
    score: float = 0.0,
) -> dict:
    """Function with complex type hints.

    Args:
        tags: List of string tags.
        metadata: Key-value metadata pairs.
        active: Whether the item is active.
        score: Numeric score.

    Returns:
        Processed result.
    """
    return {"tags": tags, "metadata": metadata, "active": active, "score": score}


# ── Type mapping tests ─────────────────────────────────────────


class TestPythonTypeToSchema:
    """Tests for _python_type_to_schema()."""

    def test_str_type(self) -> None:
        assert _python_type_to_schema(str) == {"type": "string"}

    def test_int_type(self) -> None:
        assert _python_type_to_schema(int) == {"type": "integer"}

    def test_float_type(self) -> None:
        assert _python_type_to_schema(float) == {"type": "number"}

    def test_bool_type(self) -> None:
        assert _python_type_to_schema(bool) == {"type": "boolean"}

    def test_list_type(self) -> None:
        assert _python_type_to_schema(list) == {"type": "array"}

    def test_dict_type(self) -> None:
        assert _python_type_to_schema(dict) == {"type": "object"}

    def test_list_of_str(self) -> None:
        result = _python_type_to_schema(list[str])
        assert result == {"type": "array", "items": {"type": "string"}}

    def test_optional_str(self) -> None:
        result = _python_type_to_schema(str | None)
        assert result == {"type": "string"}

    def test_unannotated(self) -> None:
        import inspect

        result = _python_type_to_schema(inspect.Parameter.empty)
        assert result == {"type": "string"}


# ── Docstring parsing tests ────────────────────────────────────


class TestParseDocstringParams:
    """Tests for _parse_docstring_params()."""

    def test_google_style_docstring(self) -> None:
        params = _parse_docstring_params(get_weather)
        assert "city" in params
        assert "unit" in params
        assert "city name" in params["city"].lower()

    def test_no_docstring(self) -> None:
        fn = lambda x: x  # noqa: E731
        params = _parse_docstring_params(fn)
        assert params == {}

    def test_multiple_params(self) -> None:
        params = _parse_docstring_params(calculate_sum)
        assert "a" in params
        assert "b" in params


# ── Declaration generation tests ───────────────────────────────


class TestFunctionToDeclaration:
    """Tests for function_to_declaration()."""

    def _make_registered(self, fn, name: str = "test_fn") -> RegisteredFunction:
        return RegisteredFunction(
            name=name,
            callable=fn,
            risk_tier=RiskTier.LOW,
            description=fn.__doc__.split("\n")[0] if fn.__doc__ else f"Function: {name}",
        )

    def test_basic_declaration(self) -> None:
        reg = self._make_registered(get_weather, "get_weather")
        decl = function_to_declaration(reg)

        assert decl["name"] == "get_weather"
        assert "description" in decl
        assert "parameters" in decl
        assert decl["parameters"]["type"] == "object"
        assert "city" in decl["parameters"]["properties"]
        assert "unit" in decl["parameters"]["properties"]

    def test_required_params(self) -> None:
        reg = self._make_registered(get_weather, "get_weather")
        decl = function_to_declaration(reg)

        # city is required (no default), unit is optional
        assert "city" in decl["parameters"]["required"]
        assert "unit" not in decl["parameters"]["required"]

    def test_all_required(self) -> None:
        reg = self._make_registered(calculate_sum, "calculate_sum")
        decl = function_to_declaration(reg)

        assert "a" in decl["parameters"]["required"]
        assert "b" in decl["parameters"]["required"]

    def test_no_params_function(self) -> None:
        reg = self._make_registered(no_params, "no_params")
        decl = function_to_declaration(reg)

        assert decl["name"] == "no_params"
        # No parameters key or empty properties
        if "parameters" in decl:
            assert decl["parameters"]["properties"] == {}

    def test_untyped_defaults_to_string(self) -> None:
        reg = self._make_registered(untyped_params, "untyped_params")
        decl = function_to_declaration(reg)

        props = decl["parameters"]["properties"]
        assert props["name"]["type"] == "string"
        assert props["count"]["type"] == "string"

    def test_complex_types(self) -> None:
        reg = self._make_registered(complex_types, "complex_types")
        decl = function_to_declaration(reg)

        props = decl["parameters"]["properties"]
        assert props["tags"]["type"] == "array"
        assert props["metadata"]["type"] == "object"
        assert props["active"]["type"] == "boolean"
        assert props["score"]["type"] == "number"

    def test_docstring_descriptions_included(self) -> None:
        reg = self._make_registered(get_weather, "get_weather")
        decl = function_to_declaration(reg)

        city_schema = decl["parameters"]["properties"]["city"]
        assert "description" in city_schema

    def test_param_overrides(self) -> None:
        reg = self._make_registered(get_weather, "get_weather")
        decl = function_to_declaration(
            reg,
            param_overrides={
                "unit": {"enum": ["celsius", "fahrenheit"]},
            },
        )

        unit_schema = decl["parameters"]["properties"]["unit"]
        assert unit_schema["enum"] == ["celsius", "fahrenheit"]


# ── Registry-to-declarations tests ─────────────────────────────


class TestRegistryToDeclarations:
    """Tests for registry_to_declarations()."""

    def test_empty_registry(self) -> None:
        registry = FunctionRegistry()
        decls = registry_to_declarations(registry)
        assert decls == []

    def test_multiple_functions(self) -> None:
        registry = FunctionRegistry()
        registry.register("get_weather", get_weather, RiskTier.LOW)
        registry.register("calculate_sum", calculate_sum, RiskTier.LOW)

        decls = registry_to_declarations(registry)
        assert len(decls) == 2

        names = [d["name"] for d in decls]
        assert "calculate_sum" in names
        assert "get_weather" in names

    def test_sorted_by_name(self) -> None:
        registry = FunctionRegistry()
        registry.register("z_func", no_params, RiskTier.LOW)
        registry.register("a_func", no_params, RiskTier.LOW)

        decls = registry_to_declarations(registry)
        assert decls[0]["name"] == "a_func"
        assert decls[1]["name"] == "z_func"

    def test_with_overrides(self) -> None:
        registry = FunctionRegistry()
        registry.register("get_weather", get_weather, RiskTier.LOW)

        decls = registry_to_declarations(
            registry,
            overrides={
                "get_weather": {
                    "unit": {"enum": ["celsius", "fahrenheit"]},
                },
            },
        )

        assert len(decls) == 1
        unit_schema = decls[0]["parameters"]["properties"]["unit"]
        assert "enum" in unit_schema
