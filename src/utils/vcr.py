import re

class VCRDehydrator:
    def __init__(self, cwd):
        self.cwd = cwd

    def dehydrate(self, text: str) -> str:
        """Normalizes paths and timestamps for deterministic test replay."""
        text = text.replace(self.cwd, "[CWD]")
        text = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z?', '[TIMESTAMP]', text)
        text = re.sub(r'\d+ms', '[DURATION]', text)
        return text
