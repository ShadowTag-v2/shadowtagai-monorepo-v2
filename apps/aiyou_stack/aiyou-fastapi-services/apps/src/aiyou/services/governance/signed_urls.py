"""GCS Signed URL Generation for Governance Traces.

Provides secure, time-limited access to governance decision traces
stored in Google Cloud Storage. FedRAMP compliant.
"""

import os
from datetime import datetime, timedelta

from google.cloud import storage
from google.oauth2 import service_account

# Default configuration
DEFAULT_BUCKET = os.getenv("GOVERNANCE_BUCKET", "pnkln-governance-traces")
DEFAULT_EXPIRATION_MINUTES = 15


class SignedURLGenerator:
    """Generates signed URLs for GCS objects with time-limited access.

    Supports both Application Default Credentials (ADC) for production
    and explicit service account credentials for local development.
    """

    def __init__(
        self,
        bucket_name: str = DEFAULT_BUCKET,
        credentials_path: str | None = None,
    ):
        self.bucket_name = bucket_name

        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            # Use Application Default Credentials (workload identity in GKE)
            self.client = storage.Client()

        self.bucket = self.client.bucket(bucket_name)

    def generate_signed_url(
        self,
        blob_path: str,
        expiration_minutes: int = DEFAULT_EXPIRATION_MINUTES,
        method: str = "GET",
    ) -> str:
        """Generate a signed URL for a GCS object.

        Args:
            blob_path: Path to the object within the bucket (e.g., "traces/abc123.json")
            expiration_minutes: How long the URL remains valid
            method: HTTP method allowed (GET for read, PUT for upload)

        Returns:
            Signed URL string

        """
        blob = self.bucket.blob(blob_path)

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method=method,
        )

        return url

    def generate_trace_url(
        self,
        decision_id: str,
        expiration_minutes: int = DEFAULT_EXPIRATION_MINUTES,
    ) -> str:
        """Generate a signed URL for a governance trace JSON file.

        Args:
            decision_id: The unique decision/transaction ID
            expiration_minutes: URL validity period

        Returns:
            Signed URL for the trace JSON

        """
        blob_path = f"traces/{decision_id}.json"
        return self.generate_signed_url(blob_path, expiration_minutes)

    def upload_trace(
        self,
        decision_id: str,
        trace_data: dict,
    ) -> str:
        """Upload a governance trace to GCS.

        Args:
            decision_id: The unique decision/transaction ID
            trace_data: The trace data dictionary

        Returns:
            The GCS URI of the uploaded trace

        """
        import json

        blob_path = f"traces/{decision_id}.json"
        blob = self.bucket.blob(blob_path)

        # Add metadata
        trace_data["uploaded_at"] = datetime.utcnow().isoformat()
        trace_data["decision_id"] = decision_id

        blob.upload_from_string(
            json.dumps(trace_data, indent=2),
            content_type="application/json",
        )

        return f"gs://{self.bucket_name}/{blob_path}"


# Singleton instance
_generator: SignedURLGenerator | None = None


def get_signed_url_generator() -> SignedURLGenerator:
    """Get or create the singleton SignedURLGenerator instance."""
    global _generator
    if _generator is None:
        _generator = SignedURLGenerator()
    return _generator


def generate_trace_url(decision_id: str, expiration_minutes: int = 15) -> str:
    """Convenience function to generate a trace URL."""
    return get_signed_url_generator().generate_trace_url(decision_id, expiration_minutes)
