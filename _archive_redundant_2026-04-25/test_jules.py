import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from packages.jules_orchestrator.client import JulesClient


def test():
  client = JulesClient()
  sources = client.list_sources()
  print("Sources:", [s["name"] for s in sources])

  # Try creating session
  for s_name in [
    "github/ShadowTag-v2/Monorepo-Uphillsnowball",
    "sources/github/ShadowTag-v2/Monorepo-Uphillsnowball",
  ]:
    print(f"Testing create session with source: {s_name}")
    try:
      res = client.create_session(s_name, task_description="Test task")
      print("Success:", res)
      break
    except Exception as e:
      print("Failed:", e)


if __name__ == "__main__":
  test()
