#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# THOROUGH MERGE RESOLUTION SCRIPT
# Branch: code-into-c → integration-main
# For use in Claude Code terminal
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SOURCE_BRANCH="claude/code-into-c-01M1anzYZdJTDDeZQsiVTkKS"
TARGET_BRANCH="claude/integration-main"
BACKUP_BRANCH="integration-main-backup-$(date +%Y%m%d-%H%M%S)"
MERGE_LOG="merge-resolution-$(date +%Y%m%d-%H%M%S).md"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

cd "$REPO_ROOT"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1: SAFETY CHECKPOINT
# ─────────────────────────────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 1: SAFETY CHECKPOINT"
echo "═══════════════════════════════════════════════════════════════"

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  WARNING: Uncommitted changes detected"
    echo "   Stashing changes..."
    git stash push -m "pre-merge-stash-$(date +%Y%m%d-%H%M%S)"
fi

# Create backup branch
echo "📦 Creating backup: $BACKUP_BRANCH"
git branch "$BACKUP_BRANCH" "$TARGET_BRANCH" 2>/dev/null || echo "   (backup may already exist)"

# Initialize merge log
cat > "$MERGE_LOG" << EOF
# Merge Resolution Log
**Date**: $(date)
**Source**: $SOURCE_BRANCH
**Target**: $TARGET_BRANCH
**Backup**: $BACKUP_BRANCH

## Conflict Resolution Decisions

| File | Strategy | Rationale |
|------|----------|-----------|
EOF

echo "✅ Backup created, log initialized"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: INITIATE MERGE
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 2: INITIATE MERGE"
echo "═══════════════════════════════════════════════════════════════"

git checkout "$TARGET_BRANCH"
echo "📍 On branch: $(git branch --show-current)"

# Start merge (will fail with conflicts - expected)
echo "🔀 Starting merge from $SOURCE_BRANCH..."
git merge "$SOURCE_BRANCH" --no-commit --no-ff 2>&1 || true

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: CATALOG CONFLICTS
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 3: CATALOG CONFLICTS"
echo "═══════════════════════════════════════════════════════════════"

# Get list of conflicted files
CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null || echo "")
CONFLICT_COUNT=$(echo "$CONFLICTS" | grep -c . || echo "0")

if [ "$CONFLICT_COUNT" -eq 0 ]; then
    echo "✅ No conflicts detected - merge clean"
    git commit -m "Merge $SOURCE_BRANCH into $TARGET_BRANCH (clean)"
    exit 0
fi

echo "📋 Found $CONFLICT_COUNT conflicted files:"
echo ""

# Display conflicts by category
while IFS= read -r file; do
    [ -z "$file" ] && continue
    ext="${file##*.}"
    case "$ext" in
        py) cat="PYTHON" ;;
        js|ts|jsx|tsx) cat="JAVASCRIPT" ;;
        md|txt|rst) cat="DOCS" ;;
        json|yaml|yml|toml) cat="CONFIG" ;;
        sh|bash) cat="SCRIPTS" ;;
        *) cat="OTHER" ;;
    esac
    echo "   [$cat] $file"
done <<< "$CONFLICTS"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: RESOLUTION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

resolve_file() {
    local file="$1"
    local strategy="$2"
    local rationale="$3"

    case "$strategy" in
        ours)
            git checkout --ours "$file"
            git add "$file"
            ;;
        theirs)
            git checkout --theirs "$file"
            git add "$file"
            ;;
        manual)
            echo "   ⏸️  Manual resolution required for: $file"
            return 1
            ;;
    esac

    # Log decision
    echo "| $file | $strategy | $rationale |" >> "$MERGE_LOG"
    echo "   ✅ Resolved: $file ($strategy)"
}

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5: INTELLIGENT AUTO-RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 5: INTELLIGENT AUTO-RESOLUTION"
echo "═══════════════════════════════════════════════════════════════"

MANUAL_REQUIRED=()

