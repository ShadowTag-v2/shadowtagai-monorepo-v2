class HooksManager:
    """Command, Prompt, Agent, HTTP, and Function hooks across 24 events."""

    def __init__(self):
        self.hooks = {}

    def register(self, event, callback):
        self.hooks.setdefault(event, []).append(callback)

    async def emit(self, event, *args, **kwargs):
        for hook in self.hooks.get(event, []):
            await hook(*args, **kwargs)
