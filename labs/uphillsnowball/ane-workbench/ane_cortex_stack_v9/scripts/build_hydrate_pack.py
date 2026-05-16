# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json

import requests

resp = requests.get("http://127.0.0.1:8090/api/hydrate-pack", timeout=30)
resp.raise_for_status()
print(json.dumps(resp.json(), indent=2))
