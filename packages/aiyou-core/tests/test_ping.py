# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from importlib import import_module

_core = import_module("packages.aiyou-core")


def test_ping():
  assert _core.ping() == "pong"
