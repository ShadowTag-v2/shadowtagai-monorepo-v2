# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class MockBridge:
    def get_task_status(self, task_id):
        return {
            "status": "MOCKED",
            "task_id": task_id,
            "result": "Bridge mocked for Judge 6 Migration",
        }

    def query_lake(self, sql):
        return [{"col1": "mock_data", "sql": sql}]


bridge = MockBridge()
