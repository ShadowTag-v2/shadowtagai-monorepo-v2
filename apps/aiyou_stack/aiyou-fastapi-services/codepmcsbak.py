import glob
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime

# --- CONFIGURATION: SHADOWTAG-OMEGA-V2 ---
PROJECT_ID = os.getenv("PROJECT_ID", "shadowtag-omega-v2")
LOCATION = "us-central1"

# --- IMPORTS ---
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Tool, grounding
except ImportError:
    print("⚠️  Vertex AI missing. Install requirements.txt")
    sys.exit(1)

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:

    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = BLUE = ""

    class Style:
        RESET_ALL = ""


# ==============================================================================
# ⚔️  INTELLIGENCE: RISK & HISTORY
# ==============================================================================
class RiskLevel:
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


HAZARD_DATABASE = [
    {"pattern": "sk-", "severity": "I", "probability": "E", "name": "API Key Leak"},
    {"pattern": "ghp_", "severity": "I", "probability": "E", "name": "Github Key Leak"},
    {
        "pattern": "import non_existent",
        "severity": "II",
        "probability": "E",
        "name": "Hallucination",
    },
    {"pattern": "<TODO>", "severity": "III", "probability": "B", "name": "Incomplete Code"},
    {"pattern": "print(", "severity": "IV", "probability": "A", "name": "Debug Leftovers"},
]


class MissionLogger:
    def __init__(self, log_file="aar_log.json"):
        self.log_file = log_file
        self.webhook = os.getenv("JUDGE6_WEBHOOK_URL")

    def get_recent_failures(self, limit=3):
        """THE LEARNER: Retrieves recent failures to warn Gemini"""
        try:
            with open(self.log_file) as f:
                history = json.load(f)
            # Filter for failures/blocks
            failures = [h for h in history if h["outcome"] == "BLOCKED"]
            return failures[-limit:]
        except:
            return []

    def send_alert(self, target, hazards, risk):
        if not self.webhook:
            return
        payload = {
            "username": "JUDGE 6 OMEGA",
            "content": f"🚨 **ABORT** | `{target}` | Risk: {risk}\nHazards: {hazards}",
        }
        try:
            req = urllib.request.Request(
                self.webhook,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req)
        except:
            pass

    def log_mission(self, target, hazards, risk, outcome):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "hazards": [h["name"] for h in hazards],
            "risk": risk,
            "outcome": outcome,
        }
        try:
            with open(self.log_file) as f:
                h = json.load(f)
        except:
            h = []
        h.append(entry)
        with open(self.log_file, "w") as f:
            json.dump(h, f, indent=4)
        if outcome == "BLOCKED":
            self.send_alert(target, [x["name"] for x in hazards], risk)


