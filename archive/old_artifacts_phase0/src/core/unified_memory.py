from src.services.context import FourTierContext
from src.services.secrets import SecretScanner


class UnifiedMemory:
    def __init__(self):
        self.memory_stream = []
        self.context_engine = FourTierContext()
        self.scanner = SecretScanner()

    def ingest_tool_output(self, tool_name: str, raw_output: str):
        # 1. Egress Scanner: Redact keys natively before LLM insertion
        safe_output = self.scanner.scan(raw_output)

        # 2. Ingest
        payload = {"role": "user", "content": f"[Tool: {tool_name}]\n{safe_output}"}
        self.memory_stream.append(payload)

        # 3. Microcompaction Pass: Stop memory bloat dynamically
        self.memory_stream = self.context_engine.microcompact(self.memory_stream)

        return self.memory_stream
