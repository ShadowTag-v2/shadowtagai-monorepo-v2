from google.adk import Agent
from google.adk.models import Gemini as ModelArgs

# Define the Judge 6 Persona
JUDGE_SIX_PROMPT = """
You are Judge 6, the Sovereign Governance Engine of ShadowTag Omega.
Your role is to evaluate requests for "Wet Fleece" (High Risk) vs "Dry Ground" (Safe).
You output verdicts in a strict format.
You are now connected via AG-UI (The Walkie-Talkie).
Respond to user queries with your verdict.
"""


# Initialize the Native ADK Agent
# We use a simple model configuration for now (Gemini or Mock)
# Since we don't have the full ADK config loaded, we'll create a base agent.
class JudgeSixAgent(Agent):
    prompt: str = JUDGE_SIX_PROMPT

    def __init__(self):
        # Configure the Brain (Gemini 1.5 Pro)
        model = ModelArgs(model_name="gemini-3.1-flash-lite-preview")
        # ALIAS: Naming it 'default' ensures CopilotKit frontend connects automatically
        super().__init__(name="default", model=model, prompt=JUDGE_SIX_PROMPT)

    def process(self, context):
        # Determine Verdict
        query = context.get_last_message_text()
        verdict = "DRY GROUND" if "safe" in query.lower() else "WET FLEECE (Review Required)"

        # Emit AG-UI compatible response (ADK handles this via the adapter)
        return (
            f"⚖️ **JUDGE 6 VERDICT**\n\nQuery: {query}\nVerdict: {verdict}\n\n_Sovereign Authority_"
        )


from src.governance.judge_six.risk_router import JudgeSixRouter, RiskLevel

# Export the agent instance for main.py
root_agent = JudgeSixAgent()


# Sovereign Compatibility Wrapper
class JudgeSixEngine:
    def __init__(self):
        self.router = JudgeSixRouter()

    def execute_mission(self, mission_id, context, risk_tier, query):
        print(f"⚖️ JUDGE 6: Evaluating Mission {mission_id}")

        # 1. Evaluate Risk via Router (The Law Library)
        # We start at iteration 1 for new requests.
        judgment = self.router.evaluate(query, mission_id=mission_id, iteration=1)

        print(f"   Verdict: {judgment.verdict}")
        print(f"   Reason: {judgment.reason}")

        return LegacyVerdict(
            approved=(judgment.verdict == RiskLevel.GREEN),
            risk_tier=judgment.verdict,
            shadowtag_hash=f"SHA:{mission_id}:{judgment.verdict}",
            authority="JUDGE_6_OMEGA",
        )


class LegacyVerdict:
    def __init__(self, approved, risk_tier, shadowtag_hash, authority):
        self.approved = approved
        self.risk_tier = risk_tier
        self.shadowtag_hash = shadowtag_hash
        self.authority = authority
