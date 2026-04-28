# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Forensic Index (Code: GLASS BOX)

Full-text compliance search engine for Judge 6 and ShadowTag.
Based on ArXiv 2510.09471 (Apertus Methodology).

Components:
- glass_box_indexer: Parquet → Elasticsearch pipeline
- es_config: Elasticsearch configuration (mmap disabled for HPC)
- pii_scrubber: Pre-index PII removal
"""

from .es_config import get_es_config
from .glass_box_indexer import GlassBoxIndexer
from .pii_scrubber import scrub_pii

__all__ = ["GlassBoxIndexer", "get_es_config", "scrub_pii"]
