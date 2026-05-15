"""PURGE SCRIPT
Target: Batch-mark legacy action items as [OBSOLETE].
Preserves: Files identified in MISSION_CRITICAL.md.
"""

import os

# Files to PRESERVE (The Golden Path)
preserved_files = [
    "src/shadowtag_v4/services/context_index.py",
    "src/orchestrator/deploy_03_cor_orchestrator.py",
    "src/pnkln/steel/steel_core.py",
    "src/judge_six/judge_core.py",
]


def is_preserved(filepath):
    return any(filepath.endswith(p) for p in preserved_files)


def process_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    new_lines = []
    modified = False

    for line in lines:
        # Check for action items
        if any(
            marker in line
            for marker in ["TODO [OBSOLETE]", "FIXME", "Next Step", "Next steps:", "Next Steps:"]
        ):
            # If it's already marked, skip
            if "[OBSOLETE]" in line or "[CRITICAL]" in line or "[HIGH]" in line:
                new_lines.append(line)
                continue

            # Mark it
            # Attempt to insert [OBSOLETE] before the marker or at the end
            if "TODO [OBSOLETE]" in line:
                line = line.replace("TODO", "TODO [OBSOLETE]")
            elif "FIXME [OBSOLETE]" in line:
                line = line.replace("FIXME", "FIXME [OBSOLETE]")
            elif (
                "Next Step [OBSOLETE]" in line
            ):  # Case insensitive handling in grep, but here strict
                line = line.replace("Next Step", "Next Step [OBSOLETE]")
            elif "Next steps [OBSOLETE]:" in line:
                line = line.replace("Next steps:", "Next steps [OBSOLETE]:")
            elif "Next Step [OBSOLETE]s:" in line:
                line = line.replace("Next Steps:", "Next Steps [OBSOLETE]:")

            modified = True

        new_lines.append(line)

    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Purged: {filepath}")


def main():
    root_dir = "."
    count = 0
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden and cache dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs[:] = [d for d in dirs if d not in ["__pycache__", "node_modules", "venv", "env"]]

        for file in files:
            if file.endswith((".py", ".ts", ".js", ".md")) and file != "MISSION_CRITICAL.md":
                filepath = os.path.join(root, file)

                # Check preservation
                if is_preserved(filepath):
                    print(f"Preserving: {filepath}")
                    continue

                process_file(filepath)
                count += 1

    print(f"\nPurge Complete. Scanned {count} files.")


if __name__ == "__main__":
    main()
