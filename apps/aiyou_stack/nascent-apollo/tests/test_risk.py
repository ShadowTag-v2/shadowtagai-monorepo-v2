from libs.steel.sentinel import JudgeSixSentinel, RiskTier


def test_sentinel():
  sentinel = JudgeSixSentinel()

  # Test 1: Catastrophic Hazard
  print("\n[TEST 1] API Key Leak (Omega Context)")
  result, risk, _ = sentinel.vet_code_diff("main.py", "api_key = 'sk-12345'")
  assert risk == RiskTier.RED
  assert result is False

  # Test 2: Memory Suppression
  print("\n[TEST 2] Allowed Wildcard in Test")
  result, risk, _ = sentinel.vet_code_diff("tests/test_main.py", "from module import *")
  assert risk == RiskTier.GREEN
  assert result is True

  print("\n>>> ✅ SENTINEL TESTS PASSED")


if __name__ == "__main__":
  test_sentinel()
