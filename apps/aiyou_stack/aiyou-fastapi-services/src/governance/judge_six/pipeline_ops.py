#!/usr/bin/env python3
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("JudgeSix.PipelineOps")


def calculate_hot_risk(transactions: list[dict[str, Any]]) -> float:
    """Scans a batch of transactions and computes the aggregate 'hot' risk.
    If 'risk_score' is not present in a transaction, it evaluates to 0.0.
    """
    if not isinstance(transactions, list):
        logger.error(f"Expected list of transactions, got {type(transactions)}")
        raise ValueError("Invalid transactions payload format.")

    total_risk: float = 0.0
    for idx, tx in enumerate(transactions):
        try:
            score = tx.get("risk_score", 0.0)
            total_risk += float(score)
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid risk score at index {idx} ({tx.get('risk_score')}): {e}. Defaulting to 0.0",
            )

    logger.debug(f"Calculated hot risk: {total_risk} over {len(transactions)} transactions.")
    return total_risk


def watch_stream(
    db_ref: Any, collection_name: str, callback: Callable[[list[dict[str, Any]], Any, Any], None],
) -> Any:
    """Wraps db.collection(...).on_snapshot to provide real-time updates to the active session.
    Expects db_ref to be a mocked or live firestore.Client instance.
    """
    try:
        query = db_ref.collection(collection_name)

        def on_snapshot(col_snapshot, changes, read_time):
            # Map snapshot into explicit list of dicts for the callback
            docs = [doc.to_dict() for doc in col_snapshot]
            logger.info(f"Stream updated: received {len(docs)} documents at {read_time}")
            callback(docs, changes, read_time)

        # Start listening
        watch = query.on_snapshot(on_snapshot)
        logger.info(f"Successfully connected to realtime stream for '{collection_name}'")
        return watch

    except Exception as e:
        logger.error(f"Failed to initialize watch stream on collection {collection_name}: {e}")
        raise
