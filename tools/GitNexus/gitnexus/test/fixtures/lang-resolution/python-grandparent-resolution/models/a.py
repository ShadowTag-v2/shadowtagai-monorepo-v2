# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .greeting import Greeting


class A:
    def greet(self) -> Greeting:
        return Greeting()
