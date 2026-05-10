# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from models.user import User
from models.repo import Repo


class UserService:
  def process_users(self, users: list[User]):
    for user in self.users:
      user.save()


class RepoService:
  def process_repos(self, repos: list[Repo]):
    for repo in self.repos:
      repo.save()
