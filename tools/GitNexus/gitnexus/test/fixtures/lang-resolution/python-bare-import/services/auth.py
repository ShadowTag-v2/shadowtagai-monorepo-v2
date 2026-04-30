# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import user


def authenticate():
    svc = user.UserService()
    svc.execute()
