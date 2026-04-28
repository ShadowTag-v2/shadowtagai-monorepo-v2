# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service.app.config import load_settings
from service.app.retrieval.sqlite_index import chunk_text

s = load_settings()
chunks = chunk_text(s.sqlite_db)
