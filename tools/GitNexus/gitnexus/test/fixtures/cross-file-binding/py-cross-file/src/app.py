# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import get_user


def run():
    u = get_user()
    u.save()
    u.get_name()
