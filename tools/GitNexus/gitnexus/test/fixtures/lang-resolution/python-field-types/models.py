# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.


class Address:
  city: str

  def save(self):
    pass


class User:
  name: str
  address: Address

  def greet(self) -> str:
    return self.name
