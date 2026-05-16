# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import pexpect
import sys

child = pexpect.spawn("gemini extensions link pickle-rick-extension")
child.logfile = sys.stdout.buffer

try:
  child.expect("Do you want to continue\? \[Y/n\]:", timeout=10)
  child.sendline("Y")
  child.expect(pexpect.EOF, timeout=30)
except pexpect.TIMEOUT:
  print("Timeout")
  sys.exit(1)
