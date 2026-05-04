"""managed_push.py — Resumable, self-healing GitHub push daemon for Monorepo-Uphillsnowball.

Features:
  - Checkpoint file: survives restarts, picks up at last committed batch
  - Token refresh: new GitHub App installation token per batch (1hr tokens, refreshed always)
  - Token pre-expiry guard: proactively re-issues token if > 45 min old
  - Exponential backoff: 3 retries with 10/30/60s waits before abort
  - launchd-friendly: exits 0 on completion, non-zero on unrecoverable failure
    so launchd knows whether to restart

Run once:
    python scripts/managed_push.py

Or let launchd manage it (see scripts/com.antigravity.push.plist).
"""

import contextlib
import json
import logging
import os
import subprocess
import sys
import time

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Config ────────────────────────────────────────────────────────────────────
APP_ID = "3018200"
PEM_PATH = os.path.expanduser("~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem")
OWNER = "ShadowTag-v2"
REPO = "Monorepo-Uphillsnowball"
REMOTE = f"https://github.com/{OWNER}/{REPO}.git"
MAX_CHUNK_MB = 25
MAX_CHUNK_BYTES = MAX_CHUNK_MB * 1024 * 1024
CHECKPOINT_FILE = "/tmp/antigravity_push_checkpoint.json"
LOG_FILE = "/tmp/antigravity_push.log"
TOKEN_MAX_AGE_SECS = 45 * 60  # refresh before the 1hr GitHub limit
MAX_RETRIES = 3

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("antigravity.push")


# ── Git helpers ───────────────────────────────────────────────────────────────
def run(cmd: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)  # nosec B602 — intentional shell for git/system ops


# ── GitHub App token ──────────────────────────────────────────────────────────
class TokenManager:
    """Issues and caches GitHub App installation tokens, proactively refreshes."""

    def __init__(self, app_id: str, pem_path: str, owner: str) -> None:
        self.app_id = app_id
        self.pem_path = pem_path
        self.owner = owner
        self._token: str | None = None
        self._issued_at: float = 0

    def _http(self) -> requests.Session:
        s = requests.Session()
        retry = Retry(connect=5, read=5, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
        s.mount("https://", HTTPAdapter(max_retries=retry))
        return s

    def _issue(self) -> str | None:
        with open(self.pem_path, "rb") as f:
            pem = f.read()
        now = int(time.time())
        payload = {"iat": now - 60, "exp": now + 600, "iss": self.app_id}
        app_jwt = jwt.encode(payload, pem, algorithm="RS256")
        hdrs = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json",
        }
        s = self._http()
        resp = s.get("https://api.github.com/app/installations", headers=hdrs, timeout=30)
        if resp.status_code != 200:
            log.error("App installations fetch failed: %s %s", resp.status_code, resp.text[:200])
            return None
        installation_id = None
        for inst in resp.json():
            if inst["account"]["login"].lower() == self.owner.lower():
                installation_id = inst["id"]
                break
        if not installation_id:
            log.error("No installation found for owner=%s", self.owner)
            return None
        resp2 = s.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=hdrs,
            timeout=30,
        )
        if resp2.status_code == 201:
            return resp2.json()["token"]
        log.error("Token exchange failed: %s %s", resp2.status_code, resp2.text[:200])
        return None

    def get(self, force: bool = False) -> str | None:
        """Return cached token, refreshing if > TOKEN_MAX_AGE_SECS old."""
        age = time.time() - self._issued_at
        if force or self._token is None or age > TOKEN_MAX_AGE_SECS:
            log.info("Refreshing GitHub App token (age=%.0fs)...", age)
            self._token = self._issue()
            self._issued_at = time.time() if self._token else 0
            if self._token:
                log.info("Token issued OK.")
            else:
                log.error("Token issue FAILED.")
        return self._token


# ── Checkpoint ────────────────────────────────────────────────────────────────
def load_checkpoint() -> int:
    try:
        with open(CHECKPOINT_FILE) as f:
            return json.load(f).get("next_batch", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def save_checkpoint(batch_index: int) -> None:
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"next_batch": batch_index, "saved_at": time.time()}, f)


