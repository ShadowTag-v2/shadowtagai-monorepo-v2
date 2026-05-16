# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from models import User


def create_user(name):
  return User(name)


admin = User("Admin")
guest = User("Guest")
