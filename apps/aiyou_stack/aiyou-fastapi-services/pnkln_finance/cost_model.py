import yaml


class PnklnCostEstimator:
    def __init__(self, path="pnkln_config/pricing.yaml"):
        self.tiers = yaml.safe_load(open(path))["pricing_tiers"]
        self.tiers.sort(
            key=lambda t: t["max_requests"] if t["max_requests"] is not None else 10**18
        )

    def estimate(self, n: int):
        total = 0
        rem = n
        prev = 0
        for t in self.tiers:
            maxn = t["max_requests"]
            base = t.get("base_cost", 0.0)
            per = t.get("cost_per_request", 0.0)
            use = rem if maxn is None else max(0, min(rem, maxn - prev))
            if use > 0:
                total += base + use * per
            rem -= use
            prev = maxn if maxn is not None else prev
            if rem <= 0:
                break
        return round(total, 2)


if __name__ == "__main__":
    est = PnklnCostEstimator()
    for k in [500, 1500, 10000, 15000, 25000]:
        print(k, est.estimate(k))
