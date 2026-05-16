# Exit Protocol - Complete All Outstanding Work

Execute the following exit protocol to safely close this session:

## 1. Complete Outstanding Todos

Review and complete all pending items in the todo list:

```
Use TodoWrite to mark all completed items, and report any items that remain blocked or pending.
```

## 2. Maintenance Tasks

### 2.1 Update Antigravity Memory
Save session context to transcripts:
```bash
# Create session transcript
echo "Session transcript will be saved to: transcripts/antigravity_session_$(date +%Y-%m-%d)_exit.md"
```

Update these files with any changes from this session:
- `ANTIGRAVITY_QUICK_REF.md` - Quick reference updates
- `transcripts/` - Session details for Antigravity continuity

### 2.2 Clean Up Temporary Files
```bash
# Remove any temp files created during session
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
```

### 2.3 Verify Services Health
```bash
# Check FlyingMonkeys
curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://flyingmonkeys-server-dev-215390634092.us-central1.run.app/health | python3 -m json.tool

# Check CodePMCS (if deployed)
curl -s -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://codepmcs-server-dev-215390634092.us-central1.run.app/health | python3 -m json.tool
```

## 3. Git Closeout

### 3.1 Stage All Changes
```bash
git status
git add -A
```

### 3.2 Create Exit Commit
```bash
git commit -m "$(cat <<'EOF'
Session exit: [SUMMARY OF WORK DONE]

Changes:
- [List key changes made this session]

Services:
- FlyingMonkeys: [status]
- CodePMCS: [status]

Todos completed: [count]
Todos remaining: [count]

Next session priorities:
- [Priority 1]
- [Priority 2]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3.3 Push to Remote
```bash
git push origin HEAD
```

### 3.4 Clean Up Stale Branches (Optional)
```bash
# List merged branches
git branch --merged | grep -v "main\|master\|claude/uninstall" | head -20

# Delete merged branches (manual confirmation required)
# git branch -d <branch-name>
```

## 4. Final Status Report

Generate and display:
1. Todo completion summary
2. Git commit hash
3. Service URLs and health
4. Next session priorities

## 5. Update Plan File

If a plan file exists, update it with:
- Completed phases
- Remaining work
- ARR/timeline adjustments

---

**IMPORTANT**: Do not exit without:
- [ ] All todos addressed (completed or documented as blocked)
- [ ] Session transcript saved
- [ ] Git committed and pushed
- [ ] Services verified healthy
- [ ] Plan file updated
