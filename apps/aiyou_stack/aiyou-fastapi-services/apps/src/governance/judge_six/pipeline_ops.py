import threading
from collections.abc import Callable
from typing import Any

from google.cloud import firestore


class PipelineOps:
    def __init__(self, db: firestore.Client):
        self.db = db

    def calculate_hot_risk(self, transactions: list[dict[str, Any]]) -> float:
        """Calculates the aggregate 'Hot Risk' for a batch of transactions.
        Logic: SUM(risk_score) for the batch.
        """
        total_risk = 0.0
        for tx in transactions:
            risk_score = tx.get("risk_score", 0.0)
            # Ensure it's a number
            if isinstance(risk_score, (int, float)):
                total_risk += risk_score
        return total_risk

    def watch_stream(
        self,
        collection_name: str,
        callback: Callable[[list[firestore.DocumentSnapshot], Any, Any], None],
    ):
        """Watches a Firestore collection stream using on_snapshot."""
        col_ref = self.db.collection(collection_name)

        # Create an Event to keep the main thread alive if needed,
        # but typically this is run in a background thread or blocking process.
        done_event = threading.Event()

        def on_snapshot(col_snapshot, changes, read_time):
            """Wrapper callback to handle the snapshot."""
            try:
                # Delegate to the provided business logic callback
                callback(col_snapshot, changes, read_time)
            except Exception as e:
                print(f"Error in snapshot listener: {e}")

        # Start the watch
        doc_watch = col_ref.on_snapshot(on_snapshot)
        return doc_watch


# Example Usage / Prototype
if __name__ == "__main__":
    # Mock DB Client for local testing without creds (won't actually connect)
    print("PipelineOps module loaded.")
