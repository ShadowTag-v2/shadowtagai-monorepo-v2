# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Proprietary
"""A2UI Widget Blueprints for CopilotKit frontends.

Declarative JSON schemas for generative UI components rendered by
the CopilotKit frontend consumer (per ADR 004).

Widget types:
- CitationCard: Legal citation with case name, reporter, and relevance score
- DataTable: Structured tabular data with sortable columns
- MetricChart: Time-series or aggregate metrics visualization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CitationCard:
    """A legal citation card for embedding in AG-UI streams.

    Rendered by the CopilotKit frontend as an interactive card
    with case details and a relevance score indicator.
    """

    widget_type: str = "citation_card"
    case_name: str = ""
    reporter: str = ""  # e.g., "123 F.3d 456"
    court: str = ""
    year: int = 0
    relevance_score: float = 0.0  # 0.0 to 1.0
    summary: str = ""
    url: str = ""

    def to_a2ui(self) -> dict[str, Any]:
        """Serialize to A2UI JSON for CopilotKit rendering."""
        return {
            "type": self.widget_type,
            "props": {
                "caseName": self.case_name,
                "reporter": self.reporter,
                "court": self.court,
                "year": self.year,
                "relevanceScore": self.relevance_score,
                "summary": self.summary,
                "url": self.url,
            },
        }


@dataclass
class DataTable:
    """A structured data table for embedding in AG-UI streams.

    Rendered by the CopilotKit frontend as a sortable, filterable table.
    """

    widget_type: str = "data_table"
    title: str = ""
    columns: list[dict[str, str]] = field(default_factory=list)
    rows: list[dict[str, Any]] = field(default_factory=list)
    sortable: bool = True
    filterable: bool = True

    def to_a2ui(self) -> dict[str, Any]:
        """Serialize to A2UI JSON for CopilotKit rendering."""
        return {
            "type": self.widget_type,
            "props": {
                "title": self.title,
                "columns": self.columns,
                "rows": self.rows,
                "sortable": self.sortable,
                "filterable": self.filterable,
            },
        }


@dataclass
class MetricChart:
    """A metrics visualization chart for embedding in AG-UI streams.

    Supports line, bar, and pie chart types. Rendered by the CopilotKit
    frontend using the client's preferred charting library.
    """

    widget_type: str = "metric_chart"
    title: str = ""
    chart_type: str = "line"  # line | bar | pie
    labels: list[str] = field(default_factory=list)
    datasets: list[dict[str, Any]] = field(default_factory=list)
    x_axis_label: str = ""
    y_axis_label: str = ""

    def to_a2ui(self) -> dict[str, Any]:
        """Serialize to A2UI JSON for CopilotKit rendering."""
        return {
            "type": self.widget_type,
            "props": {
                "title": self.title,
                "chartType": self.chart_type,
                "labels": self.labels,
                "datasets": self.datasets,
                "xAxisLabel": self.x_axis_label,
                "yAxisLabel": self.y_axis_label,
            },
        }


@dataclass
class UploadForm:
    """A file upload form for embedding in AG-UI streams.

    Allows clients to upload documents (contracts, briefs) for analysis.
    """

    widget_type: str = "upload_form"
    title: str = "Upload Document"
    accepted_types: list[str] = field(
        default_factory=lambda: [".pdf", ".docx", ".txt"]
    )
    max_size_mb: int = 25
    multiple: bool = False

    def to_a2ui(self) -> dict[str, Any]:
        """Serialize to A2UI JSON for CopilotKit rendering."""
        return {
            "type": self.widget_type,
            "props": {
                "title": self.title,
                "acceptedTypes": self.accepted_types,
                "maxSizeMb": self.max_size_mb,
                "multiple": self.multiple,
            },
        }
