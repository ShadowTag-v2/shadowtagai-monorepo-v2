import asyncio
import logging


class AsyncEvidenceLogger:
    def __init__(self, target_path: str):
        self.target_path = target_path
        self._queue = asyncio.Queue()
        self._worker_task = asyncio.create_task(self._process_queue())
        self.logger = logging.getLogger("kairos.evidence")

    async def log_evidence(self, data: str):
        await self._queue.put(data)

    async def _process_queue(self):
        while True:
            data = await self._queue.get()
            try:
                # Concurrent write path
                with open(self.target_path, "a") as f:
                    f.write(f"{data}\n")
            except Exception as e:
                self.logger.error(f"AsyncEvidenceLogger failed to write: {e}")
            finally:
                self._queue.task_done()
