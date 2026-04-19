"""ane_bridge.py — Python ctypes wrapper for libane_bridge.dylib (Pickle Rick)

Wraps the C-callable ANE bridge into a Pythonic API.
Call via zero_cpu_router.dispatch_compute() — do NOT call this directly.

Build requirement:
    cd third_party/ANE/bridge && make clean && make
"""

from __future__ import annotations

import ctypes
import logging
import pathlib
from ctypes import (
    POINTER,
    c_bool,
    c_char_p,
    c_float,
    c_int,
    c_size_t,
    c_uint8,
    c_void_p,
)

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Resolve dylib path
# ---------------------------------------------------------------------------
_DYLIB_NAME = "libane_bridge.dylib"
_BRIDGE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent.parent / "third_party" / "ANE" / "bridge"
)
_DYLIB_PATH = _BRIDGE_DIR / _DYLIB_NAME

_lib: ctypes.CDLL | None = None
_initialized = False


def _load_lib() -> ctypes.CDLL:
    """Load the ANE bridge dylib lazily."""
    global _lib
    if _lib is not None:
        return _lib
    if not _DYLIB_PATH.exists():
        raise FileNotFoundError(
            f"ANE bridge dylib not found at {_DYLIB_PATH}. "
            f"Run: cd {_BRIDGE_DIR} && make clean && make"
        )
    _lib = ctypes.CDLL(str(_DYLIB_PATH))
    _setup_signatures(_lib)
    return _lib


def _setup_signatures(lib: ctypes.CDLL) -> None:
    """Declare C function signatures for type safety."""
    # int ane_bridge_init(void)
    lib.ane_bridge_init.restype = c_int
    lib.ane_bridge_init.argtypes = []

    # ANEKernelHandle *ane_bridge_compile(...)
    lib.ane_bridge_compile.restype = c_void_p
    lib.ane_bridge_compile.argtypes = [
        c_char_p,  # mil_text
        c_size_t,  # mil_len
        POINTER(c_uint8),  # weight_data
        c_size_t,  # weight_len
        c_int,  # n_inputs
        POINTER(c_size_t),  # input_sizes
        c_int,  # n_outputs
        POINTER(c_size_t),  # output_sizes
    ]

    # bool ane_bridge_eval(ANEKernelHandle *kernel)
    lib.ane_bridge_eval.restype = c_bool
    lib.ane_bridge_eval.argtypes = [c_void_p]

    # void ane_bridge_write_input(ANEKernelHandle *k, int idx, void *data, size_t bytes)
    lib.ane_bridge_write_input.restype = None
    lib.ane_bridge_write_input.argtypes = [c_void_p, c_int, c_void_p, c_size_t]

    # void ane_bridge_read_output(ANEKernelHandle *k, int idx, void *data, size_t bytes)
    lib.ane_bridge_read_output.restype = None
    lib.ane_bridge_read_output.argtypes = [c_void_p, c_int, c_void_p, c_size_t]

    # void ane_bridge_free(ANEKernelHandle *kernel)
    lib.ane_bridge_free.restype = None
    lib.ane_bridge_free.argtypes = [c_void_p]

    # int ane_bridge_get_compile_count(void)
    lib.ane_bridge_get_compile_count.restype = c_int
    lib.ane_bridge_get_compile_count.argtypes = []

    # void ane_bridge_reset_compile_count(void)
    lib.ane_bridge_reset_compile_count.restype = None
    lib.ane_bridge_reset_compile_count.argtypes = []

    # uint8_t *ane_bridge_build_weight_blob(float *src, int rows, int cols, size_t *out_len)
    lib.ane_bridge_build_weight_blob.restype = POINTER(c_uint8)
    lib.ane_bridge_build_weight_blob.argtypes = [
        POINTER(c_float),
        c_int,
        c_int,
        POINTER(c_size_t),
    ]

    # uint8_t *ane_bridge_build_weight_blob_quantized(float *src, rows, cols, float *out_scale, size_t *out_len)
    lib.ane_bridge_build_weight_blob_quantized.restype = POINTER(c_uint8)
    lib.ane_bridge_build_weight_blob_quantized.argtypes = [
        POINTER(c_float),
        c_int,
        c_int,
        POINTER(c_float),
        POINTER(c_size_t),
    ]

    # Note: no ane_bridge_free_blob in C — blobs are malloc'd, freed via libc


# ---------------------------------------------------------------------------
# Public Python API
# ---------------------------------------------------------------------------


def init_bridge() -> bool:
    """Initialize the ANE runtime. Returns True on success."""
    global _initialized
    if _initialized:
        return True
    lib = _load_lib()
    ret = lib.ane_bridge_init()
    if ret != 0:
        logger.error("[ANE] ane_bridge_init() failed with code %d", ret)
        return False
    _initialized = True
    logger.info("[ANE] Bridge initialized (Pickle Rick online).")
    return True


