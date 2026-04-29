# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import sys


def resolve_file(filepath):
    with open(filepath) as f:
        content = f.read()

    # Pattern to match conflict blocks:
    # <<<<<<< HEAD
    # (content we want)
    # ||||||| merged common ancestors
    # (content we don't want)
    # =======
    # (content we don't want)
    # >>>>>>> branch
    #
    # OR
    #
    # <<<<<<< HEAD
    # (content we want)
    # =======
    # (content we don't want)
    # >>>>>>> branch

    # We want to keep the HEAD content.

    # Regex to capture HEAD content.
    # Note: DOTALL is needed. Non-greedy match for content.

    # Strategy: Find all blocks and replace with HEAD content.

    # Pattern A: 3-way conflict (with |||||||)
    # <{7} HEAD\n(.*?)\n\|{7} .*?\n={7}\n.*?\n>{7} .*?($|\n)

    # Pattern B: 2-way conflict
    # <{7} HEAD\n(.*?)\n={7}\n.*?\n>{7} .*?($|\n)

    # We can try a generic pattern that handles optional ||| part.
    # But python re doesn't support atomic groups, so be careful.

    # Let's iterate line by line to be safe.

    lines = content.splitlines(keepends=True)
    output_lines = []

    in_conflict = False
    in_head = False

    for line in lines:
        if line.startswith("<" * 7 + " HEAD"):
            in_conflict = True
            in_head = True
            continue

        if in_conflict:
            if line.startswith("|" * 7):
                in_head = False
                continue
            if line.startswith("=" * 7):
                in_head = False
                continue
            if line.startswith(">" * 7):
                in_conflict = False
                in_head = False
                continue

            if in_head:
                output_lines.append(line)
        else:
            output_lines.append(line)

    with open(filepath, "w") as f:
        f.writelines(output_lines)
    print(f"Resolved {filepath}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        resolve_file(sys.argv[1])
