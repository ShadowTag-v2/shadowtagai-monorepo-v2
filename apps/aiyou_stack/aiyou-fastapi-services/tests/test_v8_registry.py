# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from src.agents.v8_core import RiskLevel, TokenLedger


def test_risk_level_ordering():
    assert RiskLevel.LOW < RiskLevel.MEDIUM
    assert RiskLevel.MEDIUM < RiskLevel.HIGH
    assert RiskLevel.HIGH < RiskLevel.CRITICAL


def test_token_ledger():
    ledger = TokenLedger()
    ledger.add(1000, 1000)
    assert ledger.input_tokens == 1000
    assert ledger.output_tokens == 1000
    # Cost: (1000/1M * 3.5) + (1000/1M * 10.5) = 0.0035 + 0.0105 = 0.014
    assert abs(ledger.total_cost - 0.014) < 0.0001
