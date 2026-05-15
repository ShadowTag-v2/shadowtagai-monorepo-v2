# Antigravity IDE Installation Troubleshooting (Ubuntu/Linux)

## "Account Not Eligible" or Zsh Permission Errors?

If you are stuck in a GPG loop or facing a 404 error while installing Google Antigravity on Ubuntu, here is the working script and fixes.

### The Problem
The official documentation often assumes a perfect environment. Failures include:
1.  **Silent Fail:** `curl` missing.
2.  **GPG Loop:** Infinite "Overwrite?" prompt due to piping `curl` to `sudo gpg`.
3.  **404 Error:** Region lock or outdated link.

### The Fix: "Anti-Loop" Install Script

Stop hitting `y`. Kill the process (`Ctrl+C`) and run this:

**Step 1: Pre-Flight Check**
```bash
# Update and ensure curl and gnupg are present
sudo apt update && sudo apt install -y curl gnupg
```

**Step 2: Clean Up**
```bash
sudo rm -f /etc/apt/keyrings/antigravity-repo-key.gpg
```

**Step 3: The Working Command**
```bash
# Create the keyring folder safely
sudo mkdir -p /etc/apt/keyrings

# Download the key QUIETLY and force-save it
# The '-' at the end tells gpg to read from the pipe (stdin) explicitly
curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | \
  sudo gpg --dearmor --batch --yes -o /etc/apt/keyrings/antigravity-repo-key.gpg -
```
*Tip: If you hit a 404, try a US-based VPN.*

**Step 4: Add Repo & Install**
```bash
echo "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" | \
  sudo tee /etc/apt/sources.list.d/antigravity.list > /dev/null

sudo apt update
sudo apt install antigravity-ide
```

### Post-Install Issues

1.  **"Account Not Eligible" (Region Lock):**
    *   **Fix:** Use a US VPN (e.g., NordVPN) before launching. If blocked on Workspace, try personal Gmail.

2.  **Infinite Spinner ("Setting Up Your Account"):**
    *   **Fix:** Click "Back" and "Next" repeatedly, or restart the app.

3.  **Zsh Insecure Directories:**
    *   **Error:** `zsh compinit: insecure files...`
    *   **Fix:**
        ```bash
        sudo chmod -R 755 /usr/share/zsh/vendor-completions
        sudo chown -R root:root /usr/share/zsh/vendor-completions
        ```

## The Distinction: Official vs. Anti-Loop

The core **difference** lies in how `gpg` handles input and interactivity when piped:

1.  **The "Official" Flaw (The Zombie Loop):**
    *   Command: `curl ... | sudo gpg -o ...`
    *   **The Issue:** When you pipe `curl` into `sudo gpg`, the `gpg` process is receiving the *key data* on its standard input (stdin). If the output file already exists, `gpg` tries to ask "Overwrite? (y/N)".
    *   **The Failure:** Because stdin is occupied by the key data stream, `gpg` cannot receive your "y" or "n" keystrokes effectively, or it gets confused about the terminal state. It loops infinitely, reprompting without accepting input.

2.  **The "Anti-Loop" Fix (Robust):**
    *   Command: `curl ... | sudo gpg --batch --yes -o ... -`
    *   **The Fix:**
        *   `--batch`: Tells `gpg` to run non-interactively (no questions).
        *   `--yes`: preemptively answers "Yes" to prompts like "Overwrite?".
        *   `-` (at the end): Explicitly tells `gpg` to read the key data from stdin (the pipe).
    *   **Result:** It silently overwrites any existing corrupted file using the fresh download, completely bypassing the interactive prompt loop.
