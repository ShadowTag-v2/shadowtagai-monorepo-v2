# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class UserService:
    @staticmethod
    def find_user(name: str) -> str:
        return name

    @staticmethod
    def create_user(name: str) -> str:
        return name

    @classmethod
    def from_config(cls, config: dict) -> "UserService":
        return cls()


class AdminService:
    @staticmethod
    def find_user(name: str) -> str:
        return name

    @staticmethod
    def delete_user(name: str) -> bool:
        return True
