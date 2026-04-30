# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service import UserService


def process_user():
    svc = UserService()
    svc.get_user().save()
