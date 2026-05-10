# SSH Sanity Checklist

## 1) Confirm Git is using SSH
```bash
git remote -v
```
Expected:
```
origin  git@github.com:YourUser/YourRepo.git (fetch)
origin  git@github.com:YourUser/YourRepo.git (push)
```
If you see https://… fix it:
```bash
git remote set-url origin git@github.com:YourUser/YourRepo.git
```

## 2) Test SSH connection to GitHub
```bash
ssh -T git@github.com
```
Expected:
```
Hi YourUser! You've successfully authenticated, but GitHub does not provide shell access.
```

## 3) Check your SSH agent has the key loaded
Windows PowerShell:
```powershell
Start-SshAgent
ssh-add -l
```
macOS/Linux:
```bash
eval "$(ssh-agent -s)"
ssh-add -l
```
If none listed, add it:
```bash
ssh-add ~/.ssh/id_ed25519
```

## 4) Do a push test
```bash
echo "ssh sanity test $(date)" >> sanity.txt
git add sanity.txt
git commit -m "chore: sanity test"
git push origin main
```
No username/password prompts → SSH set.

## 5) Cursor
Save any file and watch Problems panel; Git operations should be silent.

## 6) Re-scaffold via SSH (optional)
```powershell
pwsh -NoProfile -File tools\scaffold_github_ssh.ps1 -Owner YourGitHubUser
```
