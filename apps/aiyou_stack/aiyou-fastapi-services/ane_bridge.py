# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import ctypes
from pathlib import Path

# Locate the dylib compiled from third_party/ANE/bridge/
DYLIB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "third_party" / "ANE" / "bridge" / "libane_bridge.dylib"

if not DYLIB_PATH.exists():
    raise RuntimeError(f"ANE bridge library not found at: {DYLIB_PATH}. Run 'make' in third_party/ANE/bridge.")

# Load the library
_lib = ctypes.CDLL(str(DYLIB_PATH))


# Define opaque pointer for ANEKernelHandle
class ANEKernelHandle(ctypes.Structure):
    pass


# int ane_bridge_init(void);
_lib.ane_bridge_init.argtypes = []
_lib.ane_bridge_init.restype = ctypes.c_int

# ANEKernelHandle *ane_bridge_compile(const char *mil_text, size_t mil_len, ...);
_lib.ane_bridge_compile.argtypes = [
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_size_t),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_size_t),
]
_lib.ane_bridge_compile.restype = ctypes.POINTER(ANEKernelHandle)

# bool ane_bridge_eval(ANEKernelHandle *kernel);
_lib.ane_bridge_eval.argtypes = [ctypes.POINTER(ANEKernelHandle)]
_lib.ane_bridge_eval.restype = ctypes.c_bool

# void ane_bridge_write_input(ANEKernelHandle *kernel, int idx, const void *data, size_t bytes);
_lib.ane_bridge_write_input.argtypes = [ctypes.POINTER(ANEKernelHandle), ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t]
_lib.ane_bridge_write_input.restype = None

# void ane_bridge_read_output(ANEKernelHandle *kernel, int idx, void *data, size_t bytes);
_lib.ane_bridge_read_output.argtypes = [ctypes.POINTER(ANEKernelHandle), ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t]
_lib.ane_bridge_read_output.restype = None

# void ane_bridge_free(ANEKernelHandle *kernel);
_lib.ane_bridge_free.argtypes = [ctypes.POINTER(ANEKernelHandle)]
_lib.ane_bridge_free.restype = None


def init_bridge() -> bool:
    """Initialize ANE runtime."""
    if _lib.ane_bridge_init() != 0:
        raise RuntimeError("Failed to initialize ANE bridge framework.")
    return True


def compile_kernel(mil_text: str) -> ctypes.POINTER(ANEKernelHandle):
    """Compile an ANE kernel from MIL format."""
    mil_bytes = mil_text.encode("utf-8")
    kernel = _lib.ane_bridge_compile(mil_bytes, len(mil_bytes), None, 0, 0, None, 0, None)
    if not kernel:
        raise RuntimeError("ANE MIL Compilation Failed.")
    return kernel
