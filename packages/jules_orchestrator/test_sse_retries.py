import logging
import pytest
from unittest.mock import patch, MagicMock
import time

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class SSEClientMock:
  def __init__(self, max_retries=3):
    self.max_retries = max_retries
    self.retries = 0

  def connect(self):
    logger.error("Connection failed")
    raise ConnectionError("Connection failed")

  def connect_with_retry(self):
    self.retries = 0
    while self.retries <= self.max_retries:
      try:
        logger.info(f"Attempting connection (attempt {self.retries})")
        return self.connect()
      except ConnectionError:
        if self.retries == self.max_retries:
          logger.error("Max retries exceeded")
          raise Exception("Max retries exceeded") from None
        backoff = self.calculate_backoff(self.retries)
        logger.info(f"Connection failed, retrying in {backoff}s...")
        time.sleep(backoff)
        self.retries += 1

  def calculate_backoff(self, attempt):
    return 2**attempt


def test_jules_sse_connection_retry_success():
  client = SSEClientMock(max_retries=3)
  client.connect = MagicMock(side_effect=[ConnectionError, ConnectionError, True])
  with patch("time.sleep") as mock_sleep:
    assert client.connect_with_retry() is True
    assert client.connect.call_count == 3
    assert mock_sleep.call_count == 2


def test_jules_sse_connection_max_retries_exceeded():
  client = SSEClientMock(max_retries=2)
  client.connect = MagicMock(side_effect=ConnectionError)
  with patch("time.sleep") as mock_sleep:
    with pytest.raises(Exception, match="Max retries exceeded"):
      client.connect_with_retry()
    assert client.connect.call_count == 3
    assert mock_sleep.call_count == 2


def test_jules_sse_backoff_strategy():
  client = SSEClientMock()
  assert client.calculate_backoff(0) == 1
  assert client.calculate_backoff(1) == 2
  assert client.calculate_backoff(2) == 4
