# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import inspect

from google.adk.tools.mcp_tool import mcp_session_manager

print("Classes in mcp_session_manager:")
for name, obj in inspect.getmembers(mcp_session_manager):
    if inspect.isclass(obj):
        print(name)
