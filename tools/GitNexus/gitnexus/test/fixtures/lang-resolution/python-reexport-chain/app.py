# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models import User, Repo


def main():
    user = User()
    user.save()

    repo = Repo()
    repo.persist()