# ==============================================================================
# ⚖️  JUDGE 6 SENTINEL (OMEGA UPGRADE)
# ==============================================================================
class JudgeSixSentinel:
    def __init__(self):
        self.logger = MissionLogger()
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.grounding = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
            self.model = GenerativeModel("gemini-1.5-pro-001")
            print(f"{Fore.GREEN}>>> 🌍 Vertex AI Grounding: ACTIVE ({PROJECT_ID}){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}>>> 📵 Auth Failed: {e}{Style.RESET_ALL}")
            self.model = None

    def ask_gemini(self, prompt, context=""):
        if not self.model:
            return ""

        # THE LEARNER: Inject past mistakes
        failures = self.logger.get_recent_failures()
        learning_context = ""
        if failures:
            learning_context = "AVOID PREVIOUS MISTAKES:\n" + "\n".join(
                [f"- {f['hazards']}" for f in failures],
            )

        full_prompt = f"""
        You are Judge 6 (Omega V2).
        TASK: {prompt}
        CONTEXT: {context}
        {learning_context}
        REQUIREMENT: Verify libraries via Grounding.
        OUTPUT: Return ONLY code.
        """
        try:
            print(f"{Fore.BLUE}>>> 📡 Gemini Generating (Grounded)...{Style.RESET_ALL}")
            response = self.model.generate_content(full_prompt, tools=[self.grounding])
            return response.text.replace("```python", "").replace("```", "").strip()
        except Exception:
            return ""

    def run_tests(self, file_path):
        """THE TESTER: Runs pytest if a matching test file exists"""
        test_file = f"tests/test_{os.path.basename(file_path)}"
        if not os.path.exists(test_file):
            print(
                f"{Fore.YELLOW}>>> ⚠️  No unit tests found for {file_path}. Skipping functional check.{Style.RESET_ALL}",
            )
            return True  # Pass by default if no tests, but warn

        print(f"{Fore.CYAN}>>> 🧪 Running Pytest on {test_file}...{Style.RESET_ALL}")
        result = subprocess.run(["pytest", test_file], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"{Fore.GREEN}>>> ✅ Tests Passed.{Style.RESET_ALL}")
            return True
        print(f"{Fore.RED}>>> ❌ Tests Failed:\n{result.stderr}{Style.RESET_ALL}")
        return False

    def assess_risk(self, code):
        matrix = {
            ("I", "E"): 2,
            ("II", "E"): 2,
            ("III", "B"): 2,
            ("IV", "A"): 1,
        }  # Simplified Matrix
        current, detected = 1, []
        for h in HAZARD_DATABASE:
            if h["pattern"] in code:
                # Default to High (3) if not in simplified matrix
                r = matrix.get((h["severity"], h["probability"]), 3)
                current = max(current, r)
                detected.append(h)
        return current, detected

    def execute_mission(self, file_path):
        if not os.path.exists(file_path):
            return
        with open(file_path) as f:
            content = f.read()

        # 1. GHOST WRITER
        if "???" in content:
            prompt = [l for l in content.split("\n") if "???" in l][0].replace("???", "").strip()
            content = self.ask_gemini(prompt, content)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"{Fore.GREEN}>>> 💾 Ghost Writer updated {file_path}{Style.RESET_ALL}")

        # 2. RISK AUDIT
        risk, hazards = self.assess_risk(content)

        # 3. MITIGATION (Auto-Scrub)
        if any(h["severity"] == "IV" for h in hazards):
            content = "\n".join([l for l in content.split("\n") if "print(" not in l])
            with open(file_path, "w") as f:
                f.write(content)
            risk = 1  # Downgrade risk after scrub
            print(f"{Fore.CYAN}>>> 🧹 Debugs scrubbed.{Style.RESET_ALL}")

        # 4. FUNCTIONAL TEST (The new check)
        tests_passed = self.run_tests(file_path)
        if not tests_passed:
            risk = RiskLevel.HIGH  # Fail risk if tests fail
            hazards.append({"name": "Unit Tests Failed", "severity": "II"})

        # 5. DEPLOYMENT
        if risk >= RiskLevel.HIGH:
            outcome = "BLOCKED"
            print(f"{Fore.RED}>>> 🛑 BLOCKED.{Style.RESET_ALL}")
        else:
            env = "production" if risk == 1 else "staging"
            outcome = f"DEPLOYED_{env.upper()}"
            print(f"{Fore.MAGENTA}>>> 🚀 Antigravity -> {env}{Style.RESET_ALL}")
            # subprocess.run(["./scripts/launch_antigravity.sh", env]) # Uncomment to enable actual push

        self.logger.log_mission(file_path, hazards, risk, outcome)


# ==============================================================================
# 👁️  THE ECONOMIST: SMART SCANNING
# ==============================================================================
def get_changed_files():
    """Returns only files changed in the last commit (or currently modified)"""
    try:
        # Check staged/modified files
        res = subprocess.check_output(["git", "diff", "--name-only", "HEAD"]).decode().splitlines()
        return [f for f in res if f.endswith(".py")]
    except:
        return glob.glob("*.py")  # Fallback to all


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    sentinel = JudgeSixSentinel()

    if target == ".":
        # SMART SCAN
        files = get_changed_files()
        print(f"{Fore.MAGENTA}>>> 👁️  Scanning {len(files)} changed files...{Style.RESET_ALL}")
        for f in files:
            if "codepmcs" not in f:
                sentinel.execute_mission(f)
    elif target == "--watch":
        # LOCAL MONKEY MODE (Requires 'pip install watchdog')
        print(">>> 🐒 Starting Local Monkey Watcher...")
        # Implementation of watchdog observer would go here
        # On Modified -> sentinel.execute_mission(event.src_path)
    else:
        sentinel.execute_mission(target)
