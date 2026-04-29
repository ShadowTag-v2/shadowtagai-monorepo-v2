#!/bin/bash
echo "[*] Initiating Skills Audit..."
ACTIVE_SKILLS=$(find ~/.gemini/antigravity/skills ~/.gemini/antigravity/Monorepo-Uphillsnowball/.agents/skills ~/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/skills -type f -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' \n')
ARCHIVED_SKILLS=$(find ~/.gemini/antigravity/skills/_archive_* ~/.gemini/antigravity/Monorepo-Uphillsnowball/.agents/skills/_archive_* ~/.gemini/antigravity/Monorepo-Uphillsnowball/.agent/skills/_archive_* -type f -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' \n')
echo "Active: ${ACTIVE_SKILLS:-0} | Archived: ${ARCHIVED_SKILLS:-0}"
echo "[+] Audit Complete."
