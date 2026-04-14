from dataclasses import dataclass


@dataclass
class ContractRequest:
    client_type: str  # "Actor", "Coach", "manager"
    contract_text: str
    proposed_compensation: float
    market_benchmark: float
    clauses: list[str]


@dataclass
class ContractReview:
    score: int  # 0-100
    is_fair: bool
    red_flags: list[str]
    negotiation_leverage: list[str]
    judge_verdict: str


class ContractJudge:
    """Judge #6 Domain Judge: Law (Representation).
    Reviews contracts for fairness, compliance, and leverage.
    """

    def __init__(self):
        self.risk_threshold = 70
        # Simple keyword heuristics for prototype
        self.bad_clauses = [
            "perpetuity",
            "unlimited liability",
            "work for hire without royalty",
            "non-compete > 1 year",
            "arbitration only",
        ]
        self.good_clauses = [
            "gross revenue participation",
            "backend",
            "cut of merchandise",
            "guaranteed bonus",
            "performance kicker",
        ]

    def review_contract(self, request: ContractRequest) -> ContractReview:
        """AI Agent Logic: "Would a human shark sign this?"
        """
        red_flags = []
        leverage_points = []
        score = 85  # Start high, deduct for bad, add for good

        # 1. Compensation Check
        if request.proposed_compensation < request.market_benchmark * 0.9:
            diff = round((1 - request.proposed_compensation / request.market_benchmark) * 100)
            red_flags.append(f"LOWBALL: Offer is {diff}% below market benchmark.")
            score -= 15
        elif request.proposed_compensation > request.market_benchmark * 1.2:
            leverage_points.append("STRONG OFFER: Comp is above market.")
            score += 5

        # 2. Clause Analysis
        text_lower = request.contract_text.lower()
        for bad in self.bad_clauses:
            if bad in text_lower:
                red_flags.append(f"TOXIC CLAUSE: Found '{bad}'.")
                score -= 20

        for good in self.good_clauses:
            if good in text_lower:
                leverage_points.append(f"WIN: Found '{good}'.")
                score += 10

        # 3. Verdict
        is_fair = score >= self.risk_threshold
        verdict = "SIGN" if is_fair else "NEGOTIATE"
        if score < 50:
            verdict = "WALK AWAY"

        return ContractReview(
            score=max(0, min(100, score)),
            is_fair=is_fair,
            red_flags=red_flags,
            negotiation_leverage=leverage_points,
            judge_verdict=verdict,
        )


# Example Usage
if __name__ == "__main__":
    judge = ContractJudge()
    req = ContractRequest(
        client_type="Actor",
        contract_text="Terms: Rights granted in perpetuity. No backend participation.",
        proposed_compensation=50000,
        market_benchmark=80000,
        clauses=[],
    )
    result = judge.review_contract(req)
    print(f"Verdict: {result.judge_verdict} (Score: {result.score})")
    print(f"Flags: {result.red_flags}")
