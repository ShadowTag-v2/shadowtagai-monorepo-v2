# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for A2UIAdapter — Declarative UI rendering via google/A2UI protocol."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from shadowtag_os.a2ui_adapter.adapter import (
    A2UIAdapter,
    A2UIComponent,
    A2UIResponse,
    ComponentType,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_spec_dir(tmp_path: Path) -> Path:
    """Create a temporary spec directory with component JSON files."""
    spec = tmp_path / "spec"
    spec.mkdir()

    # Write a few valid spec files
    for comp_type in ("text", "button", "custom_widget"):
        (spec / f"{comp_type}.json").write_text(json.dumps({"type": comp_type}))

    # Write an invalid JSON file (should be skipped silently)
    (spec / "broken.json").write_text("{not valid json")

    return tmp_path


@pytest.fixture
def adapter_no_spec(tmp_path: Path) -> A2UIAdapter:
    """Adapter initialized without a spec directory (fallback catalog)."""
    return A2UIAdapter(a2ui_root=tmp_path / "nonexistent")


@pytest.fixture
def adapter_with_spec(tmp_spec_dir: Path) -> A2UIAdapter:
    """Adapter initialized with a real spec directory."""
    return A2UIAdapter(a2ui_root=tmp_spec_dir)


# ---------------------------------------------------------------------------
# ComponentType enum
# ---------------------------------------------------------------------------


class TestComponentType:
    """Validate the ComponentType enum values."""

    def test_all_enum_values(self) -> None:
        """All 10 built-in component types exist."""
        expected = {
            "text",
            "button",
            "input",
            "card",
            "list",
            "image",
            "table",
            "chart",
            "container",
            "form",
        }
        assert {t.value for t in ComponentType} == expected

    def test_value_roundtrip(self) -> None:
        """Enum round-trips through .value and back."""
        for ct in ComponentType:
            assert ComponentType(ct.value) is ct


# ---------------------------------------------------------------------------
# A2UIComponent dataclass
# ---------------------------------------------------------------------------


class TestA2UIComponent:
    """Validate the A2UIComponent dataclass defaults."""

    def test_defaults(self) -> None:
        """Default children and properties are empty."""
        comp = A2UIComponent(id="c1", type=ComponentType.TEXT)
        assert comp.properties == {}
        assert comp.children == []
        assert comp.parent_id is None

    def test_with_children(self) -> None:
        """Children are stored as ID strings, not nested objects."""
        comp = A2UIComponent(
            id="root",
            type=ComponentType.CONTAINER,
            children=["child_1", "child_2"],
        )
        assert len(comp.children) == 2
        assert all(isinstance(c, str) for c in comp.children)


# ---------------------------------------------------------------------------
# A2UIResponse dataclass
# ---------------------------------------------------------------------------


class TestA2UIResponse:
    """Validate the A2UIResponse serialization."""

    def test_to_dict_structure(self) -> None:
        """to_dict() produces the correct A2UI protocol format."""
        comp = A2UIComponent(
            id="greeting",
            type=ComponentType.TEXT,
            properties={"content": "Hello"},
        )
        resp = A2UIResponse(components=[comp], root_id="greeting")
        d = resp.to_dict()

        assert d["root"] == "greeting"
        assert len(d["components"]) == 1
        assert d["components"][0]["type"] == "text"
        assert d["components"][0]["properties"]["content"] == "Hello"
        assert d["metadata"] == {}

    def test_metadata_preserved(self) -> None:
        """Custom metadata survives serialization."""
        resp = A2UIResponse(
            components=[],
            root_id="r",
            metadata={"theme": "dark", "version": 2},
        )
        d = resp.to_dict()
        assert d["metadata"]["theme"] == "dark"
        assert d["metadata"]["version"] == 2

    def test_created_at_is_timestamp(self) -> None:
        """created_at defaults to current epoch time."""
        before = time.time()
        resp = A2UIResponse(components=[], root_id="r")
        after = time.time()
        assert before <= resp.created_at <= after

    def test_multiple_components(self) -> None:
        """Multiple components serialize independently."""
        comps = [A2UIComponent(id=f"c{i}", type=ComponentType.BUTTON) for i in range(5)]
        resp = A2UIResponse(components=comps, root_id="c0")
        d = resp.to_dict()
        assert len(d["components"]) == 5
        assert [c["id"] for c in d["components"]] == [f"c{i}" for i in range(5)]


# ---------------------------------------------------------------------------
# A2UIAdapter — Catalog loading
# ---------------------------------------------------------------------------


class TestCatalogLoading:
    """Test the _load_catalog mechanism."""

    def test_fallback_catalog_used_when_no_spec(self, adapter_no_spec: A2UIAdapter) -> None:
        """When spec dir doesn't exist, fallback to built-in ComponentType."""
        assert adapter_no_spec.catalog_size == len(ComponentType)

    def test_catalog_loaded_from_spec(self, adapter_with_spec: A2UIAdapter) -> None:
        """Spec directory loads component types from JSON files."""
        # 3 valid JSON files: text, button, custom_widget
        # (broken.json is silently skipped)
        assert adapter_with_spec.catalog_size == 3
        assert "custom_widget" in adapter_with_spec._component_catalog

    def test_broken_json_skipped(self, tmp_spec_dir: Path) -> None:
        """Broken JSON files in spec/ are silently ignored."""
        adapter = A2UIAdapter(a2ui_root=tmp_spec_dir)
        # broken.json should not contribute to catalog
        assert "broken" not in adapter._component_catalog

    def test_spec_file_without_type_key(self, tmp_path: Path) -> None:
        """JSON files without a 'type' key are skipped."""
        spec = tmp_path / "spec"
        spec.mkdir()
        (spec / "no_type.json").write_text(json.dumps({"name": "widget"}))
        adapter = A2UIAdapter(a2ui_root=tmp_path)
        assert adapter.catalog_size == 0


