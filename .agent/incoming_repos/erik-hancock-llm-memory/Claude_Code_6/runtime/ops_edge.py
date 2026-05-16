# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .base import Allocator, Compiled, Compiler
from .mock_wasm import ArrayBuffer, WebAssembly


class EdgeBuffer:
    def __init__(self, heap: ArrayBuffer, ptr: int, size: int):
        self.heap = heap
        self.ptr = ptr
        self.size = size


class EdgeAllocator(Allocator):
    """ArrayBuffer allocation in Worker heap"""

    def __init__(self, heap_size_mb=64):
        self.heap = ArrayBuffer(heap_size_mb * 1024 * 1024)
        self.next_ptr = 0

    def alloc(self, size: int, options: any = None) -> EdgeBuffer:
        ptr = self.next_ptr
        self.next_ptr += size
        # Simple linear allocator for prototype, no free/fragmentation handling yet
        return EdgeBuffer(self.heap, ptr, size)

    def free(self, buf: EdgeBuffer) -> None:
        # No-op for linear allocator
        pass


def load_precompiled_wasm(src: str) -> bytes:
    # Mock loader
    return b"\x00\x61\x73\x6d"  # Magic bytes


class WASMCompiler(Compiler):
    """JR Engine DSL → WASM binary"""

    def compile(self, src: str) -> bytes:
        # TODO: Implement JR → WASM lowering
        # For now: Use precompiled WASM for testing
        return load_precompiled_wasm(src)


class WASMProgram:
    """Executable WASM module"""

    def __init__(self, device, name: str, lib: bytes):
        self.module = WebAssembly.Module(lib)
        self.instance = WebAssembly.Instance(self.module)
        # In a real scenario, we'd look up the export by name
        # For mock, we assume a standard entry point or the mock handles it
        self.check = self.instance.exports.get(name, lambda p, s: 1)

    def __call__(self, context_ptr, context_size):
        return self.check(context_ptr, context_size)


class EdgeDevice(Compiled):
    """CloudFlare Workers runtime"""

    def __init__(self, worker_url: str):
        super().__init__(
            device=worker_url,
            allocator=EdgeAllocator(),
            renderer=None,  # TODO: Hour 3-4
            compiler=WASMCompiler(),
            runtime=WASMProgram,
            graph=None,
        )
