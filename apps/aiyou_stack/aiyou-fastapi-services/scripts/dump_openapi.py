# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import sys
from pathlib import Path

# Add root to python path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from fastapi.openapi.utils import get_openapi

    from apps.api.main import app

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    # Write to file
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print("Successfully generated openapi.json")

except Exception as e:
    print(f"Error generating OpenAPI schema: {e}")
    sys.exit(1)
