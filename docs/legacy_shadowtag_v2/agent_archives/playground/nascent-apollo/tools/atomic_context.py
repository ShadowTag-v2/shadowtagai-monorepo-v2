#!/usr/bin/env python3
import argparse
from datetime import datetime

from beads_manager import BeadsEngine


def start_issue(title, brief):
    engine = BeadsEngine()
    details = f"Title: {title} | Brief: {brief}"
    engine.remember("ISSUE_START", details)

    print(f"\n✅ ATOMIC CONTEXT STARTED: {title}")
    print(f"📅 Date: {datetime.now().isoformat()}")
    print("-" * 40)
    print("📋 Copy this into your new AI Chat:\n")
    print(f"Goal: {title}")
    print(f"Context: {brief}")
    print("-" * 40)


def close_issue(summary, decisions):
    engine = BeadsEngine()
    details = f"Summary: {summary} | Decisions: {decisions}"
    engine.remember("ISSUE_CLOSE", details)

    print("\n🔒 ATOMIC CONTEXT CLOSED")
    print("-" * 40)
    print("✅ Logged to Memory Beads.")
    print("🗑️  Action: Archive/Delete your AI Chat now.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atomic Context Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Start Command
    start_parser = subparsers.add_parser("start", help="Start a new AI Issue")
    start_parser.add_argument("--title", required=True, help="Issue Title")
    start_parser.add_argument("--brief", required=True, help="Micro-Brief (Goal/Constraints)")

    # Close Command
    close_parser = subparsers.add_parser("close", help="Log & Close an Issue")
    close_parser.add_argument("--summary", required=True, help="1-sentence summary")
    close_parser.add_argument("--decisions", required=True, help="Key decisions made")

    args = parser.parse_args()

    if args.command == "start":
        start_issue(args.title, args.brief)
    elif args.command == "close":
        close_issue(args.summary, args.decisions)
    else:
        parser.print_help()
