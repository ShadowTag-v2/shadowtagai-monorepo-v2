# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import subprocess

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

# BLOCK 3: The Tools
# "The Hands of the King"


def bash_exec(command: str):
    """Executes a bash command safely.
    Includes Judge 6 Guardrails.
    """
    # Safety Check: Judge 6 Logic
    if "rm -rf" in command:
        print(f"🚫 BLOCKED BASH COMMAND: {command}")
        return {"error": "Blocked by Judge 6: High Risk Destructive Command"}

    try:
        print(f"⚡ Executing Shell: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out after 30s"}
    except Exception as e:
        return {"error": str(e)}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def jetski_browse(url: str):
    """High-Speed Extraction using JetSki logic."""
    print(f"🏄 JetSki Browsing: {url}")
    try:
        # User-Agent to avoid simple blocking
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Omega/4.0; +http://shadowtag.ai)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Simple text extraction for now - can be enhanced with DOM parsing
        text_content = soup.get_text(separator=" ", strip=True)
        return {"content": text_content[:5000], "status": "success"}  # Truncate for token limits
    except Exception as e:
        return {"error": str(e), "status": "failed"}
