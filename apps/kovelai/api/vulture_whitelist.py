# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Vulture whitelist for kovelai API
# These items are false positives — used by Pydantic models or function signatures.
#
# The `fee_type` parameter is used in the function signature of route_advance_fee()
# and documented in docstrings. Vulture flags it because it's not used inside the
# function body, but it's part of the public API contract and will be used
# when additional fee type routing logic is implemented.

fee_type  # route_advance_fee() parameter — public API contract  # noqa: B018, F821