while IFS= read -r file; do
    [ -z "$file" ] && continue

    echo ""
    echo "─────────────────────────────────────────────────────────────"
    echo "Processing: $file"
    echo "─────────────────────────────────────────────────────────────"

    # Get conflict stats
    OURS_LINES=$(git show ":2:$file" 2>/dev/null | wc -l || echo "0")
    THEIRS_LINES=$(git show ":3:$file" 2>/dev/null | wc -l || echo "0")

    echo "   Target ($TARGET_BRANCH): $OURS_LINES lines"
    echo "   Source ($SOURCE_BRANCH): $THEIRS_LINES lines"

    # Decision logic based on file type and content
    ext="${file##*.}"
    filename=$(basename "$file")

    # Auto-resolution rules
    RESOLVED=false

    # Rule 1: Lock files - always take newer
    if [[ "$filename" == *"lock"* ]] || [[ "$filename" == "package-lock.json" ]] || [[ "$filename" == "yarn.lock" ]]; then
        resolve_file "$file" "theirs" "Lock file - take source version"
        RESOLVED=true

    # Rule 2: Generated files - take source
    elif [[ "$file" == *"generated"* ]] || [[ "$file" == *"dist/"* ]] || [[ "$file" == *"build/"* ]] || [[ "$file" == *"__pycache__"* ]] || [[ "$file" == *".pyc" ]]; then
        resolve_file "$file" "theirs" "Generated file - take source"
        RESOLVED=true

    # Rule 3: Coverage/test output - take source
    elif [[ "$file" == *"coverage"* ]] || [[ "$file" == *".coverage"* ]]; then
        resolve_file "$file" "theirs" "Coverage file - take source"
        RESOLVED=true

    # Rule 4: Documentation - take source (usually more current)
    elif [[ "$ext" == "md" ]] || [[ "$ext" == "txt" ]] || [[ "$ext" == "rst" ]]; then
        resolve_file "$file" "theirs" "Documentation - take source (more current)"
        RESOLVED=true

    # Rule 5: Config files - favor target (integration-main is canonical)
    elif [[ "$ext" == "json" ]] || [[ "$ext" == "yaml" ]] || [[ "$ext" == "yml" ]] || [[ "$ext" == "toml" ]]; then
        resolve_file "$file" "ours" "Config file - keep integration-main version"
        RESOLVED=true

    # Rule 6: Dockerfile, .gitignore, .env.example - favor target
    elif [[ "$filename" == "Dockerfile" ]] || [[ "$filename" == ".gitignore" ]] || [[ "$filename" == ".env.example" ]] || [[ "$filename" == ".cursorrules" ]]; then
        resolve_file "$file" "ours" "Project config - keep integration-main"
        RESOLVED=true

    # Rule 7: Source code - take source branch (newer features)
    elif [[ "$ext" == "py" ]] || [[ "$ext" == "js" ]] || [[ "$ext" == "ts" ]]; then
        resolve_file "$file" "theirs" "Source code - take source branch features"
        RESOLVED=true

    # Rule 8: Shell scripts - take source
    elif [[ "$ext" == "sh" ]] || [[ "$ext" == "bash" ]]; then
        resolve_file "$file" "theirs" "Shell script - take source"
        RESOLVED=true

    # Default: take source
    else
        resolve_file "$file" "theirs" "Default - take source"
        RESOLVED=true
    fi

done <<< "$CONFLICTS"

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6: HANDLE DELETED FILE CONFLICTS
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 6: DELETED FILE CONFLICTS"
echo "═══════════════════════════════════════════════════════════════"

# Check for modify/delete conflicts
DELETED_CONFLICTS=$(git status --porcelain | grep "^DU\|^UD" | awk '{print $2}' || echo "")
if [ -n "$DELETED_CONFLICTS" ]; then
    while IFS= read -r file; do
        [ -z "$file" ] && continue
        echo "   Keeping file (was deleted in source): $file"
        git add "$file"
    done <<< "$DELETED_CONFLICTS"
fi

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7: STATUS REPORT
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 7: STATUS REPORT"
echo "═══════════════════════════════════════════════════════════════"

REMAINING=$(git diff --name-only --diff-filter=U 2>/dev/null | wc -l || echo "0")

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│ MERGE STATUS                                                │"
echo "├─────────────────────────────────────────────────────────────┤"
printf "│ Total conflicts:     %-37s │\n" "$CONFLICT_COUNT"
printf "│ Remaining:           %-37s │\n" "$REMAINING"
printf "│ Backup branch:       %-37s │\n" "$BACKUP_BRANCH"
echo "└─────────────────────────────────────────────────────────────┘"

echo ""
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All conflicts resolved!"
    echo ""
    echo "NEXT STEPS:"
    echo "   1. Review: git diff --staged | head -100"
    echo "   2. Commit: git commit -m 'Merge code-into-c into integration-main'"
    echo "   3. Push:   git push origin $TARGET_BRANCH"
else
    echo "⚠️  $REMAINING conflicts remaining"
    echo ""
    echo "Remaining files:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "To resolve manually:"
    echo "   git checkout --ours <file>   # Keep target version"
    echo "   git checkout --theirs <file> # Keep source version"
    echo "   git add <file>"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Script complete. Log saved to: $MERGE_LOG"
echo "═══════════════════════════════════════════════════════════════"
