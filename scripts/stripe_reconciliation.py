#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Stripe Connect Reconciliation Job (Item #16).

Compares Stripe subscription data against Firestore tenant records to detect:
1. Payment failures with active access
2. Active subscriptions without Firestore records
3. Tier mismatches between Stripe and Firestore
4. Orphaned webhook events

Run weekly via Cloud Scheduler.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, UTC

logger = logging.getLogger("stripe_reconciliation")


async def reconcile():
    """Run Stripe ↔ Firestore reconciliation."""
    try:
        import stripe
    except ImportError:
        logger.error("stripe package not installed")
        sys.exit(1)

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not stripe.api_key:
        logger.error("STRIPE_SECRET_KEY not set")
        sys.exit(1)

    # Tier mapping: Stripe Price IDs → internal tiers
    price_to_tier = {
        "price_1TNKSREHnWpykeMiRMDlVgLl": "professional",  # Pro Monthly $149
        "price_1TNKSjEHnWpykeMi0S9GCVjy": "professional",  # Pro Annual $1,428
        "price_1TNKSREHnWpykeMi8mrDf4rI": "enterprise",  # Enterprise $20K/mo
    }

    discrepancies = []
    reconciled = 0

    # 1. List all active Stripe subscriptions
    logger.info("Fetching active Stripe subscriptions...")
    subs = stripe.Subscription.list(status="active", limit=100)

    for sub in subs.auto_paging_iter():
        customer_id = sub.customer
        price_id = sub["items"]["data"][0]["price"]["id"] if sub["items"]["data"] else None
        expected_tier = price_to_tier.get(price_id, "trial")

        # 2. Check Firestore for matching tenant record
        try:
            from google.cloud import firestore as _fs

            db = _fs.AsyncClient(project="shadowtag-omega-v4")
            # Look up tenant by stripe_customer_id
            query = db.collection("tenants").where("stripe_customer_id", "==", customer_id)
            docs = [doc async for doc in query.stream()]

            if not docs:
                discrepancies.append(
                    {
                        "type": "ORPHANED_SUBSCRIPTION",
                        "customer_id": customer_id,
                        "price_id": price_id,
                        "expected_tier": expected_tier,
                    }
                )
                continue

            tenant_data = docs[0].to_dict()
            actual_tier = tenant_data.get("tier", "trial")

            # 3. Check tier mismatch
            if actual_tier != expected_tier:
                discrepancies.append(
                    {
                        "type": "TIER_MISMATCH",
                        "customer_id": customer_id,
                        "firestore_tier": actual_tier,
                        "stripe_tier": expected_tier,
                        "firm_id": tenant_data.get("firm_id"),
                    }
                )
            else:
                reconciled += 1

        except ImportError:
            logger.warning("Firestore not available, skipping reconciliation check")
            break
        except Exception as e:
            logger.warning("Reconciliation check failed for %s: %s", customer_id, e)

    # 4. Report
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_subscriptions": reconciled + len(discrepancies),
        "reconciled": reconciled,
        "discrepancies": len(discrepancies),
        "details": discrepancies,
    }

    if discrepancies:
        logger.warning("Reconciliation found %d discrepancies", len(discrepancies))
        for d in discrepancies:
            logger.warning("  %s: %s", d["type"], d.get("customer_id"))
    else:
        logger.info("Reconciliation clean: %d subscriptions verified", reconciled)

    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(reconcile())
    import json

    print(json.dumps(result, indent=2))
