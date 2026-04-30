"""Vulture whitelist for CounselConduit API.

Marks FastAPI route handlers, Pydantic model fields, and pytest fixtures
that vulture would otherwise flag as unused at 90%+ confidence.
"""

# FastAPI route handlers — called by the ASGI framework, not directly
trigger_antigravity_swarm = None  # noqa: F841
health_check = None  # noqa: F841
stripe_webhook = None  # noqa: F841
gdpr_delete_schedule = None  # noqa: F841
gdpr_status = None  # noqa: F841
create_checkout = None  # noqa: F841
create_portal = None  # noqa: F841

# Pydantic model fields — serialized via model_dump
firm_id = None  # noqa: F841
session_id = None  # noqa: F841
tenant_id = None  # noqa: F841
billing_tier = None  # noqa: F841
webhook_secret = None  # noqa: F841
stripe_customer_id = None  # noqa: F841

# pytest fixtures — used via dependency injection
client = None  # noqa: F841
test_db = None  # noqa: F841
mock_stripe = None  # noqa: F841
