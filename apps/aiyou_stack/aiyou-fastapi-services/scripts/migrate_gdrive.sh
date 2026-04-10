#!/bin/bash
set -e

# Google Drive Migration: ehanc6901@gmail.com → founder@shadowtagai.com
# Uses rclone for server-side transfer (no local bandwidth needed)
# Post-migration: deletes all data from personal account

SRC="gdrive-personal"   # ehanc6901@gmail.com
DST="gdrive-corp"       # founder@shadowtagai.com

echo "=== Google Drive Migration ==="
echo "Source:      ehanc6901@gmail.com"
echo "Destination: founder@shadowtagai.com"
echo ""

# Step 1: Install rclone if needed
if ! command -v rclone &>/dev/null; then
    echo "Installing rclone..."
    /opt/homebrew/bin/brew install rclone
fi

# Step 2: Configure remotes (interactive, run once)
if ! rclone listremotes | grep -q "$SRC:"; then
    echo "Configure source remote (ehanc6901@gmail.com):"
    rclone config create "$SRC" drive
fi

if ! rclone listremotes | grep -q "$DST:"; then
    echo "Configure destination remote (founder@shadowtagai.com):"
    rclone config create "$DST" drive
fi

# Step 3: Snapshot source file count for verification
echo ""
echo "=== PRE-FLIGHT: Counting source files ==="
SRC_COUNT=$(rclone size "$SRC:" --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "unknown")
SRC_BYTES=$(rclone size "$SRC:" --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['bytes'])" 2>/dev/null || echo "unknown")
echo "Source: $SRC_COUNT files, $SRC_BYTES bytes"

# Step 4: Dry run
echo ""
echo "=== DRY RUN (no changes) ==="
rclone copy "$SRC:" "$DST:Migrated_From_Personal/" \
    --dry-run \
    --verbose \
    --drive-acknowledge-abuse \
    2>&1 | tail -20

echo ""
read -p "Proceed with REAL copy? (y/N) " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

# Step 5: Execute copy
echo ""
echo "=== COPYING ==="
rclone copy "$SRC:" "$DST:Migrated_From_Personal/" \
    --verbose \
    --drive-acknowledge-abuse \
    --transfers 4 \
    --checkers 8

# Step 6: Verify destination matches source
echo ""
echo "=== VERIFICATION ==="
DST_COUNT=$(rclone size "$DST:Migrated_From_Personal/" --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "unknown")
DST_BYTES=$(rclone size "$DST:Migrated_From_Personal/" --json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['bytes'])" 2>/dev/null || echo "unknown")
echo "Source:      $SRC_COUNT files, $SRC_BYTES bytes"
echo "Destination: $DST_COUNT files, $DST_BYTES bytes"

if [[ "$SRC_COUNT" != "$DST_COUNT" ]]; then
    echo ""
    echo "WARNING: File counts do not match! Skipping deletion."
    echo "Run 'rclone check $SRC: $DST:Migrated_From_Personal/' to diagnose."
    exit 1
fi

echo ""
echo "File counts match."

# Step 7: Run rclone check for integrity
echo ""
echo "=== INTEGRITY CHECK ==="
if ! rclone check "$SRC:" "$DST:Migrated_From_Personal/" --one-way 2>&1; then
    echo ""
    echo "WARNING: Integrity check found differences. Skipping deletion."
    echo "Review output above, fix any issues, then re-run."
    exit 1
fi

echo ""
echo "Integrity check passed."

# Step 8: Delete from personal account
echo ""
echo "=== DELETE FROM ehanc6901@gmail.com ==="
echo "This will permanently delete ALL files from the personal Drive."
read -p "Type DELETE to confirm: " DELETE_CONFIRM
if [[ "$DELETE_CONFIRM" != "DELETE" ]]; then
    echo "Deletion skipped. Files remain on both accounts."
    echo "To delete later: rclone delete $SRC: --rmdirs --verbose"
    exit 0
fi

rclone delete "$SRC:" --rmdirs --verbose
echo ""
echo "=== CLEANUP: Emptying trash on personal account ==="
rclone cleanup "$SRC:" 2>/dev/null || echo "(Trash cleanup requires Drive API scope — empty manually at drive.google.com/drive/trash)"

echo ""
echo "=== MIGRATION COMPLETE ==="
echo "All data moved to founder@shadowtagai.com/Migrated_From_Personal/"
echo "Personal Drive (ehanc6901@gmail.com) has been wiped."
echo ""
echo "Remaining manual steps:"
echo "  1. Go to https://drive.google.com (logged in as ehanc6901) and empty trash"
echo "  2. Verify at https://drive.google.com (logged in as founder@shadowtagai.com)"
echo "  3. Optionally revoke rclone OAuth: Google Account → Security → Third-party apps"
