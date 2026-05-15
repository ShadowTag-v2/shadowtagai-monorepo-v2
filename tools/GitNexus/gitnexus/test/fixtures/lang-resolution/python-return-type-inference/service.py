# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import User


def get_user(name: str) -> User:
  return User(name)
