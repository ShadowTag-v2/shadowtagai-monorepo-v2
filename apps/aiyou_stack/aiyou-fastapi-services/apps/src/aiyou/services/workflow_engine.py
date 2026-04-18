"""Workflow Execution Engine - Process Atomic Chat JSON Action Blocks

Executes workflow definitions like:
{
  "actions": [
    {"type": "AskForInput", "title": "Issue Title", "prompt": "..."},
    {"type": "GetDate", "format": "YYYY-MM-DD HH:mm"},
    {"type": "CreateNote", "folder": "Notes", "noteTitle": "Context Index"}
  ]
}

Maps to OPORD creation and Context Index operations.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from src.shadowtag_v4.services.context_index import ContextIndexService

logger = logging.getLogger(__name__)


class WorkflowExecutionEngine:
    """Executes JSON-defined workflows for atomic chat operations.

    Supports actions:
    - AskForInput: Collect user input (maps to mission fields)
    - GetDate: Timestamp generation
    - CreateNote: Create OPORD context
    - AppendToNote: Update existing OPORD
    - OpenApp: Trigger external integrations
    """

    def __init__(self):
        self.context_service = ContextIndexService()
        self.workflow_state = {}  # Stores variables during execution

    def execute_workflow(
        self,
        workflow: dict[str, Any],
        inputs: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Execute a workflow definition.

        Args:
            workflow: JSON workflow with "block_name", "description", "actions"
            inputs: Pre-filled input values (for API calls)

        Returns:
            Execution results with opord_number, status, outputs

        """
        block_name = workflow.get("block_name", "Unnamed Workflow")
        actions = workflow.get("actions", [])

        logger.info(f"Executing workflow: {block_name}")

        # Initialize state
        self.workflow_state = inputs or {}
        results = {
            "block_name": block_name,
            "started_at": datetime.now(UTC).isoformat(),
            "actions_executed": [],
            "opord_number": None,
            "status": "running",
        }

        try:
            for action in actions:
                action_type = action.get("type")
                action_result = self._execute_action(action)

                results["actions_executed"].append({"type": action_type, "result": action_result})

            results["status"] = "completed"
            results["completed_at"] = datetime.now(UTC).isoformat()

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)

        return results

    def _execute_action(self, action: dict[str, Any]) -> Any:
        """Execute a single action from workflow."""
        action_type = action.get("type")

        handlers = {
            "AskForInput": self._handle_ask_for_input,
            "GetDate": self._handle_get_date,
            "CreateNote": self._handle_create_note,
            "AppendToNote": self._handle_append_to_note,
            "OpenApp": self._handle_open_app,
        }

        handler = handlers.get(action_type)
        if not handler:
            raise ValueError(f"Unknown action type: {action_type}")

        return handler(action)

    def _handle_ask_for_input(self, action: dict) -> str:
        """Handle AskForInput action.

        In API mode, inputs are pre-filled. In interactive mode,
        this would prompt the user.
        """
        title = action.get("title", "Input")
        prompt = action.get("prompt", "")

        # Check if input was pre-filled
        value = self.workflow_state.get(title)

        if value is None:
            # In API mode, this is an error
            raise ValueError(f"Missing required input: {title}")

        logger.info(f"Input '{title}': {value[:50]}...")
        return value

    def _handle_get_date(self, action: dict) -> str:
        """Handle GetDate action.

        Generates current timestamp in specified format.
        """
        date_format = action.get("format", "%Y-%m-%d %H:%M")

        # Convert to Python strftime format
        date_format = date_format.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
        date_format = date_format.replace("HH", "%H").replace("mm", "%M")

        timestamp = datetime.now(UTC).strftime(date_format)
        self.workflow_state["Date"] = timestamp

        logger.info(f"Generated timestamp: {timestamp}")
        return timestamp

    def _handle_create_note(self, action: dict) -> dict:
        """Handle CreateNote action.

        Creates OPORD context in Context Index.
        Maps note content to OPORD structure.
        """
        note_title = action.get("noteTitle", "Untitled")
        content = action.get("content", "")

        # Expand template variables like {{Issue Title}}
        expanded_content = self._expand_template(content)

        # Parse content into OPORD structure
        opord_data = self._parse_note_to_opord(note_title, expanded_content)

        # Create context
        result = self.context_service.create_context(**opord_data)

        self.workflow_state["opord_number"] = result["opord_number"]

        logger.info(f"Created OPORD {result['opord_number']:05d} from note")
        return result

    def _handle_append_to_note(self, action: dict) -> dict:
        """Handle AppendToNote action.

        Updates existing OPORD context with summary/decisions.
        """
        note_title = action.get("noteTitle", "Context Index")
        content = action.get("content", "")

        # Expand template variables
        expanded_content = self._expand_template(content)

        # Get OPORD number from state
        opord_number = self.workflow_state.get("opord_number")
        if not opord_number:
            raise ValueError("No OPORD number in state for AppendToNote")

        # Parse content for summary/decisions
        summary, decisions = self._parse_append_content(expanded_content)

        # Update context
        success = self.context_service.update_context(
            opord_number=opord_number,
            summary=summary,
            decisions=decisions,
        )

        logger.info(f"Updated OPORD {opord_number:05d} with append")
        return {"opord_number": opord_number, "updated": success}

    def _handle_open_app(self, action: dict) -> dict:
        """Handle OpenApp action.

        Triggers external integrations (e.g., ChatGPT, Slack, GitHub).
        For now, just logs the action.
        """
        app_name = action.get("appName", "Unknown")

        # TODO: Implement actual integrations
        logger.info(f"Would open app: {app_name}")

        return {"app": app_name, "status": "simulated"}

    def _expand_template(self, template: str) -> str:
        """Expand template variables like {{Issue Title}}.

        Replaces with values from workflow_state.
        """
        expanded = template

        for key, value in self.workflow_state.items():
            placeholder = f"{{{{{key}}}}}"
            expanded = expanded.replace(placeholder, str(value))

        return expanded

    def _parse_note_to_opord(self, note_title: str, content: str) -> dict[str, Any]:
        """Parse note content into OPORD structure.

        Content format:
        Issue: <title>
        Date: <timestamp>
        Brief: <description>

        Summary:
        Key decisions:
        Tags:
        """
        lines = content.strip().split("\n")
        parsed = {}

        # Extract fields
        for line in lines:
            if line.startswith("Issue:"):
                parsed["issue"] = line.split(":", 1)[1].strip()
            elif line.startswith("Brief:"):
                parsed["brief"] = line.split(":", 1)[1].strip()
            elif line.startswith("Tags:"):
                tags_str = line.split(":", 1)[1].strip()
                parsed["tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Map to OPORD structure
        return {
            "task_title": parsed.get("issue", note_title),
            "agent_id": self.workflow_state.get("agent_id", "workflow_engine"),
            "shift_number": 0,  # Default to shift 0
            "mission": {
                "who": "Workflow execution",
                "what": parsed.get("brief", "Execute workflow"),
                "when": self.workflow_state.get("Date", datetime.now(UTC).isoformat()),
                "where": "Context Index",
                "why": "Atomic chat workflow automation",
            },
            "tags": parsed.get("tags", ["workflow", "automated"]),
        }

    def _parse_append_content(self, content: str) -> tuple:
        """Parse append content into summary and decisions.

        Format:
        Summary: <text>
        Key decisions: <comma separated>
        """
        lines = content.strip().split("\n")
        summary = ""
        decisions = []

        for line in lines:
            if line.startswith("Summary:"):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith("Key decisions:"):
                decisions_str = line.split(":", 1)[1].strip()
                decisions = [d.strip() for d in decisions_str.split(",") if d.strip()]

        return summary, decisions
