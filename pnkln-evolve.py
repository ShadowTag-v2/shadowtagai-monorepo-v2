# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Neurosymbolic Core Engine
def strict_format(output_str: str) -> str:
    # 486 branch point simulation
    if "error" in output_str.lower():
        return "SYS_ERROR_HANDLED"
    return "SYS_OK"