def compile_kernel(
    mil_text: str | bytes,
    weights: np.ndarray | None = None,
    n_inputs: int = 1,
    input_sizes: list[int] | None = None,
    n_outputs: int = 1,
    output_sizes: list[int] | None = None,
) -> int | None:
    """Compile a MIL program into an ANE kernel.

    Args:
        mil_text: MIL program text (UTF-8 string or bytes).
        weights: Optional float32 numpy array of weights.
        n_inputs: Number of input tensors.
        input_sizes: Byte sizes for each input tensor.
        n_outputs: Number of output tensors.
        output_sizes: Byte sizes for each output tensor.

    Returns:
        Opaque kernel handle (int pointer), or None on failure.
    """
    lib = _load_lib()

    mil_bytes = mil_text.encode("utf-8") if isinstance(mil_text, str) else mil_text

    mil_len = len(mil_bytes)

    # Weight data
    if weights is not None:
        weights_f32 = np.ascontiguousarray(weights, dtype=np.float32)
        weight_ptr = weights_f32.ctypes.data_as(POINTER(c_uint8))
        weight_len = weights_f32.nbytes
    else:
        weight_ptr = ctypes.cast(None, POINTER(c_uint8))
        weight_len = 0

    # Input/output sizes
    if input_sizes is None:
        input_sizes = [1024] * n_inputs
    if output_sizes is None:
        output_sizes = [1024] * n_outputs

    in_arr = (c_size_t * n_inputs)(*input_sizes)
    out_arr = (c_size_t * n_outputs)(*output_sizes)

    handle = lib.ane_bridge_compile(
        mil_bytes,
        mil_len,
        weight_ptr,
        weight_len,
        n_inputs,
        in_arr,
        n_outputs,
        out_arr,
    )

    if handle is None or handle == 0:
        logger.error("[ANE] compile_kernel failed")
        return None

    logger.info("[ANE] Kernel compiled (handle=%d)", handle)
    return handle


def evaluate(kernel_handle: int) -> bool:
    """Run a compiled kernel on the ANE. Returns True on success."""
    lib = _load_lib()
    return bool(lib.ane_bridge_eval(kernel_handle))


def write_input(kernel_handle: int, idx: int, data: np.ndarray) -> None:
    """Write data to a kernel input tensor."""
    lib = _load_lib()
    buf = np.ascontiguousarray(data)
    lib.ane_bridge_write_input(kernel_handle, idx, buf.ctypes.data, buf.nbytes)


def read_output(
    kernel_handle: int, idx: int, shape: tuple, dtype: np.dtype = np.float16
) -> np.ndarray:
    """Read data from a kernel output tensor."""
    lib = _load_lib()
    out = np.empty(shape, dtype=dtype)
    lib.ane_bridge_read_output(kernel_handle, idx, out.ctypes.data, out.nbytes)
    return out


def free_kernel(kernel_handle: int) -> None:
    """Free a compiled kernel and all associated resources."""
    lib = _load_lib()
    lib.ane_bridge_free(kernel_handle)


def build_weight_blob(weights: np.ndarray) -> tuple[bytes, int]:
    """Build an ANE-format weight blob from float32 weights.

    Returns:
        (blob_bytes, blob_length) tuple.
    """
    lib = _load_lib()
    w = np.ascontiguousarray(weights.flatten(), dtype=np.float32)
    rows, cols = weights.shape if weights.ndim == 2 else (1, weights.size)
    out_len = c_size_t(0)
    ptr = lib.ane_bridge_build_weight_blob(
        w.ctypes.data_as(POINTER(c_float)),
        rows,
        cols,
        ctypes.byref(out_len),
    )
    blob = bytes(ctypes.cast(ptr, POINTER(c_uint8 * out_len.value)).contents)
    # Free malloc'd C memory via libc
    _libc = ctypes.CDLL(None)
    _libc.free(ptr)
    return blob, out_len.value


def build_weight_blob_quantized(weights: np.ndarray) -> tuple[bytes, float, int]:
    """Build a quantized int8 ANE weight blob with symmetric quantization.

    Returns:
        (blob_bytes, scale, blob_length) tuple.
    """
    lib = _load_lib()
    w = np.ascontiguousarray(weights.flatten(), dtype=np.float32)
    rows, cols = weights.shape if weights.ndim == 2 else (1, weights.size)
    out_len = c_size_t(0)
    out_scale = c_float(0.0)
    ptr = lib.ane_bridge_build_weight_blob_quantized(
        w.ctypes.data_as(POINTER(c_float)),
        rows,
        cols,
        ctypes.byref(out_scale),
        ctypes.byref(out_len),
    )
    blob = bytes(ctypes.cast(ptr, POINTER(c_uint8 * out_len.value)).contents)
    # Free malloc'd C memory via libc
    _libc = ctypes.CDLL(None)
    _libc.free(ptr)
    return blob, out_scale.value, out_len.value


def get_compile_count() -> int:
    """Get the number of kernels compiled since last reset."""
    lib = _load_lib()
    return lib.ane_bridge_get_compile_count()


def reset_compile_count() -> None:
    """Reset the compile counter."""
    lib = _load_lib()
    lib.ane_bridge_reset_compile_count()
