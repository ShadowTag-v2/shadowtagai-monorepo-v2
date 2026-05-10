import sys
import os
import json
import requests


def get_nanobanana_token():
  token = os.environ.get("NANO_BANANA_API_KEY")
  if not token:
    try:
      with open(".env") as f:
        for line in f:
          if line.startswith("NANO_BANANA_API_KEY="):
            return line.strip().split("=", 1)[1].strip("\"'")
    except FileNotFoundError:
      pass
  return token


def nano_banana_infer(endpoint, payload):
  token = get_nanobanana_token()
  base_url = os.environ.get(
    "NANO_BANANA_URL", "https://api.banana.dev/v1/run"
  )  # Fallback to generic if unconfigured

  headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

  try:
    response = requests.post(f"{base_url}/{endpoint}", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
  except Exception as e:
    print(f"API Error: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(e.response.text)
    sys.exit(1)


def main():
  if len(sys.argv) < 3:
    print("Usage: python3 my_nanobanana2.py --infer <model_key> '<json_payload>'")
    sys.exit(1)

  action = sys.argv[1]

  if action == "--infer":
    if len(sys.argv) < 4:
      print("Missing payload")
      sys.exit(1)

    model_key = sys.argv[2]
    payload_str = sys.argv[3]

    try:
      payload = json.loads(payload_str)
    except json.JSONDecodeError:
      print("ERROR: Could not parse JSON payload")
      sys.exit(1)

    result = nano_banana_infer(model_key, payload)
    print(json.dumps(result, indent=2))
  else:
    print(f"Unknown action: {action}")


if __name__ == "__main__":
  main()
