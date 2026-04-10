import asyncio
import logging
import os

from agents.codemender import CodeMenderAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CodeMenderVerifier")


async def main():
    print("🧪 Starting CodeMender verification...")

    # 1. Create Vulnerable File
    vuln_file = "tests/fixtures/vulnerable_demo.py"
    os.makedirs(os.path.dirname(vuln_file), exist_ok=True)

    vuln_code = """
def check_password(input_password):
    # SECURITY ISSUE: Hardcoded password
    if input_password == "[VAPORIZED_PWD]":
        return True
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and check_password(sys.argv[1]):
        print("Access Granted")
        sys.exit(0)
    else:
        print("Access Denied")
        sys.exit(1)
"""
    with open(vuln_file, "w") as f:
        f.write(vuln_code)

    print(f"📄 Created vulnerable file: {vuln_file}")

    # 2. Initialize Agent
    agent = CodeMenderAgent()
    if not agent.think_model:
        print("⚠️  Skipping test: No Gemini credentials found.")
        return

    # 3. run resolve_issue
    # We want to replace hardcoded password with an env var check
    issue = "Hardcoded password found. Replace it with os.getenv('App_PASSWORD') check."
    # Actually, the agent runs the test cmd TO VERIFY.
    # If the patch works, it should pass whatever test we give.
    # But wait, if we change the logic to env var, we need to provide the env var during test.
    # Let's verify SYNTAX first, passing None as test_cmd to skip execution loop, or a simple syntax check.

    print(f"🤖 Agent analyzing issue: '{issue}'")
    result = await agent.resolve_issue(vuln_file, issue, test_command=None)

    # 4. output results
    print("\n✅ Verification Result:")
    print(f"Status: {result['status']}")
    print(f"Root Cause: {result.get('root_cause')}")
    print("-" * 40)
    print(f"Patch:\n{result.get('patch')}")
    print("-" * 40)

    # Cleanup
    # os.remove(vuln_file)


if __name__ == "__main__":
    asyncio.run(main())
