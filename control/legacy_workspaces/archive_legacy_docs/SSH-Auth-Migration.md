# SSH-first Migration: What Happened and Why It Fixes Popups

## 1) Why the GitHub login popup kept appearing
- Your repos were using HTTPS remotes.
- When Git/VS Code/Cursor tried to sync and couldn’t find cached HTTPS credentials, it triggered the GitHub Device Login flow repeatedly.

## 2) What we changed
- We introduced an SSH-first scaffold (`tools/scaffold_github_ssh.ps1`) that sets remotes like:
  `git@github.com:Owner/Repo.git`
  instead of `https://github.com/Owner/Repo.git`.
- With SSH remotes, Git authenticates using your SSH key (no browser OAuth).

## 3) Impact on your workflow
- No more login interruptions once your SSH key is added and `ssh-agent` is running.
- Same auth method locally and in CI/CD.
- Safer than juggling personal access tokens in scripts.

## 4) Where you are now
- The browser “you’re all set” page confirmed a one-time device auth for HTTPS.
- Because the remote was HTTPS, prompts kept returning.
- Switching to SSH breaks that loop permanently.

## TL;DR
You were caught in GitHub’s HTTPS device-auth loop. Migrating remotes to SSH stops the popups and standardizes auth everywhere.

## One-time setup
Windows PowerShell:
```powershell
Start-SshAgent
ssh-keygen -t ed25519 -C "$env:USERNAME"
ssh-add $env:USERPROFILE\.ssh\id_ed25519
# Add id_ed25519.pub to GitHub → Settings → SSH and GPG keys
```
macOS/Linux:
```bash
eval "$(ssh-agent -s)"
ssh-keygen -t ed25519 -C "$(whoami)"
ssh-add ~/.ssh/id_ed25519
# Add ~/.ssh/id_ed25519.pub to GitHub → Settings → SSH and GPG keys
```

## Convert existing repos to SSH
```bash
git remote set-url origin git@github.com:<Owner>/<Repo>.git
```

## Scaffold new repos with SSH remotes
```powershell
pwsh -NoProfile -File tools\scaffold_github_ssh.ps1 -Owner <YourGitHubUserOrOrg>
```
