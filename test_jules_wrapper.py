import os
import subprocess
import json

script_path = os.path.join(os.getcwd(), "scripts", "load_mcp_secrets.sh")
cmd = f"source {script_path} && env"
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable="/bin/bash")
stdout, _ = proc.communicate()
for line in stdout.decode().splitlines():
  if "=" in line:
    k, v = line.split("=", 1)
    os.environ[k] = v

import sys

sys.path.insert(0, os.path.join(os.getcwd(), "packages"))

from jules_orchestrator import JulesClient

client = JulesClient()
try:
  sources = client.list_sources()
  print("SUCCESS: Sources fetched")
  print(json.dumps(sources, indent=2))
except Exception as e:
  print("ERROR:", str(e))
