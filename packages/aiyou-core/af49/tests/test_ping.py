# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from aiyou_core import ping


def test_ping():
  assert ping() == "pong"
