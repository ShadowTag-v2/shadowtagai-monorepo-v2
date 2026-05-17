import sys
import os
import subprocess

script_path = os.path.join(os.getcwd(), "scripts", "load_mcp_secrets.sh")
cmd = f"source {script_path} && env"
proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable="/bin/bash")
stdout, _ = proc.communicate()
for line in stdout.decode().splitlines():
  if "=" in line:
    k, v = line.split("=", 1)
    os.environ[k] = v

sys.path.insert(0, os.path.join(os.getcwd(), "packages"))

from jules_orchestrator.client import JulesClient

client = JulesClient()
sources = client.list_sources()
print("Sources:")
print(sources)
