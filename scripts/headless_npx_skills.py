import pexpect
import sys

child = pexpect.spawn(
  "npx --yes skills add vercel-labs/skills --skill find-skills", encoding="utf-8"
)
child.logfile = sys.stdout

try:
  child.expect("Which agents do you want to install to", timeout=60)
  child.sendline("\r\n")
  child.expect(pexpect.EOF, timeout=120)
except pexpect.TIMEOUT:
  print("Timeout waiting for prompt")
  sys.exit(1)
except Exception as e:
  print(f"Error: {e}")
  sys.exit(1)
