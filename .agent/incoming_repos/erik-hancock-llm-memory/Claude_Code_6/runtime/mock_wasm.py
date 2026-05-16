# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

class ArrayBuffer:
    def __init__(self, size: int):
        self.size = size
        self.data = bytearray(size)


class WebAssemblyModule:
    def __init__(self, lib: bytes):
        self.lib = lib


class WebAssemblyInstance:
    def __init__(self, module: WebAssemblyModule):
        self.module = module
        self.exports = {"check_policy": lambda ptr, size: 1}  # Mock export


class WebAssemblyNamespace:
    Module = WebAssemblyModule
    Instance = WebAssemblyInstance


WebAssembly = WebAssemblyNamespace()
