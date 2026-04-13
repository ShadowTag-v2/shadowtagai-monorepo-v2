import requests
import json

resp = requests.get("http://127.0.0.1:8090/api/hydrate-pack", timeout=30)
resp.raise_for_status()
print(json.dumps(resp.json(), indent=2))
