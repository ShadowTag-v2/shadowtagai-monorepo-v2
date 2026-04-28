# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""ShadowTag-v4 Bridge Client (Mock)
Provides connectivity to the Sovereign Task Queue and Iceberg Data Lake.
"""

import logging
import uuid

logger = logging.getLogger("bridge_client")


class BridgeClient:
    def __init__(self):
        self.tasks = {}

    def dispatch_task(self, instruction: str, url: str = None, intent: str = "general") -> str:
        """Mock: Dispatch task to Firestore"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        self.tasks[task_id] = {
            "status": "dispatched",
            "instruction": instruction,
            "url": url,
            "intent": intent,
            "result": None,
        }
        logger.info(f"🚀 [MOCK] Task dispatched: {task_id}")
        return task_id

    def get_task_status(self, task_id: str) -> dict:
        """Mock: Get task status and A2UI result"""
        if task_id not in self.tasks:
            return {"status": "error", "message": "Task not found"}

        # Simulate completion with a mock A2UI payload
        task = self.tasks[task_id]
        if task["status"] == "dispatched":
            task["status"] = "completed"
            task["result"] = {
                "type": "A2UI_PAYLOAD",
                "root_id": "root",
                "components": [
                    {
                        "id": "root",
                        "type": "Text",
                        "props": {
                            "content": f"Mock result for: {task['instruction']}",
                            "variant": "h1",
                        },
                        "children": ["details"],
                    },
                    {
                        "id": "details",
                        "type": "Text",
                        "props": {"content": "This is a mock response from the Sovereign Bridge."},
                    },
                ],
            }

        return task

    def query_lake(self, sql: str) -> list:
        """Mock: Query Iceberg Data Lake"""
        logger.info(f"🔍 [MOCK] Lake query: {sql}")
        return [{"col1": "mock_data", "col2": 123}]


# Singleton
bridge = BridgeClient()
