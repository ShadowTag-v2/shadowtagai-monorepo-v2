# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models.user import User


def process(x):
    match x:
        case User() as u:
            u.save()  # should resolve to User#save, not Repo#save
