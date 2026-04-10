import datetime
import logging
import time
from dataclasses import dataclass, field
from enum import Enum

# Google Cloud Imports
from google.cloud import bigquery

from src.pnkln.clients.gdc import GDCClient
from src.pnkln.clients.spacex import StarlinkClient
from src.pnkln.cor import CorOrchestrator as Orchestrator
from src.pnkln.services.monetization import RateCard, RevenueEvent

# Import Core Pnkln Modules
from src.pnkln.shadowtag import ShadowTag

logger = logging.getLogger(__name__)


class ConnectionType(Enum):
    FIBER = "fiber"
    STARLINK = "starlink"
    SLICE_5G = "5g_slice"


@dataclass
class Telemetry:
    latency_ms: float
    jitter_ms: float
    gpu_temp_c: float
    power_draw_w: float
    active_inferences: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)


@dataclass
class TowerNode:
    node_id: str
    location_code: str  # e.g. "US-CA-LUC-001"
    hardware_spec: str  # e.g. "NEMA-4X-H100"

    # State
    is_active: bool = False
    current_connection: ConnectionType = ConnectionType.FIBER
    _rate_card: RateCard = field(default_factory=RateCard)

    # Modules
    _ledger: ShadowTag = field(default_factory=ShadowTag)
    _brain: Orchestrator = field(
        default_factory=lambda: Orchestrator(function_caller=None)
    )  # Mocking init args for now
    _bq_client: bigquery.Client | None = None

    # Hardware Clients (Stubs)
    _starlink: StarlinkClient | None = None
    _gdc: GDCClient | None = None

    def __post_init__(self):
        try:
            self._bq_client = bigquery.Client()
        except Exception as e:
            logger.warning(f"BigQuery client failed to init (running in offline/mock mode?): {e}")

        # Initialize Stubs
        self._starlink = StarlinkClient(dish_id=f"{self.node_id}-DISH")
        self._gdc = GDCClient(project_id="pnkln-edge", zone=self.location_code)

    def heartbeat(self) -> Telemetry:
        """
        Critical <100ms check.
        If Fiber latency > 100ms, trigger Starlink failover assessment.
        Logs telemetry to BigQuery.
        """
        # Mock telemetry reading from sensors
        # In prod: read from Prometheus/Node_Exporter
        t_now = self._read_hardware_sensors()

        # PnklnJR Doctrine: Failover Logic
        if t_now.latency_ms > 100 and self.current_connection == ConnectionType.FIBER:
            logger.warning(
                f"Node {self.node_id} latency spike ({t_now.latency_ms}ms). Assessing Starlink..."
            )
            self._evaluate_failover()

        # Log to BigQuery
        self._log_telemetry(t_now)

        return t_now

    def _read_hardware_sensors(self) -> Telemetry:
        # Placeholder for real sensor I/O
        return Telemetry(
            latency_ms=12.0, jitter_ms=2.0, gpu_temp_c=45.0, power_draw_w=800.0, active_inferences=5
        )

    def _evaluate_failover(self):
        """Check if Starlink path is stable (Jitter < 25ms per T-05)."""
        starlink_jitter = 20.0  # Mock reading
        if starlink_jitter < 25.0:
            logger.info(f"Switching Node {self.node_id} to STARLINK path.")
            self.current_connection = ConnectionType.STARLINK
        else:
            logger.error("Starlink path unstable. Maintaining degraded Fiber link.")

    def _log_telemetry(self, t: Telemetry):
        """Streaming insert to BigQuery."""
        if not self._bq_client:
            return

        row = {
            "event_timestamp": t.timestamp.isoformat(),
            "node_id": self.node_id,
            "location_code": self.location_code,
            "connection_type": self.current_connection.value,
            "latency_ms": t.latency_ms,
            "jitter_ms": t.jitter_ms,
            "gpu_temp_c": t.gpu_temp_c,
            "power_draw_w": t.power_draw_w,
            # "packet_loss_rate": 0.0 # Optional/Not in mock
        }

        table_id = "pnkln_intelligence.tower_metrics"
        errors = self._bq_client.insert_rows_json(table_id, [row])
        if errors:
            logger.error(f"BQ Insert Errors: {errors}")

    def process_workload(self, workload_id: str, data: bytes):
        """Execute Edge Inference, Calculate Revenue, and Log to ShadowTag."""
        start_time = time.time()

        # 1. Orchestrate
        result = self._brain.execute(workload_id, context={"raw_data": data})
        duration_ms = (time.time() - start_time) * 1000

        # 2. Revenue Event
        # Mocking data sizes for calculation
        # data size (MB) -> GB
        gb_processed = len(data) / (1024 * 1024 * 1024)

        rev_event = RevenueEvent(
            client_id="tbd_client",
            node_id=self.node_id,
            gb_processed_at_edge=gb_processed if gb_processed > 0 else 0.001,  # Min 1MB floor
            inference_count=1,
        )
        bill_amount = rev_event.calculate_bill(self._rate_card)

        # 3. Log Provenance (The "Revenue Event")
        self._ledger.watermark(
            content=workload_id,
            metadata={
                "event_type": "EDGE_INFERENCE",
                "node": self.node_id,
                "latency": duration_ms,
                "revenue_model": "PREMIUM_INFERENCE",
                "revenue_usd": bill_amount,
                "connection": self.current_connection.value,
            },
        )
        logger.info(f"Workload {workload_id} processed. Bill: ${bill_amount:.6f}")
        return result
