# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service.app.adapters.authority_state import AuthorityState
from service.app.config import load_settings

s = load_settings()
authority = AuthorityState(s.authority_state_path).read()
