import logging
import os
import signal
import time

import psutil

logger = logging.getLogger("rkill-monitor")


class RKillMonitor:
    """Rogue Agent Squashing Policy ('The Three Strikes of Death').
    Monitors process health and kills if thresholds are exceeded.
    """

    def __init__(self):
        self.strike_limit = 3
        self.strikes = {"memory": 0, "time": 0, "forbidden_access": 0}
        self.start_time = time.time()
        self.step_start_time = time.time()

    def reset_step_timer(self):
        """Call at start of each iteration step."""
        self.step_start_time = time.time()

    # Strike 1: Memory Gluttony
    def check_memory(self):
        """Kill if >1GB RAM or >80% container limit"""
        try:
            proc = psutil.Process(os.getpid())
            mem_mb = proc.memory_info().rss / (1024**2)
            if mem_mb > 1024:
                self.strikes["memory"] += 1
                logger.warning(
                    f"[RKILL] Memory Warning: {mem_mb:.1f}MB used. Strike {self.strikes['memory']}.",
                )
                if self.strikes["memory"] >= 1:  # Strict Mode
                    self._kill("Memory exceeded 1GB")
        except Exception as e:
            logger.error(f"[RKILL] Memory check failed: {e}")

    # Strike 2: Time Dilation
    def check_time(self):
        """Kill if single step >300s or total >1hr"""
        total_elapsed = time.time() - self.start_time
        step_elapsed = time.time() - self.step_start_time

        if total_elapsed > 3600:
            self._kill("Total execution time exceeded 1hr")

        if step_elapsed > 300:
            self.strikes["time"] += 1
            if self.strikes["time"] >= 1:
                self._kill("Step time limit exceeded 300s")

    # Strike 3: Forbidden Touch
    def check_file_access(self, filepath: str):
        """Kill immediately on sensitive access"""
        forbidden = ["/etc/passwd", ".env", "id_rsa", "/.aws/", "/proc/self/"]
        for pattern in forbidden:
            if pattern in filepath:
                self.strikes["forbidden_access"] += 1
                self._kill(f"Forbidden file access: {filepath}")

    def _kill(self, reason: str):
        """Immediate termination + audit log"""
        msg = f"[RKILL] TERMINATING AGENT: {reason}"
        logger.critical(msg)
        print(msg)
        # In Cloud Run, we just exit the process to restart the container
        # Revoke API token (simulated by crashing)
        os.kill(os.getpid(), signal.SIGKILL)
