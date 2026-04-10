import logging
from collections.abc import Callable
from typing import Any

# Mock logic for Firestore if not available
try:
    from google.cloud import firestore
except ImportError:

    class firestore:
        class Client:
            def collection(self, name):
                return CollectionRef()

    class CollectionRef:
        def on_snapshot(self, callback):
            pass


class PipelineOps:
    """
    Governance operations for Judge Six.
    """

    def __init__(self, db_client=None):
        self.db = db_client or firestore.Client()
        self.logger = logging.getLogger("judge_six_ops")

    def calculate_hot_risk(self, transactions: list[dict[str, Any]]) -> float:
        """
        Calculates the aggregate risk score from a list of transactions.

        Args:
            transactions: List of transaction dicts. Each should have 'risk_score' (float).

        Returns:
            Total risk score.
        """
        total_risk = 0.0
        for tx in transactions:
            score = tx.get("risk_score", 0.0)
            if not isinstance(score, (int, float)):
                self.logger.warning(f"Invalid risk_score type in tx {tx.get('id')}: {score}")
                continue
            total_risk += float(score)

        self.logger.info(f"Calculated Hot Risk for {len(transactions)} txs: {total_risk}")
        return total_risk

    def watch_stream(self, collection_name: str, callback: Callable[[list[Any], Any, Any], None]):
        """
        Wrapper around Firestore on_snapshot to expose real-time updates.

        Args:
            collection_name: The Firestore collection to watch.
            callback: The function to call when snapshot updates.
                      Signature: (col_snapshot, changes, read_time)
        """
        self.logger.info(f"Starting watch on stream: {collection_name}")
        try:
            doc_ref = self.db.collection(collection_name)

            # Create a callback wrapper to handle errors gracefully
            def safe_callback(col_snapshot, changes, read_time):
                try:
                    self.logger.debug(f"Stream update received for {collection_name}")
                    callback(col_snapshot, changes, read_time)
                except Exception as e:
                    self.logger.error(f"Error in stream callback: {e}")

            # Return the watch object (can be used to unsubscribe)
            return doc_ref.on_snapshot(safe_callback)

        except Exception as e:
            self.logger.error(f"Failed to attach listener to {collection_name}: {e}")
            raise


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ops = PipelineOps()

    # Test Risk Calc
    sample_txs = [{"id": "tx1", "risk_score": 0.5}, {"id": "tx2", "risk_score": 0.8}, {"id": "tx3", "risk_score": 0.1}]
    print(f"Total Risk: {ops.calculate_hot_risk(sample_txs)}")
