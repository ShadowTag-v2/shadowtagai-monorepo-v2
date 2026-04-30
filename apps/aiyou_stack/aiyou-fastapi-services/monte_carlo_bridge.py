import ctypes
import os

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), "libmidas_mc.so")
try:
    midas_lib = ctypes.CDLL(lib_path)

    # Define argument types: (double, double, double, int, int, double*, double*)
    midas_lib.run_monte_carlo.argtypes = [
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
    ]
    midas_lib.run_monte_carlo.restype = None
    HAS_MIDAS_C = True
    print("[Midas] Layer 7 C++ Fast Monte Carlo Engine Loaded Successfully.")
except Exception as e:
    HAS_MIDAS_C = False
    print(f"[!] Midas C++ load failed: {e}. Will fallback to python.")


def calculate_midas_risk(
    start_price: float,
    volatility: float,
    drift: float,
    steps: int = 252,
    simulations: int = 100000,
) -> dict:
    """Invokes the C++ Midas Monte Carlo simulator.
    Returns Quarter Kelly and 95% VaR (Value at Risk).
    """
    if not HAS_MIDAS_C:
        return {"error": "C++ Module Offline"}

    var95 = ctypes.c_double(0.0)
    kelly = ctypes.c_double(0.0)

    midas_lib.run_monte_carlo(
        start_price,
        volatility,
        drift,
        steps,
        simulations,
        ctypes.byref(var95),
        ctypes.byref(kelly),
    )

    return {
        "var_95": round(var95.value, 4),
        "quarter_kelly": round(kelly.value, 4),
        "simulations": simulations,
        "engine": "C++ Midas Layer 7",
    }


if __name__ == "__main__":
    # Test execution
    res = calculate_midas_risk(
        start_price=100.0,
        volatility=0.15,
        drift=0.08,
        steps=252,
        simulations=100000,
    )
    print(f"Midas Simulation Output: {res}")
