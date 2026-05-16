# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Cloud Storage Backend: Storage for artifacts (datasets, plots, reports).

Provides:
- Upload/download of large files (datasets, plots, PDFs)
- Organized storage by session
- Public URL generation for sharing
- Lifecycle management
"""

from __future__ import annotations
from pathlib import Path
import logging

try:
  from google.cloud import storage

  STORAGE_AVAILABLE = True
except ImportError:
  STORAGE_AVAILABLE = False
  logging.warning(
    "Cloud Storage SDK not installed. Install with: pip install google-cloud-storage"
  )

logger = logging.getLogger(__name__)


class CloudStorageBackend:
  """
  Cloud Storage persistence backend for large artifacts.

  Bucket structure:
      {bucket_name}/
          sessions/
              {session_id}/
                  datasets/
                      input_data.csv
                  plots/
                      analysis_001.png
                  reports/
                      final_report.pdf
                  code/
                      analysis_script.py
  """

  def __init__(
    self,
    project_id: str,
    bucket_name: str,
    create_bucket: bool = False,
  ):
    """
    Initialize Cloud Storage backend.

    Args:
        project_id: GCP project ID
        bucket_name: Storage bucket name
        create_bucket: Whether to create bucket if it doesn't exist
    """
    if not STORAGE_AVAILABLE:
      raise RuntimeError("Cloud Storage SDK not installed")

    self.project_id = project_id
    self.bucket_name = bucket_name

    self.client = storage.Client(project=project_id)

    # Get or create bucket
    try:
      self.bucket = self.client.bucket(bucket_name)
      if not self.bucket.exists():
        if create_bucket:
          self.bucket.create(location="US")
          logger.info(f"Created bucket {bucket_name}")
        else:
          raise ValueError(f"Bucket {bucket_name} does not exist")
      else:
        logger.info(f"Using existing bucket {bucket_name}")
    except Exception as e:
      logger.error(f"Failed to initialize bucket: {e}")
      raise

  def upload_file(
    self,
    session_id: str,
    file_path: str,
    artifact_type: str = "datasets",
    filename: str | None = None,
  ) -> str:
    """
    Upload a file to Cloud Storage.

    Args:
        session_id: Session ID
        file_path: Local file path
        artifact_type: Type of artifact (datasets, plots, reports, code)
        filename: Optional custom filename (uses original name if None)

    Returns:
        Public URL of uploaded file
    """
    if filename is None:
      filename = Path(file_path).name

    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)

    blob.upload_from_filename(file_path)

    logger.info(f"Uploaded {file_path} to gs://{self.bucket_name}/{blob_path}")

    return f"gs://{self.bucket_name}/{blob_path}"

  def upload_bytes(
    self,
    session_id: str,
    data: bytes,
    filename: str,
    artifact_type: str = "datasets",
    content_type: str | None = None,
  ) -> str:
    """
    Upload bytes to Cloud Storage.

    Args:
        session_id: Session ID
        data: Byte data to upload
        filename: Filename
        artifact_type: Type of artifact
        content_type: Optional content type (e.g., "image/png")

    Returns:
        Public URL of uploaded file
    """
    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)

    if content_type:
      blob.content_type = content_type

    blob.upload_from_string(data)

    logger.info(f"Uploaded {len(data)} bytes to gs://{self.bucket_name}/{blob_path}")

    return f"gs://{self.bucket_name}/{blob_path}"

  def download_file(
    self,
    session_id: str,
    filename: str,
    artifact_type: str = "datasets",
    local_path: str | None = None,
  ) -> str:
    """
    Download a file from Cloud Storage.

    Args:
        session_id: Session ID
        filename: Filename
        artifact_type: Type of artifact
        local_path: Optional local save path (uses filename if None)

    Returns:
        Local file path
    """
    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)

    if local_path is None:
      local_path = filename

    blob.download_to_filename(local_path)

    logger.info(f"Downloaded gs://{self.bucket_name}/{blob_path} to {local_path}")

    return local_path

  def download_bytes(
    self,
    session_id: str,
    filename: str,
    artifact_type: str = "datasets",
  ) -> bytes:
    """
    Download file as bytes.

    Args:
        session_id: Session ID
        filename: Filename
        artifact_type: Type of artifact

    Returns:
        File contents as bytes
    """
    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)

    data = blob.download_as_bytes()

    logger.info(
      f"Downloaded {len(data)} bytes from gs://{self.bucket_name}/{blob_path}"
    )

    return data

  def list_artifacts(
    self,
    session_id: str,
    artifact_type: str | None = None,
  ) -> list[str]:
    """
    List artifacts for a session.

    Args:
        session_id: Session ID
        artifact_type: Optional artifact type filter

    Returns:
        List of blob paths
    """
    prefix = f"sessions/{session_id}/"
    if artifact_type:
      prefix += f"{artifact_type}/"

    blobs = self.bucket.list_blobs(prefix=prefix)

    return [blob.name for blob in blobs]

  def get_public_url(
    self,
    session_id: str,
    filename: str,
    artifact_type: str = "datasets",
    expiration_hours: int = 24,
  ) -> str:
    """
    Get a signed public URL for sharing.

    Args:
        session_id: Session ID
        filename: Filename
        artifact_type: Type of artifact
        expiration_hours: URL expiration in hours

    Returns:
        Signed public URL
    """
    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)

    from datetime import timedelta

    url = blob.generate_signed_url(
      version="v4",
      expiration=timedelta(hours=expiration_hours),
      method="GET",
    )

    return url

  def delete_artifact(
    self,
    session_id: str,
    filename: str,
    artifact_type: str = "datasets",
  ):
    """
    Delete an artifact.

    Args:
        session_id: Session ID
        filename: Filename
        artifact_type: Type of artifact
    """
    blob_path = f"sessions/{session_id}/{artifact_type}/{filename}"
    blob = self.bucket.blob(blob_path)
    blob.delete()

    logger.info(f"Deleted gs://{self.bucket_name}/{blob_path}")

  def delete_session_artifacts(self, session_id: str):
    """
    Delete all artifacts for a session.

    Args:
        session_id: Session ID
    """
    prefix = f"sessions/{session_id}/"
    blobs = self.bucket.list_blobs(prefix=prefix)

    deleted_count = 0
    for blob in blobs:
      blob.delete()
      deleted_count += 1

    logger.info(f"Deleted {deleted_count} artifacts for session {session_id}")

  def __repr__(self) -> str:
    return f"CloudStorageBackend(bucket={self.bucket_name})"
