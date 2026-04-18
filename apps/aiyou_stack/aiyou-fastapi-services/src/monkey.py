import json
import os
import sys
import traceback

import google.generativeai as genai
from dotenv import load_dotenv

# Load env vars (specifically the PROXY and API KEY)
load_dotenv()


def run_monkey(mission_id: str, objective: str):
    # 1. Routing (The Proxy Hook)
    # The proxy is running on localhost:8080 (defined in flake.nix)
    # We rely on requests/grpc respecting HTTP_PROXY env vars automatically.

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fail loud and fast if the fuel is missing
        raise ValueError("CRITICAL: No GEMINI_API_KEY found in environment.")

    genai.configure(api_key=api_key)

    # 2. The Model (Optimized for JSON)
    model = genai.GenerativeModel(
        "gemini-1.5-flash",
        generation_config={"response_mime_type": "application/json"},
    )

    # 3. The Protocol (Strict JSON)
    prompt = f"""
    ROLE: Sub-Agent (Flying Monkey).
    MISSION_ID: {mission_id}
    OBJECTIVE: {objective}

    EXECUTION_MODE: STRICT JSON.

    Perform the task. If it is code generation, include the code in the 'payload' field.
    If it is analysis, include the findings in 'analysis'.

    Output Schema:
    {{
        "id": "{mission_id}",
        "status": "success",
        "objective_hash": "{hash(objective)}",
        "payload": "string (code or raw text)",
        "analysis": {{ "key_findings": [], "risk_score": 0.0 }},
        "confidence": 0.99
    }}
    """

    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)  # Verify JSON integrity immediately

        # 4. The Artifact (The "Ream" we usually leave on the table)
        os.makedirs("artifacts", exist_ok=True)
        filename = f"artifacts/monkey_{mission_id}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        # Even death must be recorded structurallly
        err_filename = f"artifacts/monkey_{mission_id}_FATAL.json"
        with open(err_filename, "w") as f:
            json.dump(
                {
                    "id": mission_id,
                    "status": "fatal",
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                },
                f,
            )
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    run_monkey(sys.argv[1], " ".join(sys.argv[2:]))
