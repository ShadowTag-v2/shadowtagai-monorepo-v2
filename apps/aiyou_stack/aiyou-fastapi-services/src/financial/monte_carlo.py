# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import random
import statistics as st

# DOCTRINE: Pnkln Vertex Rollup (Drive Artifact)
# SOURCE: pnkln_vertex_rollup.txt
# COMPONENT: pnkln-mcarlo


def mcarlo_rev(n, base, sd, yrs=5, gr=0.6):
    """Generates revenue projections based on Gaussian distribution.
    n: number of simulations
    base: base revenue
    sd: standard deviation
    yrs: years to project
    gr: growth rate
    """
    r = []
    for _ in range(n):
        b = max(0, random.gauss(base, sd))
        v = b * ((1 + gr) ** yrs)
        r.append(v)
    return r


def mcarlo_val(n, rev_mult, rev_samples):
    """Calculates valuation metrics from revenue samples."""
    out = [max(0, rev_mult * rv) for rv in rev_samples]
    return {
        "mean": st.mean(out),
        "p10": sorted(out)[int((len(out) - 1) * 0.1)],
        "p50": sorted(out)[int((len(out) - 1) * 0.5)],
        "p90": sorted(out)[int((len(out) - 1) * 0.9)],
        "max": max(out),
    }


def mcarlo_bundle(cfg):
    """Bundles multiple scenarios into a total valuation."""
    vals = []
    comps = {}
    for k, v in cfg.items():
        rs = mcarlo_rev(v["n"], v["base"], v["sd"], v.get("yrs", 5), v.get("gr", 0.6))
        vv = mcarlo_val(v["n"], v["mult"], rs)
        comps[k] = vv
        vals.append(vv["mean"])

    t = sum(vals)
    return {"components": comps, "sum_mean": t}


# Default Pnkln Configuration (from Drive)
PNKLN_SCENARIO = {
    "pnkln_core": {"n": 8000, "base": 120e6, "sd": 50e6, "gr": 0.55, "mult": 12},
    "pnkln_swiper": {"n": 8000, "base": 200e6, "sd": 90e6, "gr": 0.6, "mult": 13},
    "pnkln_geos": {"n": 8000, "base": 30e6, "sd": 20e6, "gr": 0.5, "mult": 22},
    "pnkln_odor": {"n": 8000, "base": 120e6, "sd": 60e6, "gr": 0.5, "mult": 10},
    "pnkln_verdict": {"n": 8000, "base": 120e6, "sd": 60e6, "gr": 0.55, "mult": 11},
    "pnkln_vcm": {"n": 8000, "base": 40e6, "sd": 20e6, "gr": 0.6, "mult": 11},
    "pnkln_tokable": {"n": 8000, "base": 80e6, "sd": 40e6, "gr": 0.55, "mult": 11},
}
