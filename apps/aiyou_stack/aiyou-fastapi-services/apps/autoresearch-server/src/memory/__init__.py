# Mock Memory Module to satisfy main.py import
def get_memory_storage():
    class MockMemory:
        def load_from_firestore(self):
            return {"status": "ACTIVE", "memory_id": "MOCK-123"}

        def save_context(self, ctx):
            pass

    return MockMemory()
