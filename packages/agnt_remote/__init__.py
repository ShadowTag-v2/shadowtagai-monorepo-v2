"""agnt_remote — Blackhole Sink for remote operations.

Hard-blocks ALL external network operations. Feature flags resolve
locally only. Telemetry routes to local disk. Analytics is no-op.
"""

from .analytics import NoOpAnalytics
from .feature_flags import LocalFeatureFlags
from .telemetry_sink import LocalTelemetrySink

__all__ = [
  "LocalFeatureFlags",
  "LocalTelemetrySink",
  "NoOpAnalytics",
]
