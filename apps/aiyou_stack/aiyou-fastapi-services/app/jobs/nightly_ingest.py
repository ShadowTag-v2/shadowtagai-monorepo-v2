# app/jobs/nightly_ingest.py
import asyncio
import logging
import os

from app.services.ethical_compliance import EthicalComplianceMonitor
from app.services.ingestion_analyzer import IngestionAnalyzer

# Structured Logging for Cloud Operations
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


async def run_god_mode_batch():
    logger.info("⚡ GOD MODE: Initiating 2AM Ingestion Sequence (Gemini 2.5 Pro)")

    # 1. Gatekeeper: Ethical Compliance
    # We do not crawl if we are violating robot laws.
    compliance = EthicalComplianceMonitor()
    score = await compliance.check_all_sources()

    # Compliance threshold from env
    threshold = float(os.getenv("COMPLIANCE_THRESHOLD", "95.0"))

    if score.overall_score < threshold:
        logger.fatal(
            f"🛑 ABORT: Compliance Score {score.overall_score}% is below threshold {threshold}%.",
        )
        raise SystemExit(1)  # Failing here prevents the Design Agent from running

    # 2. The Heavy Lift: Gemini 2.5 Analysis
    analyzer = IngestionAnalyzer()

    # Explicitly requesting the 2.5 Pro model version via Vertex AI
    # This assumes the environment variable MODEL_ID="gemini-3.1-flash-lite-preview" is set
    report = await analyzer.execute_nightly_batch(
        model_version=os.getenv("MODEL_VERSION", "gemini-3.1-flash-lite-preview"),
        optimize_for="runtime_efficiency",
    )

    # 3. The Handoff: Writing to the Shared Brain (NFS)
    output_path = os.getenv("INGESTION_REPORT_PATH", "/workspace/ingestion_report.json")
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report.json())
        logger.info(f"✅ SYNAPSE FIRED: Report written to {output_path}")
    except Exception as e:
        logger.error(f"❌ FAILED to write report to {output_path}: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    asyncio.run(run_god_mode_batch())