# ---------------------------------------------------------------------------
# A2UIAdapter — render() method
# ---------------------------------------------------------------------------


class TestRender:
    """Test the async render() method across all code paths."""

    @pytest.mark.asyncio
    async def test_render_with_components(self, adapter_no_spec: A2UIAdapter) -> None:
        """Render a list of explicit components."""
        payload = {
            "components": [
                {"id": "title", "type": "text", "properties": {"content": "Hi"}},
                {"id": "btn", "type": "button", "properties": {"label": "Click"}},
            ]
        }
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "title"
        assert len(result["components"]) == 2
        assert result["components"][1]["type"] == "button"

    @pytest.mark.asyncio
    async def test_render_auto_id_generation(self, adapter_no_spec: A2UIAdapter) -> None:
        """Components without explicit IDs get auto-generated ones."""
        payload = {
            "components": [
                {"type": "text"},
                {"type": "button"},
            ]
        }
        result = await adapter_no_spec.render(payload)
        ids = [c["id"] for c in result["components"]]
        assert ids == ["comp_0", "comp_1"]

    @pytest.mark.asyncio
    async def test_render_template_error(self, adapter_no_spec: A2UIAdapter) -> None:
        """Error template renders a card with severity."""
        payload = {
            "template": "error",
            "data": {"message": "Something broke", "severity": "fatal"},
        }
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "error_card"
        assert result["components"][0]["properties"]["message"] == "Something broke"
        assert result["components"][0]["properties"]["severity"] == "fatal"

    @pytest.mark.asyncio
    async def test_render_template_error_defaults(self, adapter_no_spec: A2UIAdapter) -> None:
        """Error template uses defaults when data is empty."""
        payload = {"template": "error", "data": {}}
        result = await adapter_no_spec.render(payload)
        assert result["components"][0]["properties"]["message"] == "An error occurred"
        assert result["components"][0]["properties"]["severity"] == "error"

    @pytest.mark.asyncio
    async def test_render_template_status(self, adapter_no_spec: A2UIAdapter) -> None:
        """Status template renders a card with title and items."""
        payload = {
            "template": "status",
            "data": {"title": "System OK", "items": ["a", "b"]},
        }
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "status_card"
        props = result["components"][0]["properties"]
        assert props["title"] == "System OK"
        assert props["items"] == ["a", "b"]

    @pytest.mark.asyncio
    async def test_render_template_unknown(self, adapter_no_spec: A2UIAdapter) -> None:
        """Unknown templates return an error dict."""
        payload = {"template": "nonexistent_template"}
        result = await adapter_no_spec.render(payload)
        assert "error" in result
        assert "nonexistent_template" in result["error"]

    @pytest.mark.asyncio
    async def test_render_text_card_fallback(self, adapter_no_spec: A2UIAdapter) -> None:
        """Payloads without components or template produce a text card."""
        payload = {"message": "raw data", "count": 42}
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "text_card"
        content = result["components"][0]["properties"]["content"]
        parsed = json.loads(content)
        assert parsed["message"] == "raw data"
        assert parsed["count"] == 42

    @pytest.mark.asyncio
    async def test_render_empty_components_list(self, adapter_no_spec: A2UIAdapter) -> None:
        """Empty components list falls through to text_card fallback."""
        payload = {"components": [], "note": "empty"}
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "text_card"

    @pytest.mark.asyncio
    async def test_render_template_takes_priority(self, adapter_no_spec: A2UIAdapter) -> None:
        """When both template and components are present, template wins."""
        payload = {
            "template": "error",
            "data": {"message": "template wins"},
            "components": [{"id": "ignored", "type": "text"}],
        }
        result = await adapter_no_spec.render(payload)
        assert result["root"] == "error_card"

    @pytest.mark.asyncio
    async def test_render_count_increments(self, adapter_no_spec: A2UIAdapter) -> None:
        """render_count increments with each call."""
        assert adapter_no_spec.render_count == 0
        await adapter_no_spec.render({"template": "status", "data": {}})
        assert adapter_no_spec.render_count == 1
        await adapter_no_spec.render({"message": "x"})
        assert adapter_no_spec.render_count == 2

    @pytest.mark.asyncio
    async def test_render_children_preserved(self, adapter_no_spec: A2UIAdapter) -> None:
        """Component children IDs are preserved through rendering."""
        payload = {
            "components": [
                {
                    "id": "parent",
                    "type": "container",
                    "children": ["child_a", "child_b"],
                },
            ]
        }
        result = await adapter_no_spec.render(payload)
        assert result["components"][0]["children"] == ["child_a", "child_b"]

    @pytest.mark.asyncio
    async def test_render_invalid_component_type_raises(self, adapter_no_spec: A2UIAdapter) -> None:
        """Invalid component type raises ValueError."""
        payload = {
            "components": [{"id": "bad", "type": "nonexistent_type"}],
        }
        with pytest.raises(ValueError, match="nonexistent_type"):
            await adapter_no_spec.render(payload)
