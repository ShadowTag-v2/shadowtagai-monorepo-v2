import numpy as np


def odor_sim(n=128, src=None, k=0.92, fx=0.02):
    if src is None:
        src = [(64, 64, 1.0)]
    f = np.zeros((n, n), float)
    for _ in range(256):
        nf = np.copy(f)
        # Simple diffusion
        nf[1:-1, 1:-1] = f[1:-1, 1:-1] * k + fx * (
            f[:-2, 1:-1] + f[2:, 1:-1] + f[1:-1, :-2] + f[1:-1, 2:]
        )
        for x, y, s in src:
            nf[x % n, y % n] += s
        f = nf
    return f.tolist()


def odor_score(f, mask=None):
    f_arr = np.array(f)
    if mask is None:
        return float(f_arr.mean())
    mask_arr = np.array(mask)
    return float((f_arr * mask_arr).mean())
