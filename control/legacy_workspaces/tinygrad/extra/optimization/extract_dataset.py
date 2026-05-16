#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
# extract asts from process replay artifacts
import os
from test.external.process_replay.process_replay import _pmap

LOGOPS = os.getenv("LOGOPS", "/tmp/sops")

def extract_ast(*args) -> None:
  open(LOGOPS, "a").write(str(args[1]).replace("\n", "").replace(" ", "")+"\n")
  return None

if __name__ == "__main__":
  _pmap({"get_program":extract_ast})
