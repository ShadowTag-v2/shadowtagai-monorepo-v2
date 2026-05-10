#!/usr/bin/env python3
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
METRICS_DIR = REPO_ROOT / ".ci"
METRICS_FILE = METRICS_DIR / "metrics.jsonl"
MAX_TOTAL_ATTEMPTS = int(os.getenv("AIAUTOFIX_MAX_ATTEMPTS", "4"))
TPM_BUDGET = int(os.getenv("OPENAI_TPM_BUDGET", "450000"))
RPM_BUDGET = int(os.getenv("OPENAI_RPM_BUDGET", "60"))


def run(cmd, check=False, capture=False, cwd=REPO_ROOT):
    if capture:
        return subprocess.run(cmd, cwd=cwd, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return subprocess.run(cmd, cwd=cwd, text=True, shell=True, check=check)


def run_tests():
    r = run("pytest -q", capture=True)
    return r.returncode == 0, r.stdout


def estimate_tokens(text):
    return max(1, int(len(text) / 4))


def budget_pacer(prompt_tokens, resp_max=4096):
    tokens = prompt_tokens + resp_max
    now = time.time()
    window = 60
    stamp = os.getenv("AIAUTOFIX_TPM_STAMP")
    used = int(os.getenv("AIAUTOFIX_TPM_USED", "0"))
    if not stamp:
        os.environ["AIAUTOFIX_TPM_STAMP"] = str(now)
        os.environ["AIAUTOFIX_TPM_USED"] = "0"
        used = 0
        stamp = str(now)
    else:
        if now - float(stamp) >= window:
            os.environ["AIAUTOFIX_TPM_STAMP"] = str(now)
            os.environ["AIAUTOFIX_TPM_USED"] = "0"
            used = 0
    projected = used + tokens
    if projected > TPM_BUDGET:
        time.sleep(2)
        os.environ["AIAUTOFIX_TPM_STAMP"] = str(time.time())
        os.environ["AIAUTOFIX_TPM_USED"] = "0"
    else:
        os.environ["AIAUTOFIX_TPM_USED"] = str(projected)


def log_metric(model: str, scope: str, prompt_tokens: int, resp_max: int, note: str = "") -> None:
    try:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "ts": int(time.time()),
            "model": model,
            "scope": scope,
            "prompt_tokens": prompt_tokens,
            "resp_max": resp_max,
            "note": note,
        }
        with METRICS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass


def changed_file_list(scope="changed"):
    if scope == "project":
        r = run("git ls-files", capture=True)
        files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
        return files
    r = run("git diff --name-only HEAD~1..HEAD || git diff --name-only", capture=True)
    files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
    if not files:
        r = run("git diff --name-only --cached", capture=True)
        files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
    return files


def failing_files(out):
    s = set()
    for p in re.findall(r"^FAILED +([^\s:]+\.py)::", out, re.M):
        s.add(p)
    for p in re.findall(r"^\s*([^\s:]+\.py):\d+:", out, re.M):
        s.add(p)
    return list(s)


def build_prompt(failing_output, files, goal, max_chars=60000):
    blobs, used = [], 0
    for f in files:
        path = REPO_ROOT / f
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        chunk = f"\n### FILE: {f}\n```\n{text}\n```"
        if used + len(chunk) > max_chars:
            break
        blobs.append(chunk)
        used += len(chunk)
    ctx = "".join(blobs)
    prompt = (
        "You are a senior engineer fixing CI failures.\n\n"
        + f"GOAL: {goal}\n\n"
        + f"TEST OUTPUT (abbrev):\n````\n\n{failing_output[:20000]}\n\n````\n\n"
        + f"REPO CONTEXT (subset):\n{ctx}\n\n"
        + "REPLY ONLY WITH A VALID UNIFIED DIFF (git apply). No explanations.\n"
    )
    return prompt


def http_json(url, headers, data):
    import requests

    try:
        return requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
    except Exception:
        return None


