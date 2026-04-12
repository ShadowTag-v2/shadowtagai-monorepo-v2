"""
Thread Export Service - Export AI conversation threads in multiple formats.

Provides export functionality for OPORD contexts and conversation threads:
- JSON: Structured data export
- Markdown: Human-readable documentation format
- Text: Full-text compilation (concatenated threads with headers)
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

from agents.atomic_chat_manager import AtomicChatManager
from src.ShadowTag-v2.models.export import (
    ExportFormat,
    ExportStats,
    ThreadContent,
    ThreadExportRequest,
    ThreadMetadata,
)

logger = logging.getLogger(__name__)


class ThreadExportService:
    """
    Service for exporting AI conversation threads in various formats.

    Supports:
    - JSON: Full structured export with all metadata
    - Markdown: Documentation-style export with formatting
    - Text: Compilation format (like X thread compilations)
    """

    def __init__(self, db_path: str = "data/context_index.db"):
        self.chat_manager = AtomicChatManager(db_path=db_path)

    def export_threads(self, request: ThreadExportRequest) -> tuple[Any, ExportStats]:
        """
        Export threads based on request parameters.

        Args:
            request: Export request with format and filters

        Returns:
            Tuple of (content, stats)
        """
        # Fetch threads based on filters
        threads = self._fetch_threads(request)

        if not threads:
            return self._empty_export(request.format)

        # Export based on format
        if request.format == ExportFormat.JSON:
            content = self._export_json(threads, request.include_metadata)
        elif request.format == ExportFormat.MARKDOWN:
            content = self._export_markdown(threads, request.include_metadata)
        else:  # TEXT compilation
            content = self._export_text_compilation(threads, request.include_metadata)

        # Calculate stats
        stats = self._calculate_stats(threads, request.format, content)

        logger.info(f"Exported {len(threads)} threads in {request.format.value} format")

        return content, stats

    def export_single_thread(
        self, opord_number: int, format: ExportFormat = ExportFormat.JSON
    ) -> ThreadContent | None:
        """
        Export a single thread by OPORD number.

        Args:
            opord_number: Thread ID to export
            format: Export format

        Returns:
            ThreadContent or None if not found
        """
        results = self.chat_manager.search_opords(query=None)

        for opord in results:
            if opord.get("opord_number") == opord_number:
                return self._opord_to_thread_content(opord)

        return None

    def _fetch_threads(self, request: ThreadExportRequest) -> list[dict]:
        """Fetch threads based on request filters."""
        # If specific IDs provided, fetch those
        if request.thread_ids:
            all_opords = self.chat_manager.search_opords(query=None)
            threads = [o for o in all_opords if o.get("opord_number") in request.thread_ids]
        else:
            # Apply filters
            date_range = None
            if request.date_from or request.date_to:
                date_range = (request.date_from, request.date_to)

            threads = self.chat_manager.search_opords(
                query=None, tags=request.tags, agent_id=request.agent_id, date_range=date_range
            )

        # Additional filtering
        if request.shift_number is not None:
            threads = [t for t in threads if t.get("shift_number") == request.shift_number]

        if request.status:
            threads = [t for t in threads if t.get("status") == request.status]

        # Apply limit
        return threads[: request.limit]

    def _opord_to_thread_content(self, opord: dict) -> ThreadContent:
        """Convert OPORD dict to ThreadContent model."""
        metadata = ThreadMetadata(
            opord_number=opord.get("opord_number", 0),
            task_title=opord.get("task_title", "Untitled"),
            agent_id=opord.get("agent_id", "unknown"),
            shift_number=opord.get("shift_number", 0),
            status=opord.get("status", "unknown"),
            created_at=opord.get("created_at", datetime.now(UTC).isoformat()),
            updated_at=opord.get("updated_at"),
            tags=opord.get("tags", []) or [],
        )

        return ThreadContent(
            metadata=metadata,
            mission=opord.get("mission", {}),
            situation=opord.get("situation"),
            execution=opord.get("execution"),
            service_support=opord.get("service_support"),
            command_signal=opord.get("command_signal"),
            summary=opord.get("summary"),
            decisions=opord.get("decisions"),
        )

    def _export_json(self, threads: list[dict], include_metadata: bool = True) -> list[dict]:
        """Export threads as JSON array."""
        exported = []

        for thread in threads:
            thread_content = self._opord_to_thread_content(thread)
            exported.append(thread_content.model_dump())

        return exported

    def _export_markdown(self, threads: list[dict], include_metadata: bool = True) -> str:
        """Export threads as Markdown document."""
        lines = []

        # Header
        lines.append("# AI Thread Export")
        lines.append(f"\n*Generated on {datetime.now(UTC).strftime('%B %d, %Y')}*")
        lines.append(f"\n**Total Threads:** {len(threads)}")
        lines.append("\n---\n")

        for thread in threads:
            tc = self._opord_to_thread_content(thread)

            # Thread header
            lines.append(f"## Thread {tc.metadata.opord_number:05d}: {tc.metadata.task_title}")
            lines.append("")

            if include_metadata:
                lines.append(f"**Agent:** {tc.metadata.agent_id}")
                lines.append(f"**Shift:** {tc.metadata.shift_number}")
                lines.append(f"**Status:** {tc.metadata.status}")
                lines.append(f"**Created:** {tc.metadata.created_at}")
                if tc.metadata.tags:
                    lines.append(f"**Tags:** {', '.join(tc.metadata.tags)}")
                lines.append("")

            # Mission (5W)
            lines.append("### Mission")
            for key, value in tc.mission.items():
                lines.append(f"- **{key.upper()}:** {value}")
            lines.append("")

            # Situation
            if tc.situation:
                lines.append("### Situation")
                for key, value in tc.situation.items():
                    lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
                lines.append("")

            # Execution
            if tc.execution:
                lines.append("### Execution")
                for key, value in tc.execution.items():
                    if isinstance(value, list):
                        lines.append(f"**{key.replace('_', ' ').title()}:**")
                        for item in value:
                            lines.append(f"  - {item}")
                    else:
                        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
                lines.append("")

            # Summary
            if tc.summary:
                lines.append("### Summary")
                lines.append(tc.summary)
                lines.append("")

            # Decisions
            if tc.decisions:
                lines.append("### Key Decisions")
                for decision in tc.decisions:
                    lines.append(f"- {decision}")
                lines.append("")

            lines.append("---\n")

        return "\n".join(lines)

    def _export_text_compilation(
        self,
        threads: list[dict],
        include_metadata: bool = True,
        title: str = None,
        description: str = None,
    ) -> str:
        """
        Export threads as full-text compilation.

        Similar format to X thread compilations - concatenated with headers.
        """
        lines = []

        # Compilation header
        comp_title = title or "AI Agent Threads Compilation"
        lines.append(f"### {comp_title}")

        if description:
            lines.append(f"*{description}*")
        else:
            lines.append(
                f"*Generated on {datetime.now(UTC).strftime('%B %d, %Y')}. "
                f"This is a complete export of {len(threads)} AI conversation threads.*"
            )
        lines.append("")

        # Calculate total character count for header
        total_chars = sum(len(json.dumps(t, default=str)) for t in threads)
        lines.append(f"*Total length: ~{total_chars:,} characters.*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Each thread
        for i, thread in enumerate(threads, 1):
            tc = self._opord_to_thread_content(thread)

            # Thread header with metadata
            header_parts = [
                f"**Thread {i}: {tc.metadata.task_title}**",
                f"(@{tc.metadata.agent_id})",
                f"- OPORD: {tc.metadata.opord_number:05d}",
                f"- Date: {tc.metadata.created_at[:10] if tc.metadata.created_at else 'Unknown'}",
                f"- Status: {tc.metadata.status}",
            ]
            lines.append(" ".join(header_parts))
            lines.append("")

            # Content
            lines.append(f'"1/ Mission: {tc.mission.get("what", "No mission specified")}"')
            lines.append("")

            if tc.mission.get("why"):
                lines.append(f"Why? {tc.mission['why']}")
                lines.append("")

            if tc.mission.get("who"):
                lines.append(f"Who: {tc.mission['who']}")
            if tc.mission.get("where"):
                lines.append(f"Where: {tc.mission['where']}")
            if tc.mission.get("when"):
                lines.append(f"When: {tc.mission['when']}")
            lines.append("")

            # Situation context
            if tc.situation:
                lines.append("2/ Situation:")
                for key, value in tc.situation.items():
                    clean_key = key.replace("_", " ").title()
                    lines.append(f"- {clean_key}: {value}")
                lines.append("")

            # Execution plan
            if tc.execution:
                lines.append("3/ Execution Plan:")
                intent = tc.execution.get(
                    "commanders_intent", tc.execution.get("concept_of_operations")
                )
                if intent:
                    lines.append(f"Intent: {intent}")

                tasks = tc.execution.get("tasks", [])
                if tasks:
                    lines.append("Tasks:")
                    for task in tasks[:5]:  # Limit to first 5
                        lines.append(f"  • {task}")
                lines.append("")

            # Summary and decisions
            if tc.summary:
                lines.append(f"4/ Summary: {tc.summary}")
                lines.append("")

            if tc.decisions:
                lines.append("Key Decisions:")
                for decision in tc.decisions:
                    lines.append(f"• {decision}")
                lines.append("")

            # Tags
            if tc.metadata.tags:
                lines.append(f"#{' #'.join(tc.metadata.tags)}")
                lines.append("")

            lines.append("---")
            lines.append("")

        lines.append("*End of compilation.*")

        return "\n".join(lines)

    def _calculate_stats(
        self, threads: list[dict], format: ExportFormat, content: Any
    ) -> ExportStats:
        """Calculate export statistics."""
        # Get date range
        dates = [t.get("created_at", "") for t in threads if t.get("created_at")]
        date_range = None
        if dates:
            date_range = {"earliest": min(dates), "latest": max(dates)}

        # Calculate character count
        if isinstance(content, str):
            char_count = len(content)
        else:
            char_count = len(json.dumps(content, default=str))

        return ExportStats(
            total_threads=len(threads),
            date_range=date_range,
            export_format=format.value,
            character_count=char_count,
            generated_at=datetime.now(UTC).isoformat(),
        )

    def _empty_export(self, format: ExportFormat) -> tuple[Any, ExportStats]:
        """Return empty export for no results."""
        if format == ExportFormat.JSON:
            content = []
        else:
            content = "No threads found matching the specified criteria."

        stats = ExportStats(
            total_threads=0,
            date_range=None,
            export_format=format.value,
            character_count=len(str(content)),
            generated_at=datetime.now(UTC).isoformat(),
        )

        return content, stats

    def get_export_preview(
        self, request: ThreadExportRequest, max_preview_length: int = 500
    ) -> dict[str, Any]:
        """
        Get a preview of what would be exported.

        Returns thread count and truncated preview without full export.
        """
        threads = self._fetch_threads(request)

        preview = {
            "total_threads": len(threads),
            "format": request.format.value,
            "thread_ids": [t.get("opord_number") for t in threads[:10]],
            "truncated": len(threads) > 10,
            "estimated_size_chars": sum(len(json.dumps(t, default=str)) for t in threads),
        }

        return preview
