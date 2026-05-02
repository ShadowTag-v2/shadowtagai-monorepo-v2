import argparse
import os
import sys

# Add path to find modules in ShadowTag-Omega/libs
# Assuming we run this from ShadowTag-Omega root
sys.path.append(os.path.join(os.getcwd(), "libs"))

from agents.gemini_code_assist_proxy import GeminiCodeAssistProxy
from governance.judge_six_pipeline import JudgeSix


def run_suggestion_loop(user_prompt: str, project_id: str):
    print(f"--- Antigravity Loop Initiated (Project: {project_id}) ---")
    print(f"Goal: {user_prompt}")

    # 1. Initialize Agents
    proxy = GeminiCodeAssistProxy(project_id=project_id)
    judge = JudgeSix()

    # 2. Get Suggestion
    print("\n[1/3] Calling Gemini Code Assist Proxy...")
    suggestion_data = proxy.generate_suggestion(user_prompt)

    suggestion_text = ""
    if isinstance(suggestion_data, dict):
        if suggestion_data.get("action_type") == "mock_error":
            print(f"\n⚠️  {suggestion_data['explanation']}")
            suggestion_text = suggestion_data["code"]
        else:
            suggestion_text = str(suggestion_data)
    else:
        suggestion_text = str(suggestion_data)

    print("\n[2/3] Generated Suggestion:")
    print("-" * 40)
    print(suggestion_text[:500] + "..." if len(suggestion_text) > 500 else suggestion_text)
    print("-" * 40)

    # 3. Governance Check
    print("\n[3/3] Summoning Judge 6...")
    verdict = judge.evaluate(user_prompt, suggestion_text)

    if isinstance(verdict, tuple):
        approved, reason = verdict
    else:
        approved = False
        reason = str(verdict)

    if approved:
        print("\n✅ VERDICT: APPROVED")
        print("Reason: " + reason)
    else:
        print("\n🚫 VERDICT: REJECTED")
        print("Reason: " + reason)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Suggestion Loop")
    parser.add_argument("prompt", type=str, help="The coding task or question")
    parser.add_argument("--project", type=str, default=os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2"), help="GCP Project ID")

    args = parser.parse_args()

    run_suggestion_loop(args.prompt, args.project)
