import random
import statistics as st


def mcarlo_rev(n, base, sd, yrs=5, gr=0.6):
    r = []
    for _ in range(n):
        b = max(0, random.gauss(base, sd))
        v = b * ((1 + gr) ** yrs)
        r.append(v)
    return r


def prc(x, p):
    x = sorted(x)
    i = int((len(x) - 1) * p)
    return x[i]


def mcarlo_val(n, rev_mult, rev_samples):
    out = [max(0, rev_mult * rv) for rv in rev_samples]
    if not out:
        return {"mean": 0, "p10": 0, "p50": 0, "p90": 0, "max": 0}
    return {
        "mean": st.mean(out),
        "p10": prc(out, 0.1),
        "p50": prc(out, 0.5),
        "p90": prc(out, 0.9),
        "max": max(out),
    }


def mcarlo_bundle(cfg):
    vals = []
    comps = {}
    for k, v in cfg.items():
        rs = mcarlo_rev(v["n"], v["base"], v["sd"], v.get("yrs", 5), v.get("gr", 0.6))
        vv = mcarlo_val(v["n"], v["mult"], rs)
        comps[k] = vv
        vals.append(vv["mean"])
    t = sum(vals)
    return {"components": comps, "sum_mean": t}
