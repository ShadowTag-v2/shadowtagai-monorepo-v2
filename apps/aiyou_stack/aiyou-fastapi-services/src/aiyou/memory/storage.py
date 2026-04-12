import json
import logging
from typing import Any

# Try importing google cloud libraries
try:
    from google.cloud import firestore, storage
except ImportError:
    storage = None
    firestore = None
    print("Warning: google-cloud-storage or google-cloud-firestore not installed.")

logger = logging.getLogger(__name__)


class MemoryStorage:
    def __init__(self, gcs_bucket_name: str = "acquired-jet-478701-b3-workbench-memory"):
        self.gcs_bucket_name = gcs_bucket_name
        self._storage_client = None
        self._firestore_client = None

    @property
    def storage_client(self):
        if self._storage_client is None and storage:
            self._storage_client = storage.Client()
        return self._storage_client

    @property
    def firestore_client(self):
        if self._firestore_client is None and firestore:
            self._firestore_client = firestore.Client()
        return self._firestore_client

    def load_from_gcs(self, blob_name: str = "memory/current.json") -> dict[str, Any]:
        """
        Loads memory from GCS (GKE pods).
        Bucket: acquired-jet-478701-b3-workbench-memory
        """
        if not self.storage_client:
            logger.warning("Google Cloud Storage client not available.")
            return {}

        try:
            bucket = self.storage_client.bucket(self.gcs_bucket_name)
            blob = bucket.blob(blob_name)
            content = blob.download_as_text()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load memory from GCS: {e}")
            return {}

    def load_from_firestore(
        self, collection: str = "claude_memory", document: str = "current"
    ) -> dict[str, Any]:
        """
        Loads memory from Firestore (real-time).
        Collection: claude_memory
        Document: current
        """
        if not self.firestore_client:
            logger.warning("Google Cloud Firestore client not available.")
            return {}

        try:
            doc_ref = self.firestore_client.collection(collection).document(document)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning(f"Document {collection}/{document} does not exist.")
                return {}
        except Exception as e:
            logger.error(f"Failed to load memory from Firestore: {e}")
            return {}


def get_memory_from_gcs(
    bucket_name: str = "acquired-jet-478701-b3-workbench-memory",
    blob_name: str = "memory/current.json",
):
    """
    Direct implementation of user snippet for GCS.
    """
    if not storage:
        raise ImportError("google-cloud-storage is required")
    blob = storage.Client().bucket(bucket_name).blob(blob_name)
    return json.loads(blob.download_as_text())


def get_memory_from_firestore(collection: str = "claude_memory", document: str = "current"):
    """
    Direct implementation of user snippet for Firestore.
    """
    if not firestore:
        raise ImportError("google-cloud-firestore is required")
    doc = firestore.Client().collection(collection).document(document).get()
    return doc.to_dict()
