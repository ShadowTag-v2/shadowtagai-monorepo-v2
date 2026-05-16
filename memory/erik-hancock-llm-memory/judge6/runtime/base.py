# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from typing import Any


class Buffer:
  def __init__(self, device: str, size: int, dtype: Any, opaque: Any = None):
    self.device = device
    self.size = size
    self.dtype = dtype
    self.opaque = opaque


class Allocator:
  def alloc(self, size: int, options: Any = None) -> Any:
    raise NotImplementedError

  def free(self, buf: Any) -> None:
    raise NotImplementedError


class Compiler:
  def __init__(self, cachekey: str | None = None):
    self.cachekey = cachekey

  def compile(self, src: str) -> bytes:
    raise NotImplementedError


class Compiled:
  def __init__(
    self,
    device: str,
    allocator: Allocator,
    renderer: Any,
    compiler: Compiler,
    runtime: Any,
    graph: Any = None,
  ):
    self.device = device
    self.allocator = allocator
    self.renderer = renderer
    self.compiler = compiler
    self.runtime = runtime
    self.graph = graph

  def synchronize(self):
    pass
