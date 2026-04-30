# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import User


def process():
    if user := User("alice"):
        user.save()
