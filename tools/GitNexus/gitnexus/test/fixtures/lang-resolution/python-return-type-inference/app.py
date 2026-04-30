# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service import get_user


def process_user():
    user = get_user("alice")
    user.save()
