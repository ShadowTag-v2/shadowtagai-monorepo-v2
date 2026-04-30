# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import User


def process_user(user: User):
    user.address.save()
