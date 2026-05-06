import os
import sys
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

sys.path.insert(0, os.path.join(os.getcwd(), "packages"))

from jules_orchestrator.client import JulesClient
from jules_orchestrator.session import JulesSession

client = JulesClient()
session = JulesSession(
    client=client,
    source_name="sources/github/ShadowTag-v2/Monorepo-Uphillsnowball",
    automation_mode="AUTO_CREATE_PR",
    task_description="Get the headfade landing page live. Deploy it to Firebase Hosting.",
)
try:
    print("Starting Jules session...")
    result = session.run_auto_pr_workflow(timeout=120, interval=5)
    print("Jules session finished:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print("ERROR:", str(e))