def call_openai(model, prompt, scope, resp_max=2048, tries=4):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None, "no_key"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "max_tokens": resp_max}
    ptoks = estimate_tokens(prompt)
    budget_pacer(ptoks, resp_max)
    log_metric(model, scope, ptoks, resp_max, note="attempt")
    for i in range(tries):
        r = http_json(url, headers, data)
        if r and r.status_code == 200:
            try:
                return r.json()["choices"][0]["message"]["content"], None
            except Exception:
                return None, "parse"
        # Rate-limit handling with precise backoff
        wait_seconds = 0.0
        if r is not None:
            ra = r.headers.get("Retry-After")
            if ra:
                try:
                    wait_seconds = float(ra)
                except Exception:
                    wait_seconds = 0.0
            if not wait_seconds:
                txt = (r.text or "").lower()
                m = re.search(r"try again in ([0-9.]+)s", txt)
                if m:
                    try:
                        wait_seconds = float(m.group(1))
                    except Exception:
                        wait_seconds = 0.0
        if wait_seconds:
            time.sleep(wait_seconds + __import__("random").uniform(0.25, 0.75))
        else:
            time.sleep(0.5 * (2**i) + __import__("random").uniform(0.1, 0.3))
    return None, "fail"


def call_anthropic(model, prompt, scope, resp_max=1200, tries=4):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None, "no_key"
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    data = {"model": model, "max_tokens": resp_max, "messages": [{"role": "user", "content": prompt}], "temperature": 0}
    for i in range(tries):
        import requests

        r = None
        try:
            r = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
        except Exception:
            r = None
        if r and r.status_code == 200:
            try:
                parts = r.json().get("content", [])
                text = "".join(p.get("text", "") for p in parts if p.get("type") == "text")
                log_metric(model, scope, estimate_tokens(prompt), resp_max, note="ok")
                return text, None
            except Exception:
                return None, "parse"
        # Gentle backoff on 429/5xx
        if r is not None and (r.status_code == 429 or 500 <= r.status_code < 600):
            time.sleep(0.5 * (2**i) + __import__("random").uniform(0.1, 0.3))
        else:
            time.sleep(0.3)
    return None, "fail"


def extract_diff(text):
    if not text:
        return None
    m = re.search(r"```diff(.*?)```", text, re.S | re.I)
    if m and m.group(1).strip().startswith("--- a/"):
        return m.group(1).strip()
    if text.strip().startswith("--- a/"):
        return text.strip()
    m = re.search(r"(?s)^--- a/.+?\n\+\+\+ b/.+?$", text, re.M)
    return text[m.start() :].strip() if m else None


def apply_diff(patch_text):
    if not patch_text:
        return False, "empty"
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch", encoding="utf-8") as tf:
        tf.write(patch_text)
        tf.flush()
        patch_path = tf.name
    r = run(f'git apply --whitespace=fix --reject "{patch_path}"', capture=True)
    return (r.returncode == 0), r.stdout


def shard(lst, n):
    n = max(1, n)
    size = max(1, math.ceil(len(lst) / n))
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def attempt(goal, model, scope):
    ok, out = run_tests()
    if ok:
        return True
    failing = failing_files(out)
    base = changed_file_list(scope if scope != "project" else "changed")
    candidates = failing or base or changed_file_list("project")
    batches = list(shard(candidates, 3)) if len(candidates) > 20 else [candidates]
    for files in batches:
        run("git reset", capture=True)
        for f in files[:50]:
            run(f'git add "{f}"')
        prompt = build_prompt(out, files, goal)
        if model.startswith("gpt-5"):
            text, err = call_openai(model, prompt, scope, resp_max=2048)
            if err == "rate_limit" or not text:
                text, err = call_openai("gpt-5-fast", prompt, scope, resp_max=2048)
                if not text:
                    text, err = call_anthropic("claude-4-sonnet", prompt, scope, resp_max=1200)
        else:
            text, err = call_anthropic(model, prompt, scope, resp_max=1200)
        diff = extract_diff(text) if text else None
        applied, log = apply_diff(diff)
        if not applied:
            continue
        run("git add -A")
        run(f'git commit -m "ci: {model} autofix scope={scope} sharded" || echo "no changes"')
        ok2, _ = run_tests()
        if ok2:
            return True
    return False


def main():
    goal = os.getenv("AIAUTOFIX_GOAL", "Fix tests and lint errors; minimal diffs; stay within TPM; fallback on rate limits.")
    plan = [("gpt-5-fast", "changed"), ("claude-4-sonnet", "changed"), ("gpt-5", "project")]
    ok, _ = run_tests()
    if ok:
        print("✅ Tests green.")
        sys.exit(0)
    attempts = 0
    for model, scope in plan:
        if attempts >= MAX_TOTAL_ATTEMPTS:
            break
        if attempt(goal, model, scope):
            print(f"✅ Green after {model} ({scope}).")
            sys.exit(0)
        attempts += 1
    print("❌ Still failing after throttled AI autofix attempts.")
    sys.exit(1)


if __name__ == "__main__":
    main()