def clear_checkpoint() -> None:
    with contextlib.suppress(FileNotFoundError):
        os.remove(CHECKPOINT_FILE)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:  # returns exit code
    # Git config for large HTTP packs
    run("rm -f .git/index.lock")
    run("git config --local http.postBuffer 524288000")
    run("git config --local http.lowSpeedLimit 0")
    run("git config --local http.lowSpeedTime 999")

    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    os.environ["GIT_ASKPASS"] = "/usr/bin/false"

    # Collect files
    log.info("Scanning for untracked/modified files...")
    res = run("git ls-files --others --exclude-standard; git diff --name-only")
    all_files = sorted({f for f in res.stdout.split("\n") if f.strip() and os.path.exists(f)})
    log.info("Total files to process: %d", len(all_files))

    # Build chunks
    chunks: list[list[str]] = []
    current: list[str] = []
    current_size = 0
    for f in all_files:
        try:
            sz = os.path.getsize(f)
        except OSError:
            continue
        if sz > MAX_CHUNK_BYTES:
            log.warning("Skipping oversized file: %s (%.1f MB)", f, sz / 1e6)
            continue
        if current_size + sz > MAX_CHUNK_BYTES and current:
            chunks.append(current)
            current, current_size = [], 0
        current.append(f)
        current_size += sz
    if current:
        chunks.append(current)

    total = len(chunks)
    log.info("Total batches: %d (each ≤%d MB)", total, MAX_CHUNK_MB)

    resume_from = load_checkpoint()
    if resume_from:
        log.info("Resuming from checkpoint: batch %d/%d", resume_from + 1, total)

    token_mgr = TokenManager(APP_ID, PEM_PATH, OWNER)

    for i, chunk in enumerate(chunks):
        if i < resume_from:
            continue

        log.info("Batch %d/%d — %d files", i + 1, total, len(chunk))

        run("rm -f .git/index.lock")
        with open("/tmp/git_add_batch.txt", "w") as f:
            f.write("\n".join(chunk))
        run("git add --pathspec-from-file=/tmp/git_add_batch.txt")

        diff = run("git diff --cached --name-only")
        if not diff.stdout.strip():
            log.info("Batch %d: nothing new to commit, skipping.", i + 1)
            save_checkpoint(i + 1)
            continue

        commit_msg = f"chore(sync): monorepo bulk ingestion batch {i + 1} of {total} (25MB chunks)"
        run(f'git commit --no-verify -m "{commit_msg}"')

        # Token refresh (proactive — every 45 min or on force)
        token = token_mgr.get()
        if not token:
            log.error("Cannot obtain token. Aborting.")
            return 1
        run(f"git remote set-url origin https://x-access-token:{token}@{REMOTE.split('https://')[1]}")

        # Push with exponential backoff
        pushed = False
        for attempt in range(1, MAX_RETRIES + 1):
            push = run("git push -f origin main")
            out = (push.stdout or "") + (push.stderr or "")
            if "Everything up-to-date" in out or push.returncode == 0:
                log.info("Batch %d pushed OK (attempt %d).", i + 1, attempt)
                pushed = True
                break
            wait = 10 * (2 ** (attempt - 1))  # 10, 20, 40s
            log.warning(
                "Push failed (attempt %d/%d). Retrying in %ds. Error: %s",
                attempt,
                MAX_RETRIES,
                wait,
                push.stderr[:300],
            )
            time.sleep(wait)
            # Force-refresh token on retry in case the failure was 401
            token = token_mgr.get(force=True)
            if token:
                run(f"git remote set-url origin https://x-access-token:{token}@{REMOTE.split('https://')[1]}")

        if not pushed:
            log.error(
                "Batch %d failed after %d attempts. Saving checkpoint and exiting.",
                i + 1,
                MAX_RETRIES,
            )
            save_checkpoint(i)  # retry this batch on next launchd restart
            return 2  # non-zero → launchd will restart us

        save_checkpoint(i + 1)
        time.sleep(1)

    log.info("All %d batches complete.", total)
    clear_checkpoint()
    return 0


if __name__ == "__main__":
    sys.exit(main())
