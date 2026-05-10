import asyncio
import sys
import os

# Add root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.bash_security import BashSecurityValidator
from src.services.secrets import SecretScanner
from src.utils.ssrf import SSRFGuard


async def main():
  print("--- Test 1: BashSecurityValidator (zmodload) ---")
  validator = BashSecurityValidator()
  try:
    validator.validate("echo 'hello'; zmodload zsh/net/tcp")
    print("❌ FAILED: zmodload was not blocked.")
  except ValueError as e:
    print(f"✅ PASSED: Blocked with error: {e}")

  print("\n--- Test 2: SecretScanner (Dummy Anthropic Key) ---")
  scanner = SecretScanner()
  dummy_key = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890"
  text = f"Here is my key: {dummy_key}"
  scanned = scanner.scan(text)
  if dummy_key not in scanned and "[REDACTED_API_KEY]" in scanned:
    print(f"✅ PASSED: Key was redacted -> {scanned}")
  else:
    print("❌ FAILED: Key was not properly redacted.")

  print("\n--- Test 3: SSRFGuard (AWS Metadata 169.254.169.254) ---")
  guard = SSRFGuard()
  # Note: SSRFGuard uses gethostbyname, which might fail or return itself for IPs.
  try:
    guard.resolve_and_verify("169.254.169.254")
    print("❌ FAILED: Metadata IP was not blocked.")
  except Exception as e:
    print(f"✅ PASSED: Blocked with error: {e}")


if __name__ == "__main__":
  asyncio.run(main())
