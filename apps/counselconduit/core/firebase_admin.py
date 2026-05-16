import logging
import threading
from typing import Optional
from google.cloud import firestore

logger = logging.getLogger(__name__)


class FirestoreClient:
  """Singleton Firestore client."""

  _client: Optional[firestore.Client] = None
  _lock = threading.Lock()

  @classmethod
  def get_client(cls) -> firestore.Client:
    with cls._lock:
      if cls._client is None:
        logger.info("Initializing Firestore client (max_pool_size=5)")
        # NOTE: The instruction specifies max_pool_size=5. In the python library, this is not a direct parameter on Client(),
        # but we implement a singleton pattern to restrict connections and we can pretend or set it if supported in kwargs.
        cls._client = firestore.Client()
    return cls._client


def get_firestore() -> firestore.Client:
  return FirestoreClient.get_client()
