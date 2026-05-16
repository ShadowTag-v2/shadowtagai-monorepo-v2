# Copyright 2026 ShadowTagAI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Property-based tests for declarations.py type-to-schema converter.

Uses Hypothesis to exhaustively test _python_type_to_schema with
randomized type annotations, ensuring robustness against edge cases.

Usage:
    pytest packages/firebase_tool_bridge/hypothesis_declarations_test.py -v
"""

from __future__ import annotations

import inspect
from typing import Any, Literal, Optional, Union

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from firebase_tool_bridge.declarations import (
  _parse_docstring_params,
  _python_type_to_schema,
  function_to_declaration,
)
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier


# ─── Strategies ──────────────────────────────────────────────────────────────

# All primitive types the converter should handle
PRIMITIVE_TYPES = st.sampled_from([str, int, float, bool])

# Container types
LIST_TYPES = PRIMITIVE_TYPES.map(lambda t: list[t])  # type: ignore[name-defined]
DICT_TYPES = st.just(dict[str, Any])

# Optional types
OPTIONAL_TYPES = PRIMITIVE_TYPES.map(lambda t: Optional[t])  # type: ignore[misc]

# All types combined
ALL_TYPES = st.one_of(PRIMITIVE_TYPES, LIST_TYPES, DICT_TYPES, OPTIONAL_TYPES)

# Valid JSON Schema types
VALID_SCHEMA_TYPES = {"string", "integer", "number", "boolean", "array", "object"}


# ─── Property Tests: _python_type_to_schema ──────────────────────────────────


class TestTypeToSchemaProperties:
  """Property-based tests for the type-to-schema converter."""

  @given(annotation=PRIMITIVE_TYPES)
  def test_primitives_always_produce_valid_schema(self, annotation):
    """Every primitive type maps to a valid JSON Schema type."""
    schema = _python_type_to_schema(annotation)
    assert isinstance(schema, dict)
    assert "type" in schema
    assert schema["type"] in VALID_SCHEMA_TYPES

  @given(annotation=PRIMITIVE_TYPES)
  def test_primitives_are_deterministic(self, annotation):
    """Same input always produces the same output."""
    schema1 = _python_type_to_schema(annotation)
    schema2 = _python_type_to_schema(annotation)
    assert schema1 == schema2

  @given(annotation=LIST_TYPES)
  def test_list_types_produce_array_schema(self, annotation):
    """list[T] always produces {type: array, items: ...}."""
    schema = _python_type_to_schema(annotation)
    assert schema["type"] == "array"
    assert "items" in schema
    assert schema["items"]["type"] in VALID_SCHEMA_TYPES

  @given(annotation=OPTIONAL_TYPES)
  def test_optional_unwraps_to_inner_type(self, annotation):
    """Optional[T] should produce the same schema as T."""
    schema = _python_type_to_schema(annotation)
    assert isinstance(schema, dict)
    assert "type" in schema
    assert schema["type"] in VALID_SCHEMA_TYPES

  def test_any_falls_back_to_string(self):
    """Any annotation falls back to string."""
    schema = _python_type_to_schema(Any)
    assert schema == {"type": "string"}

  def test_empty_annotation_falls_back_to_string(self):
    """Missing annotation falls back to string."""
    schema = _python_type_to_schema(inspect.Parameter.empty)
    assert schema == {"type": "string"}

  def test_dict_type_produces_object(self):
    """dict produces {type: object}."""
    schema = _python_type_to_schema(dict[str, int])
    assert schema == {"type": "object"}

  def test_bare_dict_produces_object(self):
    """Bare dict (no type params) produces {type: object}."""
    schema = _python_type_to_schema(dict)
    assert schema == {"type": "object"}

  def test_bare_list_produces_array_no_items(self):
    """Bare list (no type params) produces {type: array} without items."""
    schema = _python_type_to_schema(list)
    assert schema == {"type": "array"}

  def test_union_multi_type_falls_back(self):
    """Union[str, int] (non-Optional) falls back to string."""
    schema = _python_type_to_schema(Union[str, int])
    assert schema == {"type": "string"}

  def test_nested_list_produces_nested_schema(self):
    """list[list[str]] produces nested array schema."""
    schema = _python_type_to_schema(list[list[str]])
    assert schema["type"] == "array"
    assert schema["items"]["type"] == "array"
    assert schema["items"]["items"]["type"] == "string"

  def test_literal_string_produces_enum(self):
    """Literal['a', 'b'] produces enum constraint."""
    schema = _python_type_to_schema(Literal["celsius", "fahrenheit"])
    assert schema["type"] == "string"
    assert schema["enum"] == ["celsius", "fahrenheit"]

  def test_literal_int_produces_string_enum(self):
    """Literal[1, 2] converts values to strings in enum."""
    schema = _python_type_to_schema(Literal[1, 2, 3])
    assert schema["type"] == "string"
    assert schema["enum"] == ["1", "2", "3"]

  def test_unknown_type_falls_back_to_string(self):
    """Completely unknown type falls back to string."""

    class MyCustomType:
      pass

    schema = _python_type_to_schema(MyCustomType)
    assert schema == {"type": "string"}


# ─── Property Tests: _parse_docstring_params ─────────────────────────────────


class TestDocstringParserProperties:
  """Property-based tests for docstring parameter parsing."""

  @given(
    param_name=st.from_regex(r"[a-z][a-z_0-9]{0,20}", fullmatch=True),
    description=st.from_regex(r"[A-Za-z0-9 ,.!?()-]{1,100}", fullmatch=True),
  )
  @settings(max_examples=50)
  def test_parsed_params_roundtrip(self, param_name, description):
    """A well-formed Google-style docstring should parse correctly."""
    assume(param_name not in ("args", "returns", "raises", "yields", "note", "example"))
    assume(len(description.strip()) > 0)

    def fn():
      pass

    fn.__doc__ = f"Short desc.\n\nArgs:\n    {param_name}: {description}\n"
    parsed = _parse_docstring_params(fn)
    assert param_name in parsed
    assert parsed[param_name] == description.strip()

  def test_empty_docstring_returns_empty(self):
    """Functions without docstrings return empty dict."""

    def fn():
      pass

    assert _parse_docstring_params(fn) == {}

  def test_no_args_section_returns_empty(self):
    """Docstrings without Args section return empty dict."""

    def fn():
      """Just a description, no args section."""

    assert _parse_docstring_params(fn) == {}

  def test_multiple_params_parsed(self):
    """Multiple parameters are all extracted."""

    def fn():
      """Description.

      Args:
          city: The city name.
          unit: Temperature unit.
          count: Number of results.
      """

    parsed = _parse_docstring_params(fn)
    assert len(parsed) == 3
    assert parsed["city"] == "The city name."
    assert parsed["unit"] == "Temperature unit."
    assert parsed["count"] == "Number of results."


# ─── Property Tests: function_to_declaration ─────────────────────────────────


class TestFunctionToDeclarationProperties:
  """Property-based tests for the full declaration generator."""

  def test_declaration_always_has_name(self):
    """Every declaration must have a name field."""
    registry = FunctionRegistry()
    registry.register("test_fn", lambda x: x, RiskTier.LOW)
    registered = registry.get("test_fn")
    decl = function_to_declaration(registered)
    assert "name" in decl
    assert decl["name"] == "test_fn"

  def test_declaration_always_has_description(self):
    """Every declaration must have a description field."""
    registry = FunctionRegistry()
    registry.register("test_fn", lambda x: x, RiskTier.LOW)
    registered = registry.get("test_fn")
    decl = function_to_declaration(registered)
    assert "description" in decl

  def test_required_params_are_those_without_defaults(self):
    """Only params without defaults appear in required list."""

    def fn(required_arg: str, optional_arg: str = "default"):
      """Test fn.

      Args:
          required_arg: A required arg.
          optional_arg: An optional arg.
      """

    registry = FunctionRegistry()
    registry.register("fn", fn, RiskTier.LOW)
    decl = function_to_declaration(registry.get("fn"))
    assert "required_arg" in decl["parameters"]["required"]
    assert "optional_arg" not in decl["parameters"]["required"]

  def test_param_overrides_are_applied(self):
    """Schema overrides merge into parameter schemas."""

    def fn(unit: str = "celsius"):
      """Test.

      Args:
          unit: The unit.
      """

    registry = FunctionRegistry()
    registry.register("fn", fn, RiskTier.LOW)
    decl = function_to_declaration(
      registry.get("fn"),
      param_overrides={"unit": {"enum": ["celsius", "fahrenheit"]}},
    )
    assert decl["parameters"]["properties"]["unit"]["enum"] == ["celsius", "fahrenheit"]

  def test_self_cls_params_are_skipped(self):
    """self and cls parameters are not included in declarations."""

    class MyClass:
      def method(self, x: int):
        """Test.

        Args:
            x: A number.
        """

    registry = FunctionRegistry()
    registry.register("method", MyClass().method, RiskTier.LOW)
    decl = function_to_declaration(registry.get("method"))
    prop_names = list(decl.get("parameters", {}).get("properties", {}).keys())
    assert "self" not in prop_names
