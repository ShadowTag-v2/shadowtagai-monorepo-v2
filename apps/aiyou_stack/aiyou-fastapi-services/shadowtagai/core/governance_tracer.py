"""Governance Tracer - Monetizes transparency via signed audit URLs.

Captures Judge 6 decision logs, uploads to private GCS bucket,
and mints time-limited "Teleport" URLs for paid audit trail access.
"""

import datetime
import json
import os

from google.cloud import storage


class GovernanceTracer:
    """The Single Point of Truth for governance decision audit trails.
    Uploads traces to GCS and generates temporary signed URLs.
    """

    def __init__(self, bucket_name: str = None, sa_json_path: str = None):
        """Initialize with private trace bucket.

        Args:
            bucket_name: GCS bucket for traces (default: from env)
            sa_json_path: Path to service account key (None for ADC)

        """
        self.bucket_name = bucket_name or os.getenv(
            "GOVERNANCE_TRACES_BUCKET",
            "shadowtagai-governance-traces",
        )

        if sa_json_path:
            self.client = storage.Client.from_service_account_json(sa_json_path)
        else:
            self.client = storage.Client()

        self.bucket = self.client.bucket(self.bucket_name)

    def capture_decision(
        self,
        decision_id: str,
        logic_log: list,
        inputs: dict,
        result: str,
        metadata: dict = None,
    ) -> dict:
        """Packages execution context into rigid audit format.

        Args:
            decision_id: Unique identifier for this decision
            logic_log: Step-by-step reasoning trace
            inputs: The data being judged
            result: Final verdict (APPROVED/REJECTED/ESCALATE)
            metadata: Additional context (optional)

        Returns:
            Structured trace data dict

        """
        trace_data = {
            "decision_id": decision_id,
            "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            "judge_version": "Judge 6 (v1.1.0)",
            "inputs": inputs,
            "logic_trace": logic_log,
            "final_verdict": result,
            "metadata": metadata or {},
        }
        return trace_data

    def upload_and_sign(self, decision_id: str, trace_data: dict, expiration_mins: int = 15) -> str:
        """Uploads trace to GCS and generates temporary signed URL.

        Args:
            decision_id: Unique identifier for this decision
            trace_data: The audit trail data to store
            expiration_mins: How long the URL is valid (default: 15)

        Returns:
            Signed URL for temporary read access

        """
        blob_name = f"traces/{datetime.date.today()}/{decision_id}.json"
        blob = self.bucket.blob(blob_name)

        # Upload the trace (private by default)
        blob.upload_from_string(json.dumps(trace_data, indent=2), content_type="application/json")

        # Mint the signed URL
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=expiration_mins),
            method="GET",
        )

        return url

    def get_or_generate_trace(self, decision_id: str, expiration_mins: int = 15) -> str:
        """Generates new signed URL for existing trace.

        Args:
            decision_id: The decision to retrieve
            expiration_mins: URL validity period

        Returns:
            Signed URL or None if not found

        """
        # Search for the trace (could be any date)
        prefix = "traces/"
        blobs = list(self.bucket.list_blobs(prefix=prefix))

        for blob in blobs:
            if decision_id in blob.name:
                return blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(minutes=expiration_mins),
                    method="GET",
                )

        return None


# Convenience function for quick integration
def trace_judge_decision(
    decision_id: str,
    logic_log: list,
    inputs: dict,
    result: str,
    bucket_name: str = None,
) -> str:
    """One-liner to capture and sign a governance decision.

    Returns signed URL for the audit trail.
    """
    tracer = GovernanceTracer(bucket_name=bucket_name)
    trace_data = tracer.capture_decision(decision_id, logic_log, inputs, result)
    return tracer.upload_and_sign(decision_id, trace_data)


if __name__ == "__main__":
    # Test simulation
    tracer = GovernanceTracer()
    tx_id = "tx_test_001"

    decision_log = [
        "STEP 1: ATP 5-19 scan... OK",
        "STEP 2: Risk classification... TIER_2_LOW",
        "STEP 3: Audit compress... 487 bytes",
        "STEP 4: Policy check... APPROVED",
    ]

    data = tracer.capture_decision(tx_id, decision_log, {"file": "test_video.mp4"}, "APPROVED")

    print(f"Trace data: {json.dumps(data, indent=2)}")
    print("\nTo generate signed URL, ensure GCS bucket exists and run with credentials.")
