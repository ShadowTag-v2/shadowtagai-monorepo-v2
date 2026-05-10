# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import models


def main():
  user = models.User("alice")
  user.save()
  user.greet()
