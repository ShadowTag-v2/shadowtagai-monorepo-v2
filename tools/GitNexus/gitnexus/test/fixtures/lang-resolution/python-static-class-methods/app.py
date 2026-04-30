# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from service import UserService, AdminService


def process():
    UserService.find_user("alice")
    UserService.create_user("bob")
    UserService.from_config({})

    AdminService.find_user("charlie")
    AdminService.delete_user("charlie")
