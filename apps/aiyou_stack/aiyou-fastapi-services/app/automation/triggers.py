"""
Trigger system for event-based automation.
"""

import logging
from typing import Any

from sqlalchemy import select

from app.automation.engine import workflow_engine
from app.core.database import AsyncSessionLocal
from app.models.automation import Trigger, TriggerType

logger = logging.getLogger(__name__)


class TriggerManager:
    """
    Manages triggers for event-based automation.
    """

    def __init__(self):
        self._event_triggers = {}
        self._webhook_triggers = {}

    async def load_triggers(self):
        """Load all enabled triggers from database."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Trigger).where(Trigger.enabled))
            triggers = result.scalars().all()

            logger.info(f"Loading {len(triggers)} triggers")

            for trigger in triggers:
                await self._register_trigger(trigger)

    async def _register_trigger(self, trigger: Trigger):
        """
        Register a trigger in memory.

        Args:
            trigger: Trigger instance to register
        """
        if trigger.trigger_type == TriggerType.EVENT:
            event_name = trigger.config.get("event_name")
            if event_name:
                if event_name not in self._event_triggers:
                    self._event_triggers[event_name] = []
                self._event_triggers[event_name].append(trigger)
                logger.info(f"Registered event trigger for '{event_name}'")

        elif trigger.trigger_type == TriggerType.WEBHOOK:
            webhook_path = trigger.config.get("webhook_path")
            if webhook_path:
                self._webhook_triggers[webhook_path] = trigger
                logger.info(f"Registered webhook trigger at '{webhook_path}'")

    async def unregister_trigger(self, trigger_id: int):
        """
        Unregister a trigger from memory.

        Args:
            trigger_id: ID of the trigger to unregister
        """
        # Remove from event triggers
        for event_name, triggers in list(self._event_triggers.items()):
            self._event_triggers[event_name] = [t for t in triggers if t.id != trigger_id]
            if not self._event_triggers[event_name]:
                del self._event_triggers[event_name]

        # Remove from webhook triggers
        for webhook_path, trigger in list(self._webhook_triggers.items()):
            if trigger.id == trigger_id:
                del self._webhook_triggers[webhook_path]

        logger.info(f"Unregistered trigger {trigger_id}")

    async def trigger_event(
        self, event_name: str, event_data: dict[str, Any] | None = None
    ) -> list[int]:
        """
        Trigger all workflows associated with an event.

        Args:
            event_name: Name of the event
            event_data: Data associated with the event

        Returns:
            List of job execution IDs
        """
        triggers = self._event_triggers.get(event_name, [])

        if not triggers:
            logger.debug(f"No triggers found for event '{event_name}'")
            return []

        logger.info(f"Triggering {len(triggers)} workflows for event '{event_name}'")

        execution_ids = []

        for trigger in triggers:
            # Check conditions
            if not await self._check_conditions(trigger, event_data):
                logger.debug(f"Trigger {trigger.id} conditions not met, skipping")
                continue

            # Execute workflow
            try:
                execution = await workflow_engine.execute_workflow(
                    workflow_id=trigger.workflow_id,
                    input_data=event_data,
                    trigger_id=trigger.id,
                )
                execution_ids.append(execution.id)

                logger.info(f"Triggered workflow {trigger.workflow_id} via event '{event_name}'")

            except Exception as e:
                logger.error(f"Failed to trigger workflow {trigger.workflow_id}: {e}")

        return execution_ids

    async def trigger_webhook(
        self, webhook_path: str, webhook_data: dict[str, Any] | None = None
    ) -> int | None:
        """
        Trigger a workflow via webhook.

        Args:
            webhook_path: Path of the webhook
            webhook_data: Data from the webhook request

        Returns:
            Job execution ID if successful, None otherwise
        """
        trigger = self._webhook_triggers.get(webhook_path)

        if not trigger:
            logger.debug(f"No webhook trigger found for path '{webhook_path}'")
            return None

        # Check conditions
        if not await self._check_conditions(trigger, webhook_data):
            logger.debug(f"Trigger {trigger.id} conditions not met, skipping")
            return None

        # Execute workflow
        try:
            execution = await workflow_engine.execute_workflow(
                workflow_id=trigger.workflow_id,
                input_data=webhook_data,
                trigger_id=trigger.id,
            )

            logger.info(f"Triggered workflow {trigger.workflow_id} via webhook '{webhook_path}'")

            return execution.id

        except Exception as e:
            logger.error(f"Failed to trigger workflow {trigger.workflow_id}: {e}")
            return None

    async def _check_conditions(self, trigger: Trigger, data: dict[str, Any] | None) -> bool:
        """
        Check if trigger conditions are met.

        Args:
            trigger: Trigger to check
            data: Data to check against

        Returns:
            True if conditions are met, False otherwise
        """
        if not trigger.conditions:
            return True

        if not data:
            return False

        # Simple condition checking (can be expanded)
        for key, expected_value in trigger.conditions.items():
            actual_value = data.get(key)

            if actual_value != expected_value:
                return False

        return True

    def get_webhook_paths(self) -> list[str]:
        """Get all registered webhook paths."""
        return list(self._webhook_triggers.keys())


# Global trigger manager instance
trigger_manager = TriggerManager()
