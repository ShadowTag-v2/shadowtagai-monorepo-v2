# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class Repo:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def save(self) -> bool:
        return False
