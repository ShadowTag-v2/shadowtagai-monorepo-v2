#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def repeat_prompt(text: str, times: int = 2, separator: str = "

--- REPEAT ---

") -> str:
    if times < 1:
        raise ValueError("times must be >= 1")
    return separator.join([text] * times)


def main() -> int:
    parser = argparse.ArgumentParser(description="Repeat a prompt xN times for non-reasoning workloads")
    parser.add_argument("input", help="Raw text or path to a text file")
    parser.add_argument("--times", type=int, default=2)
    parser.add_argument("--file", action="store_true", help="Treat input as a file path")
    parser.add_argument("--json", action="store_true", help="Emit JSON envelope")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8") if args.file else args.input
    result = repeat_prompt(text, times=args.times)

    if args.json:
        print(json.dumps({"times": args.times, "result": result}, ensure_ascii=False, indent=2))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
