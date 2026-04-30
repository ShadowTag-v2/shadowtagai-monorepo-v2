# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import User


def process():
    user = User("alice")
    user.save()
