import logging
import time

from libs.steel.pruner import CodePruner
from libs.steel.vfs import ShadowVFS
from src.shield.judge import Judge6

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelLoop")


class SentinelController:
    """
    ShadowTag Omega V7 OODA Loop Controller
    Observe, Orient, Decide, Act.
    """

    def __init__(self, root_dir: str):
        self.vfs = ShadowVFS(root_dir)
        self.pruner = CodePruner(root_dir)
        self.judge = Judge6("shadowtag-omega-v2")
        self.is_running = True

    def run_loop(self):
        logger.info("📡 SENTINEL: OODA Loop Initiated.")
        while self.is_running:
            try:
                # 1. OBSERVE: Scan for changes or objectives
                logger.info("👀 [OBSERVE] Scanning workspace...")

                # 2. ORIENT: Contextualize and prune
                logger.info("🧭 [ORIENT] Pruning context...")

                # 3. DECIDE: Policy check
                if self.judge.inspect("Maintenance Loop"):
                    # 4. ACT: Perform maintenance or tasks
                    logger.info("⚡ [ACT] Executing state refresh...")

                time.sleep(30)  # Wait for next beat
            except KeyboardInterrupt:
                self.is_running = False
                logger.info("🛑 SENTINEL: Loop Terminated.")


if __name__ == "__main__":
    controller = SentinelController(".")
    controller.run_loop()
