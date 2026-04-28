# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# IN-MEMORY STORAGE (Replace with PostgreSQL in production)
# ================================================================================

# Storage dictionaries (TODO: Replace with SQLAlchemy ORM + PostgreSQL)
videos_db: dict[str, dict] = {}
products_db: dict[str, dict] = {}
product_overlays_db: dict[str, dict] = {}
persuasion_points_db: dict[str, dict] = {}
users_db: dict[str, dict] = {}
interactions_db: list[dict] = []
retailers_db: dict[str, dict] = {}
analytics_db: dict[str, dict] = {}


# ================================================================================
