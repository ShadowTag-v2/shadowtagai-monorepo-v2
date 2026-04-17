"""
scripts/cinematic_studio.py
Telemetry capture and Auto-Healing boundary for the Cinematic Studio UI payload.
"""

import logging
import time
from collections import deque

try:
    from scripts.omega_auto_dispatcher import push_auto_repair_payload
except ImportError:
    # Handle if run from a different directory
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from scripts.omega_auto_dispatcher import push_auto_repair_payload

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CinematicTelemetry")


class CinematicTelemetry:
    def __init__(self):
        # Keep track of recent 500 errors to check for 3 concurrent hits
        self.recent_500s = deque(maxlen=3)
        self.error_threshold = 3
        self.time_window_seconds = 60

    def log_http_response(self, status_code: int, endpoint: str, stack_trace: str = ""):
        """
        Intercepts HTTP responses from the Cinematic UI.
        If a fatal 500 HTTP drop occurs over 3 concurrent hits, it autonomously dispatches
        a God Mode repair task directly to the agent swarm without user intervention.
        """
        if status_code == 500:
            current_time = time.time()
            self.recent_500s.append((current_time, endpoint, stack_trace))
            logger.error(f"Captured HTTP 500 Drop on {endpoint}")

            self._check_auto_heal_threshold()
        else:
            # If we get a 200, we might want to clear the queue if they aren't 'concurrent'
            # But we'll leave it as a sliding window of the last 3 errors for now.
            logger.info(f"Normal Response: {status_code} on {endpoint}")

    def _check_auto_heal_threshold(self):
        if len(self.recent_500s) == self.error_threshold:
            # Check if all 3 errors occurred within the time window
            first_error_time = self.recent_500s[0][0]
            last_error_time = self.recent_500s[-1][0]

            if (last_error_time - first_error_time) <= self.time_window_seconds:
                logger.critical("🔥 3 Concurrent HTTP 500s Detected! Triggering God Mode Auto-Repair Sequence.")

                # Combine stack traces to give context to the Swarm
                combined_stack = " | ".join([err[2] for err in self.recent_500s if err[2]])
                if not combined_stack:
                    combined_stack = "Fatal server error detected but no explicit traceback provided by node telemetry."

                # Autonomously dispatch repair task
                push_auto_repair_payload(combined_stack)

                # Clear queue to prevent spamming
                self.recent_500s.clear()


if __name__ == "__main__":
    # Test harness
    telemetry = CinematicTelemetry()
    telemetry.log_http_response(500, "/api/v1/render", "Traceback: ZeroDivisionError in render_pipeline")
    telemetry.log_http_response(500, "/api/v1/render", "Traceback: ZeroDivisionError in render_pipeline")
    telemetry.log_http_response(500, "/api/v1/render", "Traceback: ZeroDivisionError in render_pipeline")
