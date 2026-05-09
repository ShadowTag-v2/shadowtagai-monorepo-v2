#!/usr/bin/env python3
"""Session Pin TTL Monitor (#15).

Monitors and cleans up expired session pins from in-memory and Firestore.
Run as a periodic Cloud Scheduler job or imported by the dispatch router.
"""

import logging
import time

logger = logging.getLogger("session_pin_monitor")


async def cleanup_session_pins_firestore() -> dict:
    """Clean up expired session pins from Firestore.

    Returns a report of actions taken.
    """
    deleted = 0
    errors = 0

    try:
        from google.cloud import firestore

        db = firestore.AsyncClient(project="shadowtag-omega-v4")
        now = time.time()
        ttl_seconds = 1800  # 30 min (matches SESSION_PIN_TTL_SECONDS)

        # Query for expired pins
        cutoff = now - ttl_seconds
        query = db.collection("session_pins").where("pinned_at", "<", cutoff)

        async for doc in query.stream():
            try:
                await doc.reference.delete()
                deleted += 1
            except Exception as e:
                logger.warning("Failed to delete expired pin %s: %s", doc.id, e)
                errors += 1

    except ImportError:
        logger.warning("Firestore not available")
    except Exception as e:
        logger.error("Session pin cleanup failed: %s", e)
        errors += 1

    report = {
        "deleted": deleted,
        "errors": errors,
        "timestamp": time.time(),
    }

    if deleted > 0:
        logger.info("Cleaned up %d expired session pins", deleted)

    return report


def cleanup_session_pins_memory() -> int:
    """Clean up expired session pins from in-memory cache.

    Returns count of evicted pins.
    """
    try:
        from apps.counselconduit.api.model_router import (
            SESSION_PIN_TTL_SECONDS,
            _session_pins,
        )
    except ImportError:
        try:
            from api.model_router import (  # type: ignore[no-redef]
                SESSION_PIN_TTL_SECONDS,
                _session_pins,
            )
        except ImportError:
            logger.warning("model_router not available")
            return 0

    now = time.time()
    expired = [sid for sid, (_, ts) in _session_pins.items() if now - ts > SESSION_PIN_TTL_SECONDS]
    for sid in expired:
        del _session_pins[sid]

    if expired:
        logger.info("Evicted %d expired in-memory session pins", len(expired))
    return len(expired)


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    # Run both memory and Firestore cleanup
    memory_count = cleanup_session_pins_memory()
    firestore_report = asyncio.run(cleanup_session_pins_firestore())

    print(f"Memory pins evicted: {memory_count}")
    print(f"Firestore pins deleted: {firestore_report['deleted']}")
    print(f"Errors: {firestore_report['errors']}")
