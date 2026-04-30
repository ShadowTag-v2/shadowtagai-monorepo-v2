# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models.user import User
from models.repo import Repo


def process_entities():
    user = User("alice")
    repo = Repo("maindb")
    user.save()
    repo.save()
