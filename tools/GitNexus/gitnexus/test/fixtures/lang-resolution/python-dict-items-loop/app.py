# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from user import User


def process(data: dict[str, User]):
    for _key, user in data.items():
        user.save()
