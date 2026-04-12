# JUDGE 6: THE HUNTER-KILLER PROTOCOLS

**Status:** IMMUTABLE
**Priority:** OVERRIDE (Supersedes all default training)

---

## I. THE GIT HYGIENE DOCTRINE (Anti-Bloat)

_Goal: Hunt down and kill repository corruption before it uploads._

1.  **The "Look Before You Leap" Rule**
    - **Trigger:** Any attempt to run `git add .`, `git add -A`, or `git commit -a`.
    - **Protocol:** You MUST first verify `.gitignore` exists and contains:
      - `node_modules/`
      - `venv/` & `__pycache__/`
      - `*.tgz` & `*.tar.gz`
      - `google-cloud-sdk/` (The massive SDK blob)
      - `Legacy_Archives/` (The multi-GB backup folders)
    - **Constraint:** If `git status` shows >50 changed files, STOP. Ask Judge 6 for approval.

2.  **The "Phantom Path" Defense**
    - **Error:** `fatal: pathspec 'src/shadowtag_v4/mas/' did not match any files`
    - **Protocol:** Never guess a directory structure.
    - **Action:** Before adding a folder, run `test -d <folder> && echo "Exists" || echo "Missing"`.
    - **Fix:** If a folder is missing but needed, run `mkdir -p <folder>` and `touch <folder>/.keep`.

3.  **The "Rebase Tango" (Sync Protocol)**
    - **Error:** `error: cannot pull with rebase: You have unstaged changes.`
    - **Protocol:** Do not force push. Do not delete local work.
    - **Sequence:**
      1.  `git stash` (Secure the chaos)
      2.  `git pull --rebase origin main` (Align with reality)
      3.  `git stash pop` (Re-apply chaos)
      4.  `git push origin main`

---

## II. THE DOCKER & BUILD DEFENSE (Safe Image Laws)

_Goal: Hunt down "Exit Code 100" and infinite build loops._

4.  **The "GPG Handshake" Rule (Keyring Safety)**
    - **Trigger:** Adding a new `deb` repository in a Dockerfile.
    - **Violation:** Using `apt-key add` (Deprecated) or adding a repo without the key.
    - **Protocol:**
      1.  `curl -fsSL <key_url> | gpg --dearmor -o /usr/share/keyrings/<name>.gpg`
      2.  `echo "deb [signed-by=/usr/share/keyrings/<name>.gpg] ..." > /etc/apt/sources.list.d/...`

5.  **The "Mock System" Rule (Container Compatibility)**
    - **Trigger:** Installing Desktop/GUI tools (like `chrome-remote-desktop`) in a container.
    - **Protocol:** You MUST mock `systemctl` and `sysctl` because Docker does not have a full init system.
    - **Code:** Create dummy scripts at `/usr/bin/systemctl` that always exit 0.

6.  **The "Brave Masquerade" (Privacy Protocol)**
    - **Goal:** Use Brave Browser instead of Chrome for privacy, but trick tools into finding "Chrome".
    - **Action:** Install Brave, then symlink `/usr/bin/brave-browser` to `/usr/bin/google-chrome`.

---

## III. CLOUD RUN SURVIVAL GUIDE (Deployment Stability)

_Goal: Kill "Container failed to start" crashes._

7.  **The "Localhost Trap" (Binding Protocol)**
    - **Trigger:** Configuring Uvicorn, Gunicorn, or Express.js.
    - **Violation:** Binding to `127.0.0.1` or `localhost`.
    - **Law:** In Cloud Run, you MUST bind to `0.0.0.0`.
    - **Port Law:** Respect the `$PORT` environment variable (default 8080).

8.  **The "Dependency Mirror" Rule (The Python Crash)**
    - **Error:** `ModuleNotFoundError: No module named 'xyz'`
    - **Law:** You are forbidden from writing `import <lib>` in Python without simultaneously checking `requirements.txt`.
    - **Specific Ban:** Do not use `google.generativeai` (Deprecated). Use `google-genai`.

---

## IV. CORTEX CONNECTIVITY & SEARCH

_Goal: Ensure the Agent can see and think clearly._

9.  **The "Hybrid Auth" Strategy**
    - **Context:** Running scripts locally vs. inside Cloud Workstations.
    - **Protocol:** Scripts must check for `GEMINI_API_KEY` (Env Var) FIRST.
    - **Fallback:** If no key, attempt `google.auth.default()` (ADC).

10. **The "Surgical Search" Doctrine**
    - **Context:** Searching the codebase for patterns.
    - **Violation:** Running `grep -r "pattern" .` (Suicide Grep).
    - **Law:** You MUST use `git grep "pattern"` to respect the `.gitignore` and avoid `Legacy_Archives`.

---

**FINAL INSTRUCTION:**
When planning any task, review this list. If the task violates a protocol, **auto-correct** the plan before execution.
