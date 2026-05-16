# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
A2UIAdapter — Integration with google/A2UI.

Enables AI agents to render declarative UIs using the A2UI protocol.
Instead of generating raw HTML/code, agents emit a flat, ID-referenced
list of components that get rendered natively on any platform.

Protocol: https://a2ui.org
Repository: https://github.com/google/a2ui
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to the google/A2UI clone
_DEFAULT_A2UI_ROOT = Path(__file__).resolve().parents[3] / "external_repos" / "A2UI"


class ComponentType(Enum):
    """A2UI component types from the spec."""

    TEXT = "text"
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    LIST = "list"
    IMAGE = "image"
    TABLE = "table"
    CHART = "chart"
    CONTAINER = "container"
    FORM = "form"


@dataclass
class A2UIComponent:
    """A single A2UI component in the flat ID-referenced tree."""

    id: str
    type: ComponentType
    properties: dict[str, Any] = field(default_factory=dict)
    children: list[str] = field(default_factory=list)  # IDs, not nested objects
    parent_id: str | None = None


@dataclass
class A2UIResponse:
    """A complete A2UI response — flat list of components."""

    components: list[A2UIComponent]
    root_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the A2UI JSON protocol format."""
        return {
            "root": self.root_id,
            "components": [
                {
                    "id": c.id,
                    "type": c.type.value,
                    "properties": c.properties,
                    "children": c.children,
                }
                for c in self.components
            ],
            "metadata": self.metadata,
        }


class A2UIAdapter:
    """
    Adapter for the google/A2UI protocol.

    Converts structured payloads from the orchestrator into
    A2UI-compliant declarative component trees for rendering.
    """

    def __init__(self, a2ui_root: Path | None = None):
        self._a2ui_root = a2ui_root or _DEFAULT_A2UI_ROOT
        self._component_catalog: set[str] = set()
        self._render_count = 0
        self._load_catalog()

    def _load_catalog(self) -> None:
        """Load the component catalog from the A2UI spec directory."""
        spec_dir = self._a2ui_root / "spec"
        if not spec_dir.exists():
            # Fallback: use built-in component types
            self._component_catalog = {t.value for t in ComponentType}
            logger.info(
                "a2ui_adapter.fallback_catalog",
                count=len(self._component_catalog),
            )
            return

        # Scan spec for component definitions
        for f in spec_dir.rglob("*.json"):
            try:
                data = json.loads(f.read_text())
                if "type" in data:
                    self._component_catalog.add(data["type"])
            except Exception:
                pass

        logger.info(
            "a2ui_adapter.catalog_loaded",
            count=len(self._component_catalog),
        )

    async def render(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Render a payload into an A2UI response.

        Args:
            payload: Must contain 'components' (list of component dicts)
                     or 'template' (named template to render).

        Returns:
            A2UI-compliant JSON response.
        """
        self._render_count += 1

        template = payload.get("template", "")
        components = payload.get("components", [])

        if template:
            return self._render_template(template, payload.get("data", {}))

        if components:
            return self._render_components(components)

        # Default: wrap payload as a simple text card
        return self._render_text_card(payload)

    def _render_components(self, raw_components: list[dict]) -> dict[str, Any]:
        """Render a list of raw component dicts into A2UI format."""
        components = []
        for i, rc in enumerate(raw_components):
            comp = A2UIComponent(
                id=rc.get("id", f"comp_{i}"),
                type=ComponentType(rc.get("type", "text")),
                properties=rc.get("properties", {}),
                children=rc.get("children", []),
            )
            components.append(comp)

        root_id = components[0].id if components else "root"
        response = A2UIResponse(
            components=components,
            root_id=root_id,
        )
        return response.to_dict()

    def _render_template(self, template: str, data: dict) -> dict[str, Any]:
        """Render a named template with data binding."""
        # Built-in templates
        if template == "error":
            return A2UIResponse(
                components=[
                    A2UIComponent(
                        id="error_card",
                        type=ComponentType.CARD,
                        properties={
                            "title": "Error",
                            "message": data.get("message", "An error occurred"),
                            "severity": data.get("severity", "error"),
                        },
                    )
                ],
                root_id="error_card",
            ).to_dict()

        if template == "status":
            return A2UIResponse(
                components=[
                    A2UIComponent(
                        id="status_card",
                        type=ComponentType.CARD,
                        properties={
                            "title": data.get("title", "Status"),
                            "items": data.get("items", []),
                        },
                    )
                ],
                root_id="status_card",
            ).to_dict()

        return {"error": f"Unknown template: {template}"}

    def _render_text_card(self, payload: dict) -> dict[str, Any]:
        """Render a simple text card from arbitrary payload."""
        return A2UIResponse(
            components=[
                A2UIComponent(
                    id="text_card",
                    type=ComponentType.TEXT,
                    properties={"content": json.dumps(payload, indent=2)},
                )
            ],
            root_id="text_card",
        ).to_dict()

    @property
    def render_count(self) -> int:
        """Total renders since init."""
        return self._render_count

    @property
    def catalog_size(self) -> int:
        """Number of components in the catalog."""
        return len(self._component_catalog)
