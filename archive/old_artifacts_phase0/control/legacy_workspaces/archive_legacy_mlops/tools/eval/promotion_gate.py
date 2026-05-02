#!/usr/bin/env python3
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
POLICY = ROOT / "policy" / "config" / "strict_policy.yml"
EVAL = ROOT / ".ci" / "offline_eval.json"


def main():
    if not POLICY.exists() or not EVAL.exists():
        print("[GATE] policy or eval missing")
        sys.exit(1)
    pol = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    res = json.loads(EVAL.read_text(encoding="utf-8"))
    min_uplift = float(pol["promotion_thresholds"]["eval_uplift_min_pct"]) if pol else 999
    ok = float(res.get("uplift_pct", 0.0)) >= min_uplift
    print(f"[GATE] uplift={res.get('uplift_pct')}% min={min_uplift}% -> {'PASS' if ok else 'BLOCK'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
